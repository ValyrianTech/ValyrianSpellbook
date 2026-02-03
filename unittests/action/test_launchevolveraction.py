#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock

from action.launchevolveraction import LaunchEvolverAction, DARWIN_PROGRAM
from action.actiontype import ActionType


class TestLaunchEvolverAction(object):
    """Tests for LaunchEvolverAction"""

    def test_launchevolveraction_init(self):
        action = LaunchEvolverAction('test_evolver_action')
        assert action.id == 'test_evolver_action'
        assert action.action_type == ActionType.LAUNCHEVOLVER
        assert action.job_config is None
        assert action.run_command is None

    def test_launchevolveraction_configure(self):
        action = LaunchEvolverAction('test_evolver_action')
        action.configure(job_config='config.json')
        assert action.job_config == 'config.json'
        assert 'config.json' in action.run_command
        assert DARWIN_PROGRAM in action.run_command

    def test_launchevolveraction_json_encodable(self):
        action = LaunchEvolverAction('test_evolver_action')
        action.configure(job_config='config.json', created=1609459200)
        result = action.json_encodable()
        assert result['id'] == 'test_evolver_action'
        assert result['action_type'] == ActionType.LAUNCHEVOLVER
        assert result['job_config'] == 'config.json'

    @mock.patch('action.spawnprocessaction.RunCommandProcess')
    def test_launchevolveraction_run(self, mock_process_class):
        mock_process = mock.MagicMock()
        mock_process_class.return_value = mock_process

        action = LaunchEvolverAction('test_evolver_action')
        action.configure(job_config='config.json')
        action.run()

        # Verify run_command was updated with python3.7
        assert 'python3.7' in action.run_command
        assert DARWIN_PROGRAM in action.run_command
        assert 'config.json' in action.run_command
