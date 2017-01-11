from django.utils.dateparse import parse_datetime

# to make the fixture available:
from yawn.task.tests.test_models import run
from yawn.worker.models import Worker


def test_get_run(client, run):
    url = '/api/runs/%s/' % run.id
    response = client.get(url)
    run.refresh_from_db()  # to get submitted_time which is from the DB
    assert response.status_code == 200
    assert response.data['status'] == run.status
    assert response.data['parameters'] == run.parameters
    assert response.data['scheduled_time'] == run.scheduled_time
    assert parse_datetime(response.data['submitted_time']) == run.submitted_time
    tasks = list(run.task_set.all())
    assert response.data['tasks'][0]['status'] == tasks[0].status
    assert response.data['tasks'][1]['status'] == tasks[1].status


def test_get_task(client, run):
    task = run.task_set.first()
    worker = Worker.objects.create(name='worker1')
    task.start_execution(worker)
    url = '/api/tasks/%s/' % task.id
    response = client.get(url)
    assert response.status_code == 200
    assert response.data['name'] == task.template.name
    assert response.data['status'] == task.status
    assert response.data['executions'][0]['worker']['name'] == worker.name
    assert response.data['messages'][0]['queue'] == task.message_set.first().queue.name
