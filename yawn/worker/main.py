import os
import enum
import signal
import socket
import logging
import collections

from django.db import models
from django.db import transaction
from django.db.models import functions

from yawn.task.models import Template, Task, Execution
from yawn.worker.models import Worker, Queue
from yawn.worker.executor import Manager, Result
from yawn.workflow.models import WorkflowName, Workflow, Run
from yawn.utilities import logger
from yawn.utilities.cron import Crontab
from yawn.utilities.database import close_on_exception


class State(enum.Enum):
    stopped = 'Stopped'
    running = 'Running'
    shutdown = 'Shutting down'
    terminate = 'Terminating'


class Main:
    results = None  # type: typing.List[Result]
    executor = None
    state = State.stopped
    worker = None
    timeout = 60  # seconds

    def __init__(self, concurrency, name=None, queues: list = None):
        self.concurrency = concurrency
        self.results = collections.deque()
        self.name = name or '{} {}'.format(socket.gethostname(), os.getpid())
        if queues:
            self.queue_ids = []
            for name in queues:
                queue, created = Queue.objects.get_or_create(name=name)
                self.queue_ids.append(queue.id)
        else:
            self.queue_ids = [1]

    def run(self):
        """
        Main event loop.

        Why not threads/gevent/asyncio?
            Because this is simple and maybe even more efficient!
        """
        self.handle_signals()
        self.executor = executor.Manager()
        self.state = State.running
        logger.warning('Starting YAWN worker with concurrency=%s', self.concurrency)

        while True:
            if self.state == State.running:

                # check for tasks that should be queued
                self.schedule_workflows()

                # run queued tasks
                self.start_tasks()

                self.mark_terminated()

                # update own status and check for lost workers
                self.check_stranded()

            elif not self.executor.get_running_ids():
                # shudown: exit loop once all tasks are finished
                break

            # check status on running tasks
            self.results.extend(self.executor.read_output())
            self.save_results()

        logger.warning('Exiting')
        self.worker.status = Worker.EXITED
        self.worker.save()

    def handle_signals(self):
        """
        Handle signals:
        - SIGINT waits for running tasks to stop, then exits
        - SIGTERM kills running tasks, saves to the database, and exits
        """

        def handle_sigterm():
            self.state = State.terminate
            # kill running tasks
            self.executor.mark_terminated(self.executor.get_running_ids())
            logger.warning('Received SIGTERM, killing running tasks and exiting.')

        def handle_sigint():
            self.state = State.shutdown
            logger.warning('Received SIGINT, shutting down after all tasks have finished.')
            logger.warning('Press CTL-C again to shut down immediately.')
            signal.signal(signal.SIGINT, handle_sigterm)

        signal.signal(signal.SIGINT, handle_sigint)
        signal.signal(signal.SIGTERM, handle_sigterm)

    @close_on_exception
    def schedule_workflows(self):
        """
        Check for workflow templates with a crontab that are ready to run.
        - Query and lock the ready template.
        - Create a run and associated tasks from the template.
        - Update the template's next_run attribute.
        """
        with transaction.atomic():
            workflow = Workflow.first_ready()
            if not workflow:
                return  # there is no workflow ready to run

            run = workflow.submit_run(scheduled_time=workflow.next_run)
            workflow.next_run = Crontab(workflow.schedule).next_run(run.submitted_time)
            workflow.save()

    @close_on_exception
    def start_tasks(self):
        """
        Check for queued tasks that we can run here and start them.
        """
        if len(self.executor.get_running_ids()) >= self.concurrency:
            return  # this worker is already running enough tasks

        with transaction.atomic():

            task = workflows.Task.first_queued(self.queue_ids)
            if not task:
                return  # there are no tasks ready to run

            execution = task.start_execution(execution_host=self.name)

        self.executor.start_subprocess(
            execution_id=execution.id,
            command=execution.task.template.command,
            environment=execution.task.run.parameters,
            timeout=execution.task.template.timeout
        )

    @close_on_exception
    def check_stranded(self):
        """
        Look for executors where the connection has broken and tasks need to be re-submitted.
        """
        if not self.worker:
            self.worker = Worker.objects.create(
                name=self.name,
                start_timestamp=functions.Now(),
                last_heartbeat=functions.Now()
            )
        else:
            self.worker.refresh_from_db()

        if self.worker.status == Worker.LOST:
            # someone else marked us as lost, terminate all tasks and exit
            logger.warning('Marked as lost, committing harakiri')
            self.state = State.terminate
            self.executor.mark_terminated(self.executor.get_running_ids())
            return

        # update our timestamp so no one marks us as lost
        self.worker.last_heartbeat = functions.Now()
        self.worker.save()

        # look for lost workers and re-queue their tasks
        Worker.find_lost(self.timeout)

    @close_on_exception
    def save_results(self):
        """Persist the subprocess results to the database"""
        for _ in range(len(self.results)):
            with transaction.atomic():
                result = self.results[0]
                execution = Execution.objects.get(id=result.execution_id)
                execution.update(
                    exit_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr
                )
                # pop after doing the update so it will retry if the db was disconnected
                self.results.popleft()

    @close_on_exception
    def mark_terminated(self):
        """Kill any tasks marked for termination by the user"""
        killed_execution_ids = workflows.Execution.objects.filter(
            id__in=self.executor.get_running_ids(),
            status=workflows.Execution.KILLED,
        ).values_list('id', flat=True)
        if killed_execution_ids:
            self.executor.mark_terminated(killed_execution_ids)
