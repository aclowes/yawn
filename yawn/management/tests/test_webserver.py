import sys

from unittest import mock

from django.core import management

from yawn.management.commands import webserver


@mock.patch.object(webserver.WSGIApplication, 'run')
def test_webserver(mock_run):
    # pytest with coverage arguments causes gunicorn's argparse to fail
    with mock.patch.object(sys, 'argv', ['yawn', 'worker', '-b', '0.0.0.0:8000']):
        management.call_command('webserver')
        assert mock_run.call_count == 1
