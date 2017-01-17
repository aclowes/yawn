from yawn.worker.models import Queue
from yawn.worker.main import Main


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
