import pytest
from django.contrib.auth.models import User


@pytest.fixture()
def user():
    return User.objects.get(username='test_user')


def test_list_users(client, user):
    response = client.get('/api/users/')
    assert response.status_code == 200
    users = response.data['results']
    assert len(users) == 1
    assert users[0]['email'] == user.email
    assert users[0]['username'] == user.username


def test_get_me(client, user):
    response = client.get('/api/users/me/')
    assert response.status_code == 200
    assert response.data['email'] == user.email
    assert response.data['username'] == user.username


def test_update_token(client, user):
    response = client.patch('/api/users/%s/' % user.id, {'refresh_token': True, 'username': 'other'})
    assert response.status_code == 200, response.data
    assert response.data['api_token'] is not None
    assert response.data['api_token'] == user.auth_token.key
    assert response.data['username'] == 'other'


def test_login_success(client, user):
    user.set_password('abcd')
    user.save()
    response = client.patch('/api/users/login/', {'username': user.username, 'password': 'abcd'})
    assert response.status_code == 200, response.data


def test_login_failure(client, user):
    response = client.patch('/api/users/login/', {'username': user.username, 'password': 'abcd'})
    assert response.status_code == 401, response.data
