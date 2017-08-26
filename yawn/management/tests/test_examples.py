from django.core import management

from yawn.workflow.models import Workflow


def test_examples():
    management.call_command('examples')
    assert Workflow.objects.count() == 3
