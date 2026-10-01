#!/usr/bin/env python
"""Helper functions for spawning and managing external command processes."""

import logging
import multiprocessing
import os
import shlex
import sys
from logging.handlers import RotatingFileHandler
from subprocess import PIPE, Popen

PROGRAM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# make the directory for logs if it doesn't exist
logs_dir = os.path.join(PROGRAM_DIR, 'logs')
if not os.path.isdir(logs_dir):  # pragma: no cover
    os.makedirs(logs_dir)

PROCESS_LOG = logging.getLogger('process_log')

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
PROCESS_LOG.addHandler(stream_handler)

file_handler = RotatingFileHandler(os.path.join(PROGRAM_DIR, 'logs', 'process_log.txt'), maxBytes=10000000, backupCount=5)
file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
PROCESS_LOG.addHandler(file_handler)

PROCESS_LOG.setLevel(logging.INFO)

SHELL_METACHARACTERS = "|&;<>(){}$`*?[]~!\n"


class RunCommandProcess(multiprocessing.Process):
    """
    Multiprocessing process that runs a command and logs its output.

    Breaking change: RunCommandProcess does NOT run the command through a shell, so shell
    features (pipes, redirection, &&/;, $VAR expansion, globs, command substitution) are NOT
    supported. A string command is split into argv using shlex.split; a list command is used
    as-is. To use shell features, pass an explicit shell argv list such as ['sh', '-c', '...']
    or ['bash', '-lc', '...']. Set ``strict=True`` to raise a ValueError when a string command
    contains shell metacharacters (otherwise a warning is logged).
    """
    @classmethod
    def contains_shell_metacharacters(cls, command) -> bool:
        """
        Return True when command is a string containing shell metacharacters.

        Non-string commands (e.g. argv lists) return False, as do strings without
        any character from SHELL_METACHARACTERS.
        """
        if not isinstance(command, str):
            return False
        return any(char in SHELL_METACHARACTERS for char in command)

    def __init__(self, command, working_dir=None, strict: bool = False):
        multiprocessing.Process.__init__(self)

        self.command = command
        self.working_dir = working_dir
        self.strict = strict

        if RunCommandProcess.contains_shell_metacharacters(command):
            message = (
                'Command contains shell metacharacters, but RunCommandProcess no longer runs '
                'commands through a shell (breaking change). Shell features such as pipes (|), '
                'redirection (>, >>, <), &&/; chaining, $VAR expansion, globs (*, ?, [...]), '
                'command substitution (`...`) and subshells are NOT supported. Invoke a shell '
                "explicitly (e.g. ['sh', '-c', command] or ['bash', '-lc', command]) or pass an "
                'argv list for exact control.'
            )
            if strict:
                raise ValueError(message)
            PROCESS_LOG.warning(message)

    def run(self):
        """Execute the command, stream stdout/stderr to the process logger, then restore cwd."""
        current_run_dir = os.getcwd()
        if self.working_dir is not None and current_run_dir != self.working_dir:
            os.chdir(self.working_dir)
            PROCESS_LOG.info(f'Switched to working dir: {os.getcwd()}')

        process_id = multiprocessing.current_process().name
        PROCESS_LOG.info(f'{process_id} | Spawned new process to run command: {self.command}')
        PROCESS_LOG.info(f'{process_id} | Process starting...')

        # Intentional (breaking change): the shell is NOT used, so shell features are unavailable.
        argv = shlex.split(self.command) if isinstance(self.command, str) else self.command
        command_process = Popen(argv, stdout=PIPE, stderr=PIPE, universal_newlines=True)

        for stdout_line in iter(command_process.stdout.readline, ""):
            PROCESS_LOG.info(f'{process_id} | {stdout_line.strip()}')

        for stdout_line in iter(command_process.stderr.readline, ""):
            PROCESS_LOG.error(f'{process_id} | {stdout_line.strip()}')

        PROCESS_LOG.info(f'{process_id} | Process finished')

        if current_run_dir != os.getcwd():
            os.chdir(current_run_dir)
            PROCESS_LOG.info(f'Switched back to: {os.getcwd()}')
