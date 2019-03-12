#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from actiontype import ActionType
from spawnprocessaction import SpawnProcessAction

DARWIN_PROGRAM = os.path.join('darwin', 'darwin.py')


class LaunchEvolverAction(SpawnProcessAction):
    def __init__(self, action_id):
        super(LaunchEvolverAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.LAUNCHEVOLVER
        # self.run_command = '%s %s' % (DARWIN_PROGRAM, r'D:\darwin\fulltest.json')
        self.job_config = None

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['run_command']  : The command to run
        """
        super(LaunchEvolverAction, self).configure(**config)
        if 'job_config' in config:
            self.job_config = config['job_config']

        self.run_command = '%s %s' % (DARWIN_PROGRAM, self.job_config)

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super(LaunchEvolverAction, self).json_encodable()
        ret.update({'job_config': self.job_config})
        return ret
