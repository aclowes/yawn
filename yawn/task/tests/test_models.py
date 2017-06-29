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
from yawn.worker.models import Queue, Worker
from yawn.task.models import Task, Execution, Template


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

    execution.update_output(execution.id, 'foo', 'blah')
    execution.refresh_from_db()
    assert execution.stdout == 'foo'
    assert execution.stderr == 'blah'

    # only provide one, check it also works
    execution.update_output(execution.id, 'bar', None)
    execution.refresh_from_db()
    assert execution.stdout == 'foobar'
    assert execution.stderr == 'blah'


def test_task_without_workflow():
    template = Template.objects.create(name='task1', command='')
    task = Task.objects.create(template=template)
    worker = Worker.objects.create(name='worker1')

    # asserts that a task can be run without having a workflow associated
    execution = task.start_execution(worker)
    execution.mark_finished(exit_code=0)
    task.refresh_from_db()
    assert task.status == Task.SUCCEEDED
