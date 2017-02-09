from yawn.task.models import Template, Task, Execution  # NOQA
from yawn.worker.models import Worker
from yawn.workflow.models import WorkflowName


def test_find_lost():
    name = WorkflowName.objects.create(name='workflow1')
    workflow = name.new_version(parameters={'parent': True, 'child': False})
    task1 = Template.objects.create(workflow=workflow, name='task1', command=[''])
    task2 = Template.objects.create(workflow=workflow, name='task2', command=[''])
    task2.upstream.add(task1)
    run = workflow.submit_run(parameters={'child': True})
    task1, task2 = run.task_set.all()  # type: Task
    worker = Worker.objects.create(name='worker1')
    execution = task1.start_execution(worker)

    worker.find_lost(-1)
    worker.refresh_from_db()
    execution.refresh_from_db()

    assert worker.status == Worker.LOST
    assert execution.status == Execution.LOST
