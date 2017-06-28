import os
import socket

import logging
from django.core.management.base import BaseCommand

from yawn.worker.main import Main


class Command(BaseCommand):
    help = 'Run the worker to execute tasks'

    def add_arguments(self, parser):
        name_default = '{} {}'.format(socket.gethostname(), os.getpid())
        parser.add_argument('--concurrency', type=int, help='Number of concurrent tasks to run', default=1)
        parser.add_argument('--name', type=str, help='Worker name to register', default=name_default)
        parser.add_argument('--queues', type=str, nargs='+', default=['default'], metavar='QUEUE',
                            help='Space-separated list of queues to consume from')

    def handle(self, *args, **options):
        log_level = logging.INFO
        if options['verbosity'] == 0:
            log_level = logging.ERROR
        if options['verbosity'] > 1:
            log_level = logging.DEBUG
        logging.basicConfig(level=log_level, format='%(message)s')

        worker = Main(
            options['concurrency'],
            options['name'],
            options['queues'],
        )
        worker.run()
