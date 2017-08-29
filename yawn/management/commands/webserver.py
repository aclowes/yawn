import shlex

from gunicorn.app.base import BaseApplication
from django.core.management.base import BaseCommand
from django.core.wsgi import get_wsgi_application


class WSGIApplication(BaseApplication):
    """A Gunicorn Application, with logic to parse config passed from the command"""

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
        return get_wsgi_application()


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
