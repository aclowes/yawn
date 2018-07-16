"""
Workflows:
A, B, C succeed, D is waiting -> Running
A, B, C succeed, D is running -> Running
A, B, C failed, D is queued -> Running
A, B, C, D succeed -> Succeeded
A, B failed, C, D upstream_failed -> Failed
"""
import datetime
from unittest import mock

import pytz
from django.utils import timezone

from yawn.task.models import Template, Task
from yawn.workflow.models import Workflow, WorkflowName, Run


def test_first_ready():
    name = WorkflowName.objects.create(name='workflow1')

    # not active, shouldn't get selected
    Workflow.objects.create(
        name=name, version=1, schedule_active=False,
        next_run=timezone.now() - datetime.timedelta(hours=1)
    )
    # future run date
    Workflow.objects.create(
        name=name, version=2, schedule_active=True,
        next_run=timezone.now() + datetime.timedelta(hours=1)
    )
    ready_workflow = Workflow.objects.create(
        name=name, version=3, schedule_active=True,
        next_run=timezone.now() - datetime.timedelta(seconds=1)
    )

    workflow = Workflow.first_ready()
    assert workflow.id == ready_workflow.id


@mock.patch('yawn.workflow.models.Crontab')
def test_next_run(mock_cron):
    next_run = timezone.datetime(2011, 1, 1, tzinfo=pytz.UTC)
    mock_cron().next_run.return_value = next_run

    name = WorkflowName.objects.create(name='workflow1')
    workflow = Workflow.objects.create(
        name=name, version=2, schedule_active=True,
        schedule='*'
    )
    assert workflow.next_run == next_run


def test_new_version():
    name = WorkflowName.objects.create(name='workflow1')
    workflow_1 = name.new_version(schedule='0 0 *', schedule_active=True)
    assert workflow_1.next_run
    assert workflow_1.version == 1
    workflow_2 = name.new_version()
    assert workflow_2.version == 2
    workflow_1.refresh_from_db()
    assert workflow_1.schedule_active is False


def test_submit_run():
    # create a workflow
    name = WorkflowName.objects.create(name='workflow1')
    workflow = name.new_version(parameters={'parent': True, 'child': False})
    task1 = Template.objects.create(workflow=workflow, name='task1', command=[''])
    task2 = Template.objects.create(workflow=workflow, name='task2', command=[''])
    task2.upstream.add(task1)

    # submit a run
    run = workflow.submit_run(parameters={'child': True})
    tasks = list(run.task_set.all())

    # check that tasks are copied to the run correctly
    assert run.parameters == {'parent': True, 'child': True}
    assert len(tasks) == 2
    assert tasks[0].template == task1
    assert tasks[0].status == Task.QUEUED
    assert tasks[1].template == task2
    assert tasks[1].status == Task.WAITING


def test_statuses():
    # create a workflow
    name = WorkflowName.objects.create(name='workflow1')
    workflow = name.new_version(parameters={'parent': True, 'child': False})
    task1 = Template.objects.create(workflow=workflow, name='task1', command=[''])
    task2 = Template.objects.create(workflow=workflow, name='task2', command=[''])
    task2.upstream.add(task1)

    run = workflow.submit_run(parameters={'child': True})
    task1, task2 = list(run.task_set.all())

    run.update_status()
    assert run.status == Run.RUNNING

    task1.status = Task.FAILED
    task1.save()
    run.update_status()
    assert run.status == Run.RUNNING

    task2.status = Task.UPSTREAM_FAILED
    task2.save()
    run.update_status()
    assert run.status == Run.FAILED

    task1.status = Task.SUCCEEDED
    task1.save()
    task2.status = Task.SUCCEEDED
    task2.save()
    run.update_status()
    assert run.status == Run.SUCCEEDED
