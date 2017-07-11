import django
import pytest

from django.conf import settings
from django.db import transaction
from django.test import runner

import yawn.settings.test

# Setup at the module level because django settings need to be
# initialized before importing other django code.
# This file is only imported by pytest when running tests.
settings.configure(**yawn.settings.test.__dict__)
django.setup()


@pytest.fixture(scope='session')
def setup_django():
    """Provide a test database and django configuration"""
    from yawn.worker.models import Queue

    # these are positional arguments, written out for clarity
    verbosity = 1
    interactive = False  # whether to ask before deleting
    old_config = runner.setup_databases(verbosity, interactive)

    # create the default queue outside the transaction
    Queue.get_default_queue()

    yield

    for connection, old_name, destroy in old_config:
        connection.creation.destroy_test_db(old_name)


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
