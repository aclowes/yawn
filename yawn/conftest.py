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
    verbosity = 1
    interactive = False  # whether to ask before deleting
    old_config = runner.setup_databases(verbosity, interactive)

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

    user = User.objects.create_user('test_user')
    client = APIClient()
    client.force_authenticate(user)
    return client
