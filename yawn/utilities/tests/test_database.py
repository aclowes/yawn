import datetime

import pytest
from django.db import connection

from yawn.utilities import database
from yawn.utilities.database import close_on_exception


@pytest.mark.no_transaction
def test_close_on_exception():

    @close_on_exception
    def example_disconnect():
        with connection.cursor() as cursor:

            # kill the current connection, which will raise a django.db.OperationalError
            cursor.execute('select pg_terminate_backend(pg_backend_pid())')

            # which means we never get here
            cursor.execute('select 1')
            assert False, 'exception was not raised'

    # this will cause a disconnect:
    example_disconnect()

    # but the exception is caught, and on retry the database reconnects:
    with connection.cursor() as cursor:
        cursor.execute('select 1')


def test_current_time():
    assert isinstance(database.current_time(), datetime.datetime)
