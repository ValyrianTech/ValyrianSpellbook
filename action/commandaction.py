#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from subprocess import Popen, PIPE

from action import Action
from actiontype import ActionType


class CommandAction(Action):
    def __init__(self, action_id):
        super(CommandAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.COMMAND
        self.run_command = None

    def run(self):
        if self.run_command is None or self.run_command == '':
            return False

        command_args = [str(arg) for arg in self.run_command.split()]

        logging.getLogger('Spellbook').info('Running command: %s' % ' '.join(command_args))
        command_process = Popen(command_args, stdout=PIPE, stderr=PIPE, shell=True)
        output, error = command_process.communicate()
        stripped_output = output.strip()
        logging.getLogger('Spellbook').info('Command output: %s' % stripped_output)

        stripped_error = error.strip()
        if len(stripped_error):
            logging.getLogger('Spellbook').error('Command error: %s' % stripped_error)

        return True if command_process.returncode == 0 else False

    def configure(self, **config):
        super(CommandAction, self).configure(**config)
        if 'run_command' in config:
            self.run_command = config['run_command']

    def json_encodable(self):
        ret = super(CommandAction, self).json_encodable()
        ret.update({'run_command': self.run_command})
        return ret
