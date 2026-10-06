#!/usr/bin/env python

"""Action that spawns a new system process."""

from helpers.loghelpers import LOG
from helpers.runcommandprocess import RunCommandProcess

from .action import Action
from .actionresult import ActionResult
from .actiontype import ActionType


class SpawnProcessAction(Action):
    """Action that spawns a new system process."""
    def __init__(self, action_id):
        super().__init__(action_id=action_id)
        self.action_type = ActionType.SPAWNPROCESS
        self.run_command = None
        self.working_dir = None

    def run(self):
        """
        Run the action

        A successful ActionResult (success=True) means the underlying process was
        successfully launched, i.e. RunCommandProcess.start() did not raise an
        exception. It does NOT mean the spawned process ran to completion or
        completed successfully. Callers should not interpret success=True as
        evidence of the spawned process's outcome.

        :return: An ActionResult indicating success or failure
        """
        if self.run_command is None or self.run_command == '':
            return ActionResult(success=False)

        try:
            process = RunCommandProcess(command=self.run_command, working_dir=self.working_dir)
            process.start()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Spawning process failed: {ex}')
            return ActionResult(success=False)

        return ActionResult(success=True)

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
