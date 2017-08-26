from unittest import mock

from django.core import management

from yawn.management.commands import worker


@mock.patch.object(worker.Main, 'run')
def test_worker(mock_run):
    management.call_command('worker')
    assert mock_run.called
