import os
import sys
import subprocess

from unittest import mock

from django.conf import settings
from django.core import management

import yawn

from yawn.management.commands import webserver


@mock.patch.object(webserver.WSGIApplication, 'run')
def test_webserver(mock_run):
    # pytest with coverage arguments causes gunicorn's argparse to fail
    with mock.patch.object(sys, 'argv', ['worker']):
        management.call_command('webserver')
        assert mock_run.call_count == 1


def test_static_files():
    # make files to serve
    root = os.path.join(os.path.dirname(yawn.__file__), 'staticfiles/')
    os.makedirs(root, exist_ok=True)
    for filename in ('index.html', 'favicon.ico'):
        path = os.path.join(root, filename)
        subprocess.check_call(['touch', path])

    # setup whitenoise after the files exist
    app = webserver.get_wsgi_application()
    whitenoise = webserver.DefaultFileServer(app, settings)
    whitenoise.application = mock.Mock()

    # an API request
    whitenoise({'PATH_INFO': '/api/'}, None)
    assert whitenoise.application.call_count == 1

    # an unmatched file, goes to homepage
    start_response = mock.Mock()
    response = whitenoise({'PATH_INFO': '/', 'REQUEST_METHOD': 'GET'}, start_response)
    assert 'index.html' in response.filelike.name

    # a real static file
    response = whitenoise({'PATH_INFO': '/favicon.ico', 'REQUEST_METHOD': 'GET'}, start_response)
    assert 'favicon.ico' in response.filelike.name
