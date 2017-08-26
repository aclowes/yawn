import os
import subprocess

from unittest import mock

from django.conf import settings
from django.core import management

import yawn

from yawn.management.commands import webserver


@mock.patch.object(webserver.WSGIApplication, 'run')
def test_webserver(mock_run):
    mock.patch('argparse._sys.argv', ['worker'])
    management.call_command('webserver')
    assert mock_run.call_count == 1


def test_static_files():
    app = webserver.get_wsgi_application()
    whitenoise = webserver.DefaultFileServer(app, settings)
    whitenoise.application = mock.Mock()

    # make files to serve
    for filename in ('index.html', 'favicon.ico'):
        path = os.path.join(os.path.dirname(yawn.__file__), 'staticfiles', filename)
        subprocess.check_call(['touch', path])

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
