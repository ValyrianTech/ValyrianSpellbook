#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from subprocess import Popen, PIPE

from helpers.loghelpers import LOG
from .action import Action
from .actiontype import ActionType


class CommandAction(Action):
    def __init__(self, action_id):
        super(CommandAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.COMMAND
        self.run_command = None
        self.working_dir = None

    def run(self):
        """
        Run the action

        :return: True upon success, False upon failure
        """
        if self.run_command is None or self.run_command == '':
            return False

        current_run_dir = os.getcwd()
        if self.working_dir is not None and current_run_dir != self.working_dir:
            os.chdir(self.working_dir)
            LOG.info('Switched to working dir: %s' % os.getcwd())

        LOG.info('Running command: %s' % self.run_command)
        command_process = Popen(self.run_command, stdout=PIPE, stderr=PIPE, shell=True)
        output, error = command_process.communicate()
        stripped_output = output.strip()
        LOG.info('Command output: %s' % stripped_output)

        stripped_error = error.strip()
        if len(stripped_error):
            LOG.error('Command error: %s' % stripped_error)

        if current_run_dir != os.getcwd():
            os.chdir(current_run_dir)
            LOG.info('Switched back to: %s' % os.getcwd())

        if command_process.returncode == 0:
            return True, stripped_output, stripped_error
        else:
            return False, stripped_output, stripped_error

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['run_command']  : The command to run
        """
        super(CommandAction, self).configure(**config)
        if 'run_command' in config:
            self.run_command = config['run_command']
        if 'working_dir' in config:
            self.working_dir = config['working_dir']

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super(CommandAction, self).json_encodable()
        ret.update({'run_command': self.run_command, 'working_dir': self.working_dir})
        return ret
