import shlex

from gunicorn.app.base import BaseApplication
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


class WSGIApplication(BaseApplication):
    def __init__(self, options):
        self.options = options
        super().__init__()

    def load_config(self):
        parser = self.cfg.parser()

        # by default, log access to stdout
        self.cfg.set('accesslog', '-')

        env_vars = self.cfg.get_cmd_args_from_env()
        if env_vars:
            env_args = parser.parse_args(env_vars)
            self._set_cfg(env_args)

        if self.options:
            cmd_args = parser.parse_args(shlex.split(self.options))
            self._set_cfg(cmd_args)

    def _set_cfg(self, args):
        """Given an argparse namespace, set cfg variables"""
        for k, v in vars(args).items():
            if v is None:
                continue
            if k == "args":
                continue
            self.cfg.set(k.lower(), v)

    def load(self):
        app = get_wsgi_application()
        whitenoise = DefaultFileServer(app, settings)
        return whitenoise


class Command(BaseCommand):
    help = 'Run the webserver.'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        """Adds the Gunicorn command line args to YAWN"""
        parser.add_argument('--gunicorn', type=str,
                            help='Arguments to pass to gunicorn. See `gunicorn -h` for documentation. '
                                 'Alternatively put them in the GUNICORN_CMD_ARGS env variable.')

    def handle(self, *args, **options):
        print('  Invoking gunicorn YAWN webserver')

        # Run Gunicorn
        gunicorn_args = options.get('gunicorn')
        app = WSGIApplication(gunicorn_args)
        app.run()
