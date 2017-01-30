import pytest

from yawn.task.models import Template
from yawn.worker.models import Worker, Queue, Message
from yawn.workflow.models import WorkflowName


def test_get_workers(client):
    worker = Worker.objects.create(name='worker1')
    response = client.get('/api/workers/')
    assert response.status_code == 200
    workers = response.data['results']
    assert len(workers) == 1
    assert workers[0]['name'] == worker.name
    assert workers[0]['status'] == worker.status


@pytest.fixture()
def queue():
    queue = Queue.objects.create(name='queue1')

    # need all this for a task...
    name = WorkflowName.objects.create(name='workflow1')
    workflow = name.new_version()
    Template.objects.create(workflow=workflow, name='task1', command=[''])
    run = workflow.submit_run()
    task = run.task_set.first()

    # create some messages
    Message.objects.create(task=task, queue=queue)
    Message.objects.create(task=task, queue=queue)
    Message.objects.create(task=task, queue=Queue.get_default_queue())
    return queue


def test_get_queues(client, queue):
    response = client.get('/api/queues/')
    assert response.status_code == 200
    queues = response.data['results']
    assert len(queues) == 2
    assert queues[1]['name'] == queue.name
    assert queues[1]['message_count'] == 2
