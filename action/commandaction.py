#!/usr/bin/env python
"""Action that executes a system command."""

import shlex
import subprocess

from helpers.loghelpers import LOG

from .action import Action
from .actiontype import ActionType


class CommandAction(Action):
    """Action that executes a system command."""
    def __init__(self, action_id):
        super().__init__(action_id=action_id)
        self.action_type = ActionType.COMMAND
        self.run_command = None
        self.working_dir = None

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

        :return: True upon success, False upon failure
        """
        if self.run_command is None or self.run_command == '':
            return False

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
            result = subprocess.run(argv, shell=False, capture_output=True, cwd=self.working_dir)
        except OSError as e:
            LOG.error(f'Command failed to run: {e}')
            return False, b'', str(e).encode()
        stripped_output = result.stdout.strip()
        LOG.info(f'Command output: {stripped_output}')

        stripped_error = result.stderr.strip()
        if len(stripped_error):
            LOG.error(f'Command error: {stripped_error}')

        if result.returncode == 0:
            return True, stripped_output, stripped_error
        else:
            return False, stripped_output, stripped_error

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['run_command']  : The command to run
        """
        super().configure(**config)
        if 'run_command' in config:
            self.run_command = config['run_command']
        if 'working_dir' in config:
            self.working_dir = config['working_dir']

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super().json_encodable()
        ret.update({'run_command': self.run_command, 'working_dir': self.working_dir})
        return ret
