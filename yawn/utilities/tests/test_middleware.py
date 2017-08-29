import os
from unittest import mock

from django.conf import settings


def test_static_files(client):
    root = os.path.join(settings.BASE_DIR, 'utilities/tests/static')
    with mock.patch.object(settings, 'WHITENOISE_ROOT', root):
        # an API request
        response = client.get('/api/')
        assert 'workflows' in response.data

        # an unmatched file, goes to homepage
        response = client.get('/something')
        assert next(response.streaming_content) == b'index\n'

        # a real static file
        response = client.get('/static.txt')
        assert next(response.streaming_content) == b'static\n'
