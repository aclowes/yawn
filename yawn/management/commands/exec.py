"""
This helper command will import any python callable on your python path and
call it with the supplied arguments.

Use `yawn.task.decorators.make_task` to
"""
import importlib

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Execute a python callable'

    def add_arguments(self, parser):
        parser.add_argument('module', help='The python module to import, i.e. animal.bird')
        parser.add_argument('callable', help='The python callable to invoke, i.e. Swallow')
        parser.add_argument('argument', nargs='*', help='Arguments to pass to the callable')

    def handle(self, *args, **options):
        self.stdout.write('Importing module %s' % options['module'])
        module_ = importlib.import_module(options['module'])

        arguments = ''
        if options['argument']:
            arguments = "'{}'".format("', '".join(options['argument']))

        self.stdout.write('Calling %s(%s)' % (options['callable'], arguments))
        getattr(module_, options['callable'])(*options['argument'])

        self.stdout.write('Execution complete')
