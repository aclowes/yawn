import pytest

from django.utils.dateparse import parse_datetime

from yawn.workflow.models import WorkflowName
from yawn.workflow.tests.utils import load_sample_workflow

data = pytest.fixture(load_sample_workflow)


def test_create_workflow(client, data):
    response = client.post('/api/workflows/', data)
    assert response.status_code == 201
    assert response.data['name'] == data['name']
    assert response.data['next_run'] is not None
    assert response.data['schedule'] == data['schedule']
    assert response.data['schedule_active'] == data['schedule_active']
    assert response.data['parameters'] == data['parameters']
    assert response.data['tasks'][0]['command'] == data['tasks'][0]['command']
    assert response.data['tasks'][0]['queue'] == 'default'
    assert response.data['tasks'][0]['timeout'] == data['tasks'][0]['timeout']
    assert response.data['tasks'][1]['upstream'] == data['tasks'][1]['upstream']
    assert response.data['tasks'][1]['max_retries'] == 0  # default
    assert response.data['tasks'][1]['timeout'] is None  # default


def test_create_workflow_versions(client, data):
    response = client.post('/api/workflows/', data)
    assert response.status_code == 201, response.data
    assert response.data['version'] == 1

    # no change, same version returned
    response = client.post('/api/workflows/', data)
    assert response.data['version'] == 1

    # any change, new version created
    data['tasks'][0]['max_retries'] = 2
    response = client.post('/api/workflows/', data)
    assert response.status_code == 201, response.data
    assert response.data['version'] == 2


def test_invalid_fields(client, data):
    data['name'] = ''
    data['parameters'] = 'not a dict'
    data['tasks'][1]['upstream'].append('invalid_task')
    response = client.post('/api/workflows/', data)
    assert response.status_code == 400, response.data
    assert 'This field may not be blank' in response.data['name'][0]
    assert 'must be a dictionary' in response.data['parameters'][0]
    assert 'upstream task(s) invalid_task' in response.data['tasks'][0]


def test_more_invalid_fields(client, data):
    data['parameters'] = {'invalid variable': 1}
    data['tasks'] = []
    response = client.post('/api/workflows/', data)
    assert response.status_code == 400, response.data
    assert 'Invalid parameter key' in response.data['parameters'][0]
    assert 'Invalid parameter value' in response.data['parameters'][1]
    assert 'non_field_errors' in response.data['tasks']


def test_list_workflow_names(client):
    name = WorkflowName.objects.create(name='workflow1')
    version1 = name.new_version()
    version2 = name.new_version()
    response = client.get('/api/names/')
    assert response.status_code == 200, response.data
    assert response.data['results'][0]['name'] == name.name
    response = client.get('/api/names/{}/'.format(name.id))
    assert response.status_code == 200, response.data
    assert response.data['current_version_id'] == version2.id
    assert response.data['current_version'] == version2.version
    assert response.data['task_count'] == 0
    assert response.data['versions'] == [version1.id, version2.id]


def test_get_run(client, run):
    url = '/api/runs/%s/' % run.id
    response = client.get(url)
    run.refresh_from_db()  # to get submitted_time which is from the DB
    assert response.status_code == 200, response.data
    assert response.data['status'] == run.status
    assert response.data['parameters'] == run.parameters
    assert response.data['scheduled_time'] == run.scheduled_time
    assert parse_datetime(response.data['submitted_time']) == run.submitted_time
    tasks = list(run.task_set.all())
    # we get all the tasks in the list view as they are used in the DetailHistory table
    assert response.data['tasks'][0]['status'] == tasks[0].status
    assert response.data['tasks'][1]['status'] == tasks[1].status


def test_post_run(client, run):
    """create a new run of the workflow"""
    url = '/api/runs/'
    workflow = run.workflow
    data = {'workflow_id': workflow.id, 'parameters': {'A': '1', 'B': 'false'}}
    response = client.post(url, data)
    assert response.status_code == 201, response.data
    assert response.data['id'] == run.id + 1
    assert response.data['status'] == run.RUNNING
    merged_parameters = workflow.parameters.copy()
    merged_parameters.update(data['parameters'])
    assert response.data['parameters'] == merged_parameters

    # without parameters
    data = {'workflow_id': workflow.id}
    response = client.post(url, data)
    assert response.status_code == 201, response.data
    assert response.data['id'] == run.id + 2
    assert response.data['status'] == run.RUNNING
    assert response.data['parameters'] == workflow.parameters


def test_patch_run(client, run):
    url = '/api/runs/%s/' % run.id
    update = {'parameters': {'A': '1', 'B': 'false'}}
    response = client.patch(url, update)
    run.refresh_from_db()
    assert response.status_code == 200, response.data
    assert response.data['parameters'] == update['parameters']
    assert response.data['parameters'] == run.parameters
