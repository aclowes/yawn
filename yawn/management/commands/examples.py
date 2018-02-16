import random

from django.core.management.base import BaseCommand

from yawn.task.models import Template
from yawn.workflow.models import WorkflowName
from yawn.workflow.serializers import WorkflowSerializer
from yawn.workflow.tests.utils import load_sample_workflow


class Command(BaseCommand):
    help = 'Load sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample workflows!')

        self.stdout.write('First, a simple four task workflow...')
        name, _ = WorkflowName.objects.get_or_create(name='Simple Workflow Example')
        workflow = name.new_version(parameters={'MY_OBJECT_ID': '1', 'SOME_SETTING': 'false'})
        task1 = Template.objects.create(workflow=workflow, name='start', command='echo Starting...')
        task2 = Template.objects.create(workflow=workflow, name='task2', command='echo Working on $MY_OBJECT_ID')
        task2.upstream.add(task1)
        task3 = Template.objects.create(workflow=workflow, name='task3',
                                        command='yawn exec yawn.management.tests.test_exec '
                                                'ExampleClass "thing to log"')
        task3.upstream.add(task1)
        task4 = Template.objects.create(workflow=workflow, name='done', command='echo Finished!')
        task4.upstream.add(task2, task3)

        workflow.submit_run(parameters={'child': 'true'})
        workflow.submit_run(parameters={'child': 'true'})
        workflow.submit_run(parameters={'child': 'true'})

        self.stdout.write('Second, a big beast workflow...')

        name, _ = WorkflowName.objects.get_or_create(name='Big Ol\' Workflow Example')
        workflow = name.new_version()
        tasks = []
        for x in range(30):
            task = Template.objects.create(workflow=workflow, name='task%s' % x, command='echo stuff')
            if tasks:
                task.upstream.add(*random.sample(tasks, k=min(x, 5)))
            tasks.append(task)

        # Create from a dictionary:
        self.stdout.write('Third, an example using the serializer...')
        serializer = WorkflowSerializer(data=load_sample_workflow())
        serializer.is_valid(raise_exception=True)
        workflow = serializer.save()
        workflow.submit_run()
