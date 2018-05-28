import functools

from django import db
from django.db import OperationalError

from yawn.utilities import logger


def close_on_exception(func):
    """
    A wrapper to close the database connection if a DB error occurs,
    so that it will get re-opened on the next use.

    Squashes the exception and logs it.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except OperationalError as exc:
            logger.error('Database error, closing connection', exc_info=True)
            db.connection.close()
            assert db.connection.closed_in_transaction is False, \
                'Could not close connection, probably because this wrapper ' \
                'was used inside an transaction.atomic() block.'

    return wrapper


def current_time():
    """Return the database time"""
    with db.connection.cursor() as cursor:
        cursor.execute("SELECT STATEMENT_TIMESTAMP()")
        row = cursor.fetchone()
    return row[0]
