#!/usr/bin/env python
"""Action that executes a system command."""

import shlex
import subprocess

from helpers.loghelpers import LOG

from .action import Action
from .actionresult import ActionResult
from .actiontype import ActionType

# Bounds synchronous command execution so a hung command fails the action
# instead of blocking the trigger/action processing loop.
DEFAULT_COMMAND_TIMEOUT = 60


class CommandAction(Action):
    """Action that executes a system command."""
    def __init__(self, action_id):
        super().__init__(action_id=action_id)
        self.action_type = ActionType.COMMAND
        self.run_command = None
        self.working_dir = None
        self.command_timeout = DEFAULT_COMMAND_TIMEOUT

    def run(self, **kwargs):
        """
        Run the action

        if a parameter called 'placeholders' is passed in the kwargs, the placeholders in the run_command will be replaced with the values in the placeholders dict

        Note: placeholders are intended to occupy a complete command argument/token (e.g. run_command='echo {MESSAGE}').
        Each substituted value is quoted with shlex.quote() so that a whole-token placeholder can never inject shell
        metacharacters, regardless of the characters contained in the value. Embedding a placeholder inside a larger
        already-quoted literal (e.g. run_command='echo "prefix {MESSAGE} suffix"') is NOT supported: the quoting inserted
        by shlex.quote() then interacts with the surrounding quoting, and the value becomes a literal substring of that
        single argument rather than its own quoted token.

        The command is bounded by ``self.command_timeout`` (default
        ``DEFAULT_COMMAND_TIMEOUT``); if it does not complete within that many
        seconds a failure ``ActionResult`` with ``stderr == b'timeout'`` is
        returned instead of blocking indefinitely. This is a synchronous action:
        unlike ``SpawnProcessAction`` / ``RunCommandProcess``, which deliberately
        launch detached processes and are therefore not subject to this timeout,
        the command here runs to completion (or timeout) before returning.

        :return: An ActionResult indicating success or failure, along with the
                 stdout and stderr produced by the command
        """
        if self.run_command is None or self.run_command == '':
            return ActionResult(success=False)

        command = self.run_command
        placeholders = kwargs.get('placeholders', {})
        for key, value in placeholders.items():
            LOG.info(f'Replacing placeholder {key} with {value}')
            command = command.replace(key, shlex.quote(str(value)))

        LOG.info(f'Running command: {command}')
        if self.working_dir is not None:
            LOG.info(f'Working dir: {self.working_dir}')

        argv = shlex.split(command)
        try:
            result = subprocess.run(argv, shell=False, capture_output=True, cwd=self.working_dir, check=False, timeout=self.command_timeout)
        except subprocess.TimeoutExpired as e:
            LOG.error(f'Command timed out after {self.command_timeout}s: {command}')
            return ActionResult(success=False, stdout=e.stdout or b'', stderr=b'timeout')
        except OSError as e:
            LOG.error(f'Command failed to run: {e}')
            return ActionResult(success=False, stdout=b'', stderr=str(e).encode())
        stripped_output = result.stdout.strip()
        LOG.info(f'Command output: {stripped_output}')

        stripped_error = result.stderr.strip()
        if len(stripped_error):
            LOG.error(f'Command error: {stripped_error}')

        if result.returncode == 0:
            return ActionResult(success=True, stdout=stripped_output, stderr=stripped_error)
        else:
            return ActionResult(success=False, stdout=stripped_output, stderr=stripped_error)

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['run_command']      : The command to run
                       - config['working_dir']      : The working directory to run the command in
                       - config['command_timeout']  : Positive number of seconds to bound command
                                                      execution (default DEFAULT_COMMAND_TIMEOUT)
        """
        super().configure(**config)
        if 'run_command' in config:
            self.run_command = config['run_command']
        if 'working_dir' in config:
            self.working_dir = config['working_dir']
        if 'command_timeout' in config:
            self.command_timeout = config['command_timeout']

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super().json_encodable()
        ret.update({'run_command': self.run_command, 'working_dir': self.working_dir, 'command_timeout': self.command_timeout})
        return ret
