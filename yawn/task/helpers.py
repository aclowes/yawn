import shlex

from yawn.task.models import Template, Task
from yawn.workflow.models import Workflow  # noqa - needed to load the foreign key!
from yawn.worker.models import Queue


def delay(func, *args, timeout=None, max_retries=0, queue=None):
    arguments = [shlex.quote(arg) for arg in args]
    command = 'yawn exec {0.__module__} {0.__name__} {1}'.format(
        func, ' '.join(arguments)).strip()
    task_name = '{0.__module__}.{0.__name__}({1})'.format(
        func, ', '.join(arguments))

    if queue:
        queue_obj, _ = Queue.objects.get_or_create(name=queue)
    else:
        queue_obj = Queue.get_default_queue()

    template, _ = Template.objects.get_or_create(
        name=task_name,
        command=command,
        queue=queue_obj,
        max_retries=max_retries,
        timeout=timeout
    )
    task = Task.objects.create(
        template=template
    )
    task.enqueue()
    return task
