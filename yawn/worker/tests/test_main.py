import datetime
from unittest import mock

from django.utils import timezone

from yawn.worker.models import Queue
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
