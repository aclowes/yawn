from datetime import timedelta

from django.db import models
from django.db.models import functions

from yawn.utilities import logger


class Worker(models.Model):
    """Information about current and past workers"""
    #
    # NOTE: consider instead taking an advisory lock for each worker,
    # and using it to check if a worker is still connected.
    # See `pg_try_advisory_lock` and `select * from pg_locks where locktype = 'advisory'`
    # That would give more immediate feedback, but its not clear we need to be faster.
    #
    ACTIVE = 'active'
    EXITED = 'exited'
    LOST = 'lost'
    STATUS_CHOICES = [(x, x) for x in (ACTIVE, EXITED, LOST)]

    name = models.TextField(blank=False)
    status = models.TextField(choices=STATUS_CHOICES, default=ACTIVE)
    start_timestamp = models.DateTimeField(default=functions.Now)
    last_heartbeat = models.DateTimeField(default=functions.Now)

    @staticmethod
    def find_lost(timeout):
        from yawn.task.models import Execution

        # Make a sparse index so looking up active workers is fast:
        # CREATE INDEX yawn_worker_active ON yawn_worker (status) WHERE status = 'active'
        lost = Worker.objects.filter(
            status=Worker.ACTIVE, last_heartbeat__lt=functions.Now() - timedelta(seconds=timeout)
        )
        for worker in lost:
            logger.warning('Marking %r as lost', worker)
            worker.status = Worker.LOST
            worker.save()

            executions = worker.execution_set.filter(status=Execution.RUNNING)

            for execution in executions:
                logger.warning('Marking %r as lost', execution)
                execution.mark_finished(lost=True)

    def __str__(self):
        return self.name


class Queue(models.Model):
    """Arbitrary tag defining where tasks run."""

    name = models.TextField(unique=True)

    _default = None

    def __str__(self):
        return self.name

    @classmethod
    def get_default_queue(cls):
        if not cls._default:
            cls._default = Queue.objects.get_or_create(name='default')[0]
        return cls._default


class Message(models.Model):
    """The order of tasks waiting to be processed, like messages on a queue"""

    # I hope we never get to 9 Quintillion (9,223,372,036,854,775,807) messages
    id = models.BigAutoField(primary_key=True)

    queue = models.ForeignKey(Queue, models.PROTECT)
    task = models.ForeignKey('Task', models.PROTECT)
