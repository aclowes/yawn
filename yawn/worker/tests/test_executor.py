import time
import pytest

from unittest import mock

from .. import executor


@pytest.fixture()
def manager():
    return executor.Manager()


def test_read_output(manager):
    execution_id = 1
    command = 'echo starting && sleep 0.1 && echo stopping 1>&2'
    manager.start_subprocess(execution_id, command, environment={}, timeout=None)

    # stdout is ready
    results = manager.read_output(timeout=1)
    assert len(results) == 1, 'Unexpected state {}'.format(manager.running[1])
    assert results[0].stdout == 'starting\n'
    assert results[0].stderr is None
    assert results[0].returncode is None
    assert results[0].execution_id == execution_id

    # sleep to ensure the returncode is ready
    time.sleep(1)

    # stderr is ready
    results = manager.read_output(timeout=1)
    assert len(results) == 1, 'Unexpected state {}'.format(manager.running[1])
    assert results[0].stdout is None
    assert results[0].stderr == 'stopping\n'
    assert results[0].execution_id == execution_id

    # grhh... sometime it exits later, on circleci it often exits concurrently
    if results[0].returncode is None:
        results = manager.read_output(timeout=1)
        assert len(results) == 1, 'Unexpected state {}'.format(manager.running[1])

    assert results[0].execution_id == execution_id
    assert results[0].returncode == 0


def test_timeout(manager):
    command = 'sleep 10'
    manager.start_subprocess(1, command, environment={}, timeout=-1)

    results = manager.read_output()  # first read kills, but the pipes are still open
    assert results == []

    results = manager.read_output(timeout=1)
    assert len(results) == 1, 'Unexpected state {}'.format(manager.running[1])
    assert results[0].stdout is None
    assert results[0].stderr is None
    assert results[0].returncode == -9


@mock.patch('yawn.worker.executor.os.killpg')
def test_timeout_already_exited(mock_kill, manager):
    command = 'true'
    manager.start_subprocess(1, command, environment={}, timeout=-1)

    results = manager.read_output(timeout=1)
    assert len(results) == 1, 'Unexpected state {}'.format(manager.running[1])
    assert results[0].stdout is None
    assert results[0].stderr is None
    assert results[0].returncode == 0

    assert mock_kill.call_count == 1


def test_mark_terminated(manager):
    execution_id = 1
    execution = executor.Execution(None, execution_id, None)
    manager.running[execution_id] = execution
    manager.mark_terminated([1, 2])
    assert execution.deadline <= time.monotonic()
