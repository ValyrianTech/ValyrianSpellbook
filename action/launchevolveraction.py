#!/usr/bin/env python
"""Action that launches a Darwin evolutionary process."""

import os
import platform

from helpers.loghelpers import LOG

from .actiontype import ActionType
from .spawnprocessaction import SpawnProcessAction

PROGRAM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if platform.system() == 'Windows' or platform.system() == 'Linux':
    DARWIN_PROGRAM = os.path.join(PROGRAM_DIR, 'darwin', 'darwin.py')
else:
    raise NotImplementedError('Unsupported platform: only windows and linux are supported')


class LaunchEvolverAction(SpawnProcessAction):
    """Action that launches a Darwin evolutionary process."""
    def __init__(self, action_id):
        super().__init__(action_id=action_id)
        self.action_type = ActionType.LAUNCHEVOLVER
        self.job_config = None

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['run_command']  : The command to run
        """
        super().configure(**config)
        if 'job_config' in config:
            self.job_config = config['job_config']
            self.run_command = f'"{DARWIN_PROGRAM}" {self.job_config}'

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super().json_encodable()
        ret.update({'job_config': self.job_config})
        return ret

    def run(self):
        """Run."""
        self.run_command = f'python3.7 "{DARWIN_PROGRAM}" {self.job_config}'
        LOG.info(f'Launching evolver with command: {self.run_command}')
        super().run()
