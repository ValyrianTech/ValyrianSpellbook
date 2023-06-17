#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from .action import Action
from .actiontype import ActionType
from helpers.loghelpers import LOG
from helpers.runcommandprocess import RunCommandProcess


class SpawnProcessAction(Action):
    def __init__(self, action_id):
        super(SpawnProcessAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.SPAWNPROCESS
        self.run_command = None
        self.working_dir = None

    def run(self):
        """
        Run the action

        :return: True upon success, False upon failure
        """
        if self.run_command is None or self.run_command == '':
            return False

        try:
            process = RunCommandProcess(command=self.run_command, working_dir=self.working_dir)
            process.start()
        except Exception as ex:
            LOG.error('Spawning process failed: %s' % ex)
            return False

        return True

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['run_command']  : The command to run
        """
        super(SpawnProcessAction, self).configure(**config)
        if 'run_command' in config:
            self.run_command = config['run_command']
        if 'working_dir' in config:
            self.working_dir = config['working_dir']

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super(SpawnProcessAction, self).json_encodable()
        ret.update({'run_command': self.run_command, 'working_dir': self.working_dir})
        return ret
