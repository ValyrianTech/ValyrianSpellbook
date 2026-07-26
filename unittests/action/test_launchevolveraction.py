#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock
import importlib

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


class TestLaunchEvolverActionPlatformCheck(object):
    """Tests for platform-specific module-level code in launchevolveraction.py"""

    def test_platform_windows(self):
        """Test that Windows platform sets DARWIN_PROGRAM correctly (line 13)"""
        with mock.patch('action.launchevolveraction.platform.system', return_value='Windows'):
            import action.launchevolveraction as mod
            importlib.reload(mod)
            assert mod.DARWIN_PROGRAM is not None
        importlib.reload(mod)
        # Reload helpers.actionhelpers so its LaunchEvolverAction reference is fresh
        import helpers.actionhelpers
        importlib.reload(helpers.actionhelpers)

    def test_platform_unsupported(self):
        """Test that unsupported platform raises NotImplementedError (line 17)"""
        with mock.patch('action.launchevolveraction.platform.system', return_value='Darwin'):
            import action.launchevolveraction as mod
            with pytest.raises(NotImplementedError):
                importlib.reload(mod)
        importlib.reload(mod)
        # Reload helpers.actionhelpers so its LaunchEvolverAction reference is fresh
        import helpers.actionhelpers
        importlib.reload(helpers.actionhelpers)
