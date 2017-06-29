from gunicorn.app.base import Application
from django.core.management.base import BaseCommand
from django.core.wsgi import get_wsgi_application
from django.conf import settings
from whitenoise.django import DjangoWhiteNoise
from whitenoise.utils import decode_path_info


class DefaultFileServer(DjangoWhiteNoise):
    def __call__(self, environ, start_response):
        """
        Serve index.html if not /api/ or a static file

        This allows users to navigate directly to a URL like http://127.0.0.1:8000/workflows/2
        and we return index.html, and then react-router interprets the path.
        """
        path = decode_path_info(environ['PATH_INFO'])
        if path.startswith('/api'):
            return self.application(environ, start_response)
        static_file = self.files.get(path)
        if static_file is None:
            # serve the homepage on non-existent file
            static_file = self.files.get('/index.html')
        return self.serve(static_file, environ, start_response)


class WSGIApplication(Application):
    def init(self, parser, opts, args):
        name = "yawn webserver"
        self.cfg.set("default_proc_name", name)

    def load(self):
        app = get_wsgi_application()
        whitenoise = DefaultFileServer(app, settings)
        return whitenoise


class Command(BaseCommand):
    help = 'Run the webserver. Accepts gunicorn args'

    def handle(self, *args, **options):
        print('  Invoking YAWN webserver')
        app = WSGIApplication()
        app.run()
