import os

import pytest
import yaml


@pytest.fixture()
def data():
    filename = os.path.join(os.path.dirname(__file__), 'workflow.yaml')
    return yaml.load(open(filename).read())


def test_create_workflow(client, data):
    response = client.post('/api/workflows/', data)
    assert response.status_code == 201
    assert response.data['name'] == data['name']
    assert response.data['next_run'] is None
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
    assert response.status_code == 201
    assert response.data['version'] == 1

    # no change, same version returned
    response = client.post('/api/workflows/', data)
    # assert response.status_code == 302
    assert response.data['version'] == 1

    # any change, new version created
    data['tasks'][0]['max_retries'] = 2
    response = client.post('/api/workflows/', data)
    assert response.status_code == 201
    assert response.data['version'] == 2


def test_invalid_fields(client, data):
    data['name'] = 'not a slug'
    data['parameters'] = 'not a dict'
    data['tasks'][1]['upstream'].append('invalid_task')
    response = client.post('/api/workflows/', data)
    assert response.status_code == 400
    assert 'required pattern' in response.data['name'][0]
    assert 'must be a dictionary' in response.data['parameters'][0]
    assert 'upstream task(s) invalid_task' in response.data['tasks'][0]


def test_more_invalid_fields(client, data):
    data['parameters'] = {'invalid variable': 1}
    data['tasks'] = []
    response = client.post('/api/workflows/', data)
    assert response.status_code == 400
    assert 'Invalid parameter key' in response.data['parameters'][0]
    assert 'Invalid parameter value' in response.data['parameters'][1]
    assert 'non_field_errors' in response.data['tasks']

# test workflow already exists, no change
