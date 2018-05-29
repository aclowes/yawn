import enum
import signal
import typing  # NOQA
import collections

import time
from django.db import transaction
from django.db.models import functions

from yawn.task.models import Task, Execution
from yawn.worker.models import Worker, Queue
from yawn.worker.executor import Manager, Result  # NOQA
from yawn.workflow.models import Workflow
from yawn.utilities import logger
from yawn.utilities.cron import Crontab
from yawn.utilities.database import close_on_exception


class State(enum.Enum):
    stopped = 'Stopped'
    running = 'Running'
    shutdown = 'Shutting down'
    terminate = 'Terminating'


class Main:
    results = None  # type: typing.Deque[Result]
    executor = None
    state = State.stopped
    worker = None
    timeout = 60  # seconds

    def __init__(self, concurrency, name, queues: list):
        self.concurrency = concurrency
        self.results = collections.deque()
        self.name = name
        self.queue_ids = []
        for name in queues:
            queue, created = Queue.objects.get_or_create(name=name)
            self.queue_ids.append(queue.id)

    def run(self):
        """
        Main event loop.

        Why not threads/gevent/asyncio?
            Because this is simple and maybe more efficient
        """
        self.handle_signals()
        self.executor = Manager()
        self.state = State.running
        loop_start = time.time()
        logger.warning('Starting YAWN worker with concurrency=%s', self.concurrency)

        while True:

            if self.state == State.running:

                # update own status and check for lost workers
                self.update_worker()

                # check for tasks that should be queued
                self.schedule_workflows()

                # run queued tasks
                self.start_tasks()

                self.mark_terminated()

            elif not self.executor.get_running_ids():
                # shutdown: exit loop once all tasks are finished
                break

            # check status on running tasks
            self.results.extend(self.executor.read_output())
            self.save_results()

            # don't run the loop more than once per second
            loop_duration = time.time() - loop_start
            time.sleep(max(1 - loop_duration, 0))
            loop_start += loop_duration

        logger.warning('Exiting')
        self.worker.status = Worker.EXITED
        self.worker.save()

    def handle_signals(self):
        """
        Handle signals:
        - SIGINT waits for running tasks to stop, then exits
        - SIGTERM kills running tasks, saves to the database, and exits
        """

        def handle_sigterm(*args):
            self.state = State.terminate
            # kill running tasks
            self.executor.mark_terminated(self.executor.get_running_ids())
            logger.warning('Received SIGTERM, killing running tasks and exiting.')

        def handle_sigint(*args):
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

            task = Task.first_queued(self.queue_ids)
            if not task:
                return  # there are no tasks ready to run

            execution = task.start_execution(self.worker)

        logger.info('Starting task %s execution %s', task.id, execution.id)
        self.executor.start_subprocess(
            execution_id=execution.id,
            command=execution.task.template.command,
            environment=execution.task.run.parameters if execution.task.run else {},
            timeout=execution.task.template.timeout
        )

    @close_on_exception
    def update_worker(self):
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
                if result.stdout or result.stderr:
                    Execution.update_output(result.execution_id, result.stdout, result.stderr)
                if result.returncode is not None:
                    execution = Execution.objects.get(id=result.execution_id)
                    logger.info('Task %s execution %s exited with code %s',
                                execution.task.id, execution.id, result.returncode)
                    execution.mark_finished(result.returncode)
                # pop after doing the updates have completed successfully
                # in the case of an exception before here, the updates will be retried
                self.results.popleft()

    @close_on_exception
    def mark_terminated(self):
        """Kill any tasks marked for termination by the user"""
        killed_execution_ids = Execution.objects.filter(
            id__in=self.executor.get_running_ids(),
            status=Execution.KILLED,
        ).values_list('id', flat=True)
        if killed_execution_ids:
            self.executor.mark_terminated(killed_execution_ids)
