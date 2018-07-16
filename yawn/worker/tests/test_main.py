import datetime
import signal
from unittest import mock

from django.utils import timezone

from yawn.task.models import Template, Task  # noqa: used in typing
from yawn.worker.executor import Result
from yawn.worker.models import Queue, Worker
from yawn.worker.main import Main, State
from yawn.workflow.models import WorkflowName, Workflow


def test_init_default_queue():
    worker = Main(1, 'test name', ['default'])
    assert worker.name == 'test name'
    assert worker.concurrency == 1
    assert len(worker.queue_ids) == 1
    queue = Queue.objects.get(id=worker.queue_ids[0])
    assert queue.name == 'default'


def test_init_custom_queues():
    queues = ['queue1', 'queue2']
    worker1 = Main(1, 'name', queues)
    worker2 = Main(1, 'name', queues)
    assert len(worker1.queue_ids) == 2
    # check that they end up with the same queue IDs
    assert sorted(worker1.queue_ids) == sorted(worker2.queue_ids)
    queue_names = Queue.objects.filter(
        id__in=worker1.queue_ids).values_list('name', flat=True)
    assert sorted(queue_names) == queues


@mock.patch('yawn.worker.main.time.sleep')
def test_run(mock_time):
    # so the worker exits immediately
    worker = Main(1, 'test name', ['default'])

    def set_shutdown(_):
        # stop the worker after one run
        worker.state = State.shutdown

    mock_time.side_effect = set_shutdown
    worker.run()


def test_schedule_workflows():
    name = WorkflowName.objects.create(name='workflow1')
    next_run = timezone.now() - datetime.timedelta(hours=1)
    workflow = Workflow.objects.create(
        name=name, version=1, schedule_active=True, schedule='0 0 *', next_run=next_run)
    worker = Main(1, 'test name', ['default'])
    worker.schedule_workflows()
    workflow.refresh_from_db()
    assert workflow.next_run > next_run


def test_signals():
    try:
        worker = Main(1, 'test name', ['default'])
        worker.handle_signals()
        worker.executor = mock.Mock()

        handler = signal.getsignal(signal.SIGINT)
        handler()
        assert worker.state == State.shutdown

        handler = signal.getsignal(signal.SIGTERM)
        handler()
        assert worker.state == State.terminate
        assert worker.executor.mark_terminated.called

    finally:
        # restore the default handlers
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)


def test_set_lost():
    worker = Main(1, 'test name', ['default'])
    worker.update_worker()  # first time creates the row
    worker.worker.status = Worker.LOST
    worker.worker.save()

    worker.executor = mock.Mock()
    worker.update_worker()

    assert worker.state == State.terminate
    assert worker.executor.mark_terminated.called


def test_save_results():
    # lots of setup
    worker = Main(1, 'test name', ['default'])
    worker.update_worker()

    name = WorkflowName.objects.create(name='workflow1')
    workflow = name.new_version(parameters={'parent': True, 'child': False})
    Template.objects.create(workflow=workflow, name='task1', command=[''])
    run = workflow.submit_run(parameters={'child': True})
    task1 = run.task_set.first()  # type: Task
    execution = task1.start_execution(worker.worker)

    result = Result(execution_id=execution.id)
    result.stdout = 'test stdout'
    worker.results.append(result)

    # trigger a save
    worker.save_results()

    execution.refresh_from_db()
    assert execution.stdout == result.stdout
    assert not worker.results
