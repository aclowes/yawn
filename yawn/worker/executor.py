import errno
import logging
import os
import signal
import subprocess
import select
import selectors
import time
import typing

logger = logging.getLogger(__name__)


class Result:
    """Returned to communicate the status of a process"""
    stdout = None
    stderr = None
    returncode = None

    def __init__(self, execution_id):
        self.execution_id = execution_id


class Execution:
    """Internal process tracker"""

    def __init__(self, process, execution_id, timeout):
        self.id = execution_id
        self.process = process
        self.start_time = time.monotonic()
        self.deadline = self.start_time + timeout if timeout else None


class Manager:
    """
    Class for starting subprocesses and reading from them.
    """

    def __init__(self):
        """"""
        self.selector = selectors.DefaultSelector()

        # dict mapping file descriptors to the owning subprocess
        self.pipes = dict()  # type: typing.Dict[typing.io, Execution]
        self.running = dict()  # type: typing.Dict[int, Execution]

    def start_subprocess(self, execution_id: int, command: list, environment: dict, timeout: int) -> None:
        """
        Start a subprocess:
        - extend the parent process's environment with custom environment variables
        - track stdout and stderr file descriptors for later reading
        - set process group to facilitate killing the subprocess if needed

        :param execution_id: the ID of the Execution instance being run
        :param command: a list of arguments, first argument must be an executable
        :param environment: environment variables from the WorkflowRun
        :param timeout: maximum number of seconds the process should be allowed to run for
        """
        process_environment = os.environ.copy()
        process_environment.update(environment)
        logger.info('Starting execution #%s', execution_id)

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   preexec_fn=os.setpgrp, env=process_environment)

        # store references to the process and file descriptors
        execution = Execution(process, execution_id, timeout)
        self.pipes.update({
            process.stdout: execution,
            process.stderr: execution
        })
        self.running[execution_id] = execution

    def read_output(self, timeout=0.1) -> typing.List[Result]:
        """
        Read from all ready subprocess file descriptors.

        The returned byte string could include partial utf-8 characters,
        and when decoding the user should trim 0-3 bytes off the end to
        get a readable unicode string.

        :param timeout: in seconds, provided for testing
        """
        all_results = {}
        read_set = self.pipes.keys()

        try:
            # 1/10 second timeout so we return control to the calling event loop
            # if no file descriptors are ready to read
            read_ready, _, _ = select.select(read_set, [], [], timeout)
        except select.error as exc:
            # a signal could interrupt. fixed in python 3.5:
            # https://www.python.org/dev/peps/pep-0475/
            if exc.args[0] != errno.EINTR:
                raise
            read_ready = []

        # read from each ready file descriptor
        for fd in read_ready:
            execution = self.pipes[fd]
            # Popen gives us io.BufferedReader; use read1 to get a single read
            data = fd.read1(1024)

            if data == b'':
                # the pipe is closed
                fd.close()
                del self.pipes[fd]
            else:
                result = all_results.setdefault(execution.id, Result(execution.id))
                if fd == execution.process.stdout:
                    result.stdout = data
                else:
                    result.stderr = data

        # check if each running process needs cleanup
        for execution in list(self.running.values()):
            # check if the process should be killed
            if execution.deadline and execution.deadline < time.monotonic():
                # kill the process group, in an attempt to kill any children it has spawned
                try:
                    # setpgrp above sets the PGID to the subprocess' PID
                    os.killpg(execution.process.pid, signal.SIGKILL)
                    logger.info('Terminated execution #%s', execution.id)
                except (ProcessLookupError, PermissionError) as exc:
                    logger.info('Execution #%s was marked to kill but has already exited (%s)',
                                execution.id, type(exc))

            # check if the process has exited
            try:
                execution.process.wait(timeout=0)
            except subprocess.TimeoutExpired:
                continue  # we'll try again later

            # we may not have read everything available, so only cleanup after all pipes are closed
            open_pipes = {execution.process.stdout, execution.process.stderr} & set(self.pipes.keys())
            if not open_pipes and execution.process.returncode is not None:
                result = all_results.setdefault(execution.id, Result(execution.id))
                result.returncode = execution.process.returncode
                run_time = time.monotonic() - execution.start_time
                logger.info('Execution #%s exited with code %s after %s seconds',
                            execution.id, result.returncode, run_time)
                del self.running[execution.id]

        return list(all_results.values())

    def mark_terminated(self, execution_ids: typing.Iterable[int]):
        """
        Set the deadline to now for the given execution_ids so they
        are terminated in the next loop.
        """
        now = time.monotonic()
        for execution_id in execution_ids:
            if execution_id in self.running:
                self.running[execution_id].deadline = now
            else:
                logger.info('Execution #%s is not running, ignoring termination request', execution_id)

    def get_running_ids(self):
        return list(self.running.keys())
