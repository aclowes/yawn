from django.db import models
from django.contrib.postgres import fields
from django.db.models import functions

from yawn.utilities import cron, database
from yawn.utilities.cron import Crontab


class WorkflowName(models.Model):
    name = models.TextField(unique=True)
    current_version = models.OneToOneField('Workflow', on_delete=models.CASCADE,
                                           null=True, related_name='is_current')

    def new_version(self, **kwargs):
        """Create a new version of a workflow"""
        version = 0
        if self.current_version_id:
            version = self.current_version.version

            # disable the past schedule
            self.current_version.schedule_active = False
            self.current_version.save()

        workflow = Workflow.objects.create(name=self, version=version + 1, **kwargs)
        self.current_version = workflow
        self.save()
        return workflow


class Workflow(models.Model):
    class Meta:
        unique_together = (('name', 'version'),)

    name = models.ForeignKey(WorkflowName, models.PROTECT)
    version = models.IntegerField(editable=False)  # serializer read-only

    # scheduling is completely optional:
    schedule_active = models.BooleanField(default=False)
    schedule = models.TextField(null=True, validators=[cron.cron_validator])
    next_run = models.DateTimeField(null=True)

    # parameters
    parameters = fields.JSONField(default=dict)

    def save(self, **kwargs):
        if self.schedule_active:
            if not self.next_run:
                self.next_run = Crontab(self.schedule).next_run(database.current_time())
        else:
            self.next_run = None
        super().save(**kwargs)

    @classmethod
    def first_ready(cls):
        ready_templates = list(cls.objects.raw("""
            SELECT * FROM yawn_workflow
            WHERE schedule_active
            AND next_run < transaction_timestamp()
            ORDER BY next_run LIMIT 1
            FOR UPDATE SKIP LOCKED -- requires PG 9.5+
        """))
        return ready_templates[0] if len(ready_templates) else None

    def submit_run(self, parameters=None, scheduled_time=None):
        """Create a run of this template"""
        from yawn.task.models import Task

        run_parameters = self.parameters.copy()
        run_parameters.update(parameters or {})

        run = Run.objects.create(
            workflow=self,
            submitted_time=functions.Now(),
            scheduled_time=scheduled_time,
            parameters=run_parameters,
        )
        for template in self.template_set.all():
            task = Task.objects.create(
                run=run,
                template=template,
            )
            if not template.upstream.exists():
                task.enqueue()

        # refresh to get the actual DB submitted time
        run.refresh_from_db()
        return run

    def __str__(self):
        return '{} v{}'.format(self.name.name, self.version)


class Run(models.Model):
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    STATUS_CHOICES = [(x, x) for x in (RUNNING, SUCCEEDED, FAILED)]

    workflow = models.ForeignKey(Workflow, models.PROTECT)
    submitted_time = models.DateTimeField()
    scheduled_time = models.DateTimeField(null=True)
    status = models.TextField(default=RUNNING, choices=STATUS_CHOICES)
    parameters = fields.JSONField(default=dict)

    def update_status(self):
        from yawn.task.models import Task

        task_statuses = self.task_set.all().values_list('status', flat=True)

        if all([status == Task.SUCCEEDED for status in task_statuses]):
            self.status = self.SUCCEEDED
        elif any([status in [Task.WAITING, Task.QUEUED, Task.RUNNING] for status in task_statuses]):
            self.status = self.RUNNING
        else:
            self.status = self.FAILED

        self.save()

    def __str__(self):
        return 'Workflow {} Run {}'.format(self.workflow_id, self.id)
