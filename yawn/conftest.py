import os

import django
import pytest

from django.db import transaction
from django.test import runner

# Setup at the module level because django settings need to be
# initialized before importing other django code.
# This file is only imported by pytest when running tests.
os.environ['DJANGO_SETTINGS_MODULE'] = 'yawn.settings.test'
django.setup()


@pytest.fixture(scope='session')
def setup_django():
    """Provide a test database and django configuration"""
    from yawn.worker.models import Queue

    manager = runner.DiscoverRunner(verbosity=1, interactive=False)
    old_config = manager.setup_databases()

    # create the default queue outside the transaction
    Queue.get_default_queue()

    yield

    manager.teardown_databases(old_config)


class TestPassedRollback(Exception):
    """Signal to rollback after a test passes"""


@pytest.fixture(autouse=True)
def test_transaction(setup_django, request):
    if 'no_transaction' in request.keywords:
        # the database reconnect test cannot work inside a transaction
        # so provide a way to disable transactions.
        yield
    else:
        try:
            with transaction.atomic():
                yield
                raise TestPassedRollback()
        except TestPassedRollback:
            pass


@pytest.fixture()
def client():
    from django.contrib.auth.models import User
    from rest_framework.test import APIClient

    user = User.objects.create_user('test_user', is_staff=True)
    api_client = APIClient()
    api_client.force_authenticate(user)
    return api_client


@pytest.fixture()
def run():
    """Setup a workflow and run to test with"""
    from yawn.workflow.models import WorkflowName
    from yawn.task.models import Template

    name = WorkflowName.objects.create(name='workflow1')
    workflow = name.new_version(parameters={'parent': True, 'child': False})
    task1 = Template.objects.create(workflow=workflow, name='task1', command='')
    task2 = Template.objects.create(workflow=workflow, name='task2', command='')
    task2.upstream.add(task1)

    return workflow.submit_run(parameters={'child': True})
