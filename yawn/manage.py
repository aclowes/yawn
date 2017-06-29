#!/usr/bin/env python
import os
import sys

from django.conf import settings
from django.core.management import execute_from_command_line


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yawn.settings.debug")

    # check if yawn is in installed apps, and bail if it is not
    if 'yawn' not in settings.INSTALLED_APPS:
        print("Please check your DJANGO_SETTINGS_MODULE environment variable.\n"
              "Make sure 'yawn' is in your INSTALLED_APPS.\n"
              "Generally, your settings file should start with 'from yawn.settings.base import *'")
        sys.exit(1)

    print('YAWN workflow management tool')
    if os.environ['DJANGO_SETTINGS_MODULE'] == 'yawn.settings.debug':
        print('  Running in DEBUG mode')

    # run the django manage.py command line
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
