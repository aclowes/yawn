from django.db import models
from django.db import transaction
from django.db.models import functions

from yawn.worker.models import Worker, Queue, Message
from yawn.utilities import logger


class Template(models.Model):
    workflow = models.ForeignKey('Workflow', models.PROTECT, editable=False, null=True)
    queue = models.ForeignKey(Queue, models.PROTECT)
    name = models.TextField()

    command = models.TextField()
    max_retries = models.IntegerField(default=0)
    timeout = models.IntegerField(null=True)  # seconds

    # self-reference for upstream tasks
    upstream = models.ManyToManyField(
        'Template', related_name='downstream', symmetrical=False, blank=True)

    class Meta:
        unique_together = ('workflow', 'name')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # can't set the default above because the value isn't serializable for migrations
        if not self.queue_id:
            self.queue = Queue.get_default_queue()
        super().save(*args, **kwargs)


class Task(models.Model):
    WAITING = 'waiting'
    QUEUED = 'queued'
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    UPSTREAM_FAILED = 'upstream_failed'
    STATUS_CHOICES = [(x, x) for x in (WAITING, QUEUED, RUNNING, SUCCEEDED, FAILED, UPSTREAM_FAILED)]

    run = models.ForeignKey('Run', models.PROTECT, null=True)
    template = models.ForeignKey(Template, models.PROTECT)
    status = models.TextField(choices=STATUS_CHOICES, default=WAITING)

    def __str__(self):
        return '#{task.id} ({task.status})'.format(task=self)

    @classmethod
    def first_queued(cls, queue_ids: list):
        """Get the first task for the given queue names, or None"""
        messages = list(Message.objects.raw(
            # this means retried tasks will go to the top of the queue
            """SELECT * FROM yawn_message WHERE queue_id IN %s
            ORDER BY id LIMIT 1 FOR UPDATE SKIP LOCKED""",
            # psycopg2 handles tuple & list params differently, check the docs:
            params=(tuple(queue_ids),)
        ))
        if not messages:
            return None
        messages[0].delete()
        return messages[0].task

    def enqueue(self):
        """Update the task's status and put a message on the queue"""
        self.status = Task.QUEUED
        self.save()
        Message.objects.create(
            task=self,
            queue=self.template.queue
        )

    def start_execution(self, worker) -> 'Execution':
        self.status = self.RUNNING
        self.save(update_fields=['status'])
        execution = Execution.objects.create(
            task=self,
            worker=worker
        )
        return execution

    def update_downstream(self):
        """
        Enqueue downstream tasks that can run since this one has completed.

        If this runs in a separate transaction from saving the task status,
        then we cannot miss a task because of concurrency.
        """
        downstream = Task.objects.filter(
            run=self.run,
            template__upstream=self.template,
            status__in=[Task.WAITING, Task.UPSTREAM_FAILED]
        ).select_for_update()

        for task in downstream:
            if self.status == Task.SUCCEEDED:
                waiting_for = Task.objects.filter(
                    run=self.run,
                    template__downstream=task.template_id
                ).exclude(status=Task.SUCCEEDED).exists()
                if not waiting_for:
                    logger.info('Submitting %s because all dependencies are complete', task)
                    task.enqueue()

            elif task.status == Task.WAITING:
                # my status is failed or upstream_failed, fail anything waiting downstream
                logger.info('Setting status of %s to upstream_failed', task)
                task.status = Task.UPSTREAM_FAILED
                task.save()
                task.update_downstream()


class Execution(models.Model):
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    KILLED = 'killed'
    LOST = 'lost'
    STATUS_CHOICES = [(x, x) for x in (RUNNING, SUCCEEDED, FAILED, KILLED, LOST)]

    task = models.ForeignKey(Task, models.PROTECT)
    worker = models.ForeignKey(Worker, models.PROTECT)
    status = models.TextField(default=RUNNING, choices=STATUS_CHOICES)

    start_timestamp = models.DateTimeField(default=functions.Now)
    stop_timestamp = models.DateTimeField(null=True)

    exit_code = models.IntegerField(null=True)
    stdout = models.TextField(default='', blank=True)
    stderr = models.TextField(default='', blank=True)

    def __str__(self):
        return '#{exec.id} ({exec.status})'.format(exec=self)

    @classmethod
    def update_output(cls, execution_id, stdout, stderr):
        """
        Append to stdout & stderr.
        Use concatenation to efficiently update the fields.
        """
        query = Execution.objects.filter(id=execution_id)
        query.update(
            stdout=functions.Concat('stdout', models.Value(stdout or '')),
            stderr=functions.Concat('stderr', models.Value(stderr or ''))
        )

    def mark_finished(self, exit_code=None, lost=False):
        """
        Update the execution status after it has finished:
         successfully, in error, or because it was lost.

        Also update the task and workflow; re-queue the task if
         it should be retried.
        """
        if lost:
            self.status = Execution.LOST
            self.task.enqueue()

        elif exit_code == 0:
            self.task.status = Task.SUCCEEDED
            self.status = Execution.SUCCEEDED

        else:
            # queue another run if there are remaining retries
            # (current execution is not in count b/c it hasn't been saved yet)
            failed_count = self.task.execution_set.filter(status=Task.FAILED).count()
            if failed_count < self.task.template.max_retries:
                self.task.enqueue()
            else:
                self.task.status = Task.FAILED

            self.status = Execution.FAILED

        if self.task.status != Task.RUNNING:
            self.task.save()
            with transaction.atomic():
                self.task.update_downstream()
            if self.task.run:
                self.task.run.update_status()

        self.stop_timestamp = functions.Now()
        self.exit_code = exit_code
        # need to be careful not to overwrite stdout/stderr
        self.save(update_fields=['status', 'stop_timestamp', 'exit_code'])
