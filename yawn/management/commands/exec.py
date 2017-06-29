import argparse
import importlib

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Execute a python callable'

    def add_arguments(self, parser):
        parser.add_argument('module')
        parser.add_argument('callable')
        parser.add_argument('arguments', nargs=argparse.REMAINDER)

    def handle(self, *args, **options):
        self.stdout.write('Importing module %s' % options['module'])
        module_ = importlib.import_module(options['module'])

        self.stdout.write('Calling %s("%s")' % (options['callable'], '", "'.join(options['arguments'])))
        getattr(module_, options['callable'])(*options['arguments'])

        self.stdout.write('Execution complete')
