import io
import logging

import pytest
from django.core import management

LOG1 = 'In example_function'
LOG2 = 'In ExampleClass'


def example_function():
    logging.info(LOG1)


class ExampleClass:
    def __init__(self, argument):
        logging.basicConfig()
        logging.warning(argument)


def test_call_function(caplog):
    caplog.set_level(logging.INFO)
    stdout = io.StringIO()
    management.call_command('exec', 'yawn.management.tests.test_exec', 'example_function', stdout=stdout)
    assert 'Execution complete' in stdout.getvalue()
    assert caplog.records[0].message == LOG1


def test_call_class(caplog):
    stdout = io.StringIO()
    management.call_command('exec', 'yawn.management.tests.test_exec', 'ExampleClass', LOG2, stdout=stdout)
    assert 'Execution complete' in stdout.getvalue()
    assert caplog.records[0].message == LOG2


def test_invalid_module():
    stdout = io.StringIO()
    with pytest.raises(ImportError):
        management.call_command('exec', 'yawn.no_such_module', 'ExampleClass', stdout=stdout)
