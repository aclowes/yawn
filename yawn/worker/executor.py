import errno
import os
import signal
import subprocess
import select
import selectors
import time
import typing

from yawn.utilities import logger


class Result:
    """
    Returned to communicate the status of a process

    In practice has stdout/stderr OR returncode, not both
    """
    stdout = None
    stderr = None
    returncode = None

    def __init__(self, execution_id):
        self.execution_id = execution_id

    def __str__(self):
        return 'Result(id={}, stdout={}, stderr={}, returncode={})'.format(
            self.execution_id, self.stdout, self.stderr, self.returncode)


class Execution:
    """Internal process tracker"""

    def __init__(self, process, execution_id, timeout):
        self.id = execution_id
        self.process = process
        self.start_time = time.monotonic()
        self.deadline = self.start_time + timeout if timeout else None

    def __str__(self):
        return 'Result(id={}, stdout={}, stderr={}, returncode={})'.format(
            self.id, self.process.stdout, self.process.stderr, self.process.returncode)


class Manager:
    """
    Class for starting subprocesses and reading from them.
    """

    def __init__(self):
        self.selector = selectors.DefaultSelector()

        # dict mapping file descriptors to the owning subprocess
        self.pipes = dict()  # type: typing.Dict[typing.io, Execution]
        self.running = dict()  # type: typing.Dict[int, Execution]

    def start_subprocess(self, execution_id: int, command: str, environment: dict, timeout: int) -> None:
        """
        Start a subprocess:
        - extend the parent process's environment with custom environment variables
        - track stdout and stderr file descriptors for later reading
        - set process group to facilitate killing any children of the command

        :param execution_id: the ID of the Execution instance being run
        :param command: a list of arguments, first argument must be an executable
        :param environment: environment variables from the WorkflowRun
        :param timeout: maximum number of seconds the process should be allowed to run for
        """
        process_environment = os.environ.copy()
        for key, value in environment.items():
            # all variables must be strings, be explicit so it fail in our code
            process_environment[key] = str(value)

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   preexec_fn=os.setpgrp, env=process_environment, shell=True)

        # store references to the process and file descriptors
        # Popen gives us io.BufferedReader; get the raw file handle instead
        execution = Execution(process, execution_id, timeout)
        self.pipes.update({
            process.stdout.raw: execution,
            process.stderr.raw: execution
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
            logger.warning('Received select.error: %s', exc)
            read_ready = []

        # read from each ready file descriptor
        for fd in read_ready:
            execution = self.pipes[fd]
            data = fd.read(1024)
            if data == b'':
                # the pipe is closed
                fd.close()
                del self.pipes[fd]
                continue

            # keep reading up to 3 more bytes until we get a full UTF-8 character
            for _ in range(3):
                try:
                    data = data.decode('utf-8')
                    break
                except UnicodeDecodeError:
                    data += fd.read1(1)
            else:
                logger.error('Unable to decode byte data! Throwing it away.')

            result = all_results.setdefault(execution.id, Result(execution.id))
            if fd == execution.process.stdout.raw:
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
                                execution.id, exc.__class__.__name__)

            # check if the process has exited
            exit_code = execution.process.poll()
            if exit_code is None:
                continue  # we'll check again later

            # we may not have read everything available, so only cleanup after all pipes are closed
            open_pipes = (
                {execution.process.stdout.raw, execution.process.stderr.raw}
                & set(self.pipes.keys())
            )
            if not open_pipes:
                result = all_results.setdefault(execution.id, Result(execution.id))
                result.returncode = execution.process.returncode
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
