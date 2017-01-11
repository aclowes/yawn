"""
Test workflow logic
A
 \
  C - D
 /
B

Tasks:
A succeeded, do nothing to C(waiting)
A & B succeed, submit C(waiting)
A & B succeed, submit C(upstream_failed)
A & B succeed, don't submit C(failed)
A succeeded but B failed, mark C and D upstream_failed
"""
import pytest

from yawn.worker.models import Queue, Worker
from yawn.task.models import Template, Task, Execution
from yawn.workflow.models import WorkflowName


@pytest.fixture()
def run():
    """Setup a workflow and run to test with"""
    name = WorkflowName.objects.create(name='workflow1')
    workflow = name.new_version(parameters={'parent': True, 'child': False})
    task1 = Template.objects.create(workflow=workflow, name='task1', command=[''])
    task2 = Template.objects.create(workflow=workflow, name='task2', command=[''])
    task2.upstream.add(task1)

    run = workflow.submit_run(parameters={'child': True})
    return run


def test_first_queued(run):
    task1, task2 = run.task_set.all()
    task2.enqueue()
    queue = Queue.objects.get(name='default')
    first = Task.first_queued([queue.id])
    assert first.id == task1.id
    first = Task.first_queued([queue.id])
    assert first.id == task2.id
    first = Task.first_queued([queue.id])
    assert first is None


def test_first_queued_by_queue(run):
    task1, task2 = run.task_set.all()
    default_queue = Queue.objects.get(name='default')
    other_queue = Queue.objects.create(name='test')
    task2.template.queue = other_queue
    task2.enqueue()
    first = Task.first_queued([default_queue.id])
    assert first.id == task1.id
    first = Task.first_queued([default_queue.id])
    assert first is None
    first = Task.first_queued([other_queue.id])
    assert first.id == task2.id


def test_start_execution(run):
    task1, task2 = run.task_set.all()
    worker = Worker.objects.create(name='worker1')
    execution = task1.start_execution(worker)
    assert execution.status == Execution.RUNNING
    assert task1.status == Task.RUNNING


def test_execution_exitcode(run):
    task1, task2 = run.task_set.all()
    worker = Worker.objects.create(name='worker1')
    execution = task1.start_execution(worker)

    execution.mark_finished(exit_code=0)
    task2.refresh_from_db()
    assert execution.status == Execution.SUCCEEDED
    assert task1.status == Task.SUCCEEDED
    assert task2.status == Task.QUEUED

    task2.status = Task.WAITING
    task2.save()

    execution.mark_finished(exit_code=1)
    task2.refresh_from_db()
    assert execution.status == Execution.FAILED
    assert task1.status == Task.FAILED
    assert task2.status == Task.UPSTREAM_FAILED

    execution.mark_finished(lost=True)
    assert execution.status == Execution.LOST
    assert task1.status == Task.QUEUED


def test_execution_output(run):
    task1, task2 = run.task_set.all()
    worker = Worker.objects.create(name='worker1')
    execution = task1.start_execution(worker)

    execution.update_output(stdout='foo', stderr='blah')
    execution.refresh_from_db()
    assert execution.stdout == 'foo'
    assert execution.stderr == 'blah'

    execution.update_output(stdout='bar')
    execution.refresh_from_db()
    assert execution.stdout == 'foobar'
    assert execution.stderr == 'blah'
