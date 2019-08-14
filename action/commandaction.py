#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE

from helpers.loghelpers import LOG
from .action import Action
from .actiontype import ActionType


class CommandAction(Action):
    def __init__(self, action_id):
        super(CommandAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.COMMAND
        self.run_command = None

    def run(self):
        """
        Run the action

        :return: True upon success, False upon failure
        """
        if self.run_command is None or self.run_command == '':
            return False

        LOG.info('Running command: %s' % self.run_command)
        command_process = Popen(self.run_command, stdout=PIPE, stderr=PIPE, shell=True)
        output, error = command_process.communicate()
        stripped_output = output.strip()
        LOG.info('Command output: %s' % stripped_output)

        stripped_error = error.strip()
        if len(stripped_error):
            LOG.error('Command error: %s' % stripped_error)

        return True if command_process.returncode == 0 else False

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['run_command']  : The command to run
        """
        super(CommandAction, self).configure(**config)
        if 'run_command' in config:
            self.run_command = config['run_command']

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super(CommandAction, self).json_encodable()
        ret.update({'run_command': self.run_command})
        return ret
