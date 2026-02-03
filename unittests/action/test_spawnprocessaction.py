#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock

from action.spawnprocessaction import SpawnProcessAction
from action.actiontype import ActionType


class TestSpawnProcessAction(object):
    """Tests for SpawnProcessAction"""

    def test_spawnprocessaction_init(self):
        action = SpawnProcessAction('test_spawn_action')
        assert action.id == 'test_spawn_action'
        assert action.action_type == ActionType.SPAWNPROCESS
        assert action.run_command is None
        assert action.working_dir is None

    def test_spawnprocessaction_configure(self):
        action = SpawnProcessAction('test_spawn_action')
        action.configure(run_command='echo hello', working_dir='/tmp')
        assert action.run_command == 'echo hello'
        assert action.working_dir == '/tmp'

    def test_spawnprocessaction_configure_without_optional_params(self):
        action = SpawnProcessAction('test_spawn_action')
        action.configure()
        assert action.run_command is None
        assert action.working_dir is None

    def test_spawnprocessaction_json_encodable(self):
        action = SpawnProcessAction('test_spawn_action')
        action.configure(run_command='echo hello', working_dir='/tmp', created=1609459200)
        result = action.json_encodable()
        assert result['id'] == 'test_spawn_action'
        assert result['action_type'] == ActionType.SPAWNPROCESS
        assert result['run_command'] == 'echo hello'
        assert result['working_dir'] == '/tmp'

    def test_spawnprocessaction_run_with_no_command(self):
        action = SpawnProcessAction('test_spawn_action')
        assert action.run() == False

    def test_spawnprocessaction_run_with_empty_command(self):
        action = SpawnProcessAction('test_spawn_action')
        action.run_command = ''
        assert action.run() == False

    @mock.patch('action.spawnprocessaction.RunCommandProcess')
    def test_spawnprocessaction_run_success(self, mock_process_class):
        mock_process = mock.MagicMock()
        mock_process_class.return_value = mock_process

        action = SpawnProcessAction('test_spawn_action')
        action.configure(run_command='echo hello', working_dir='/tmp')
        result = action.run()

        assert result == True
        mock_process_class.assert_called_once_with(command='echo hello', working_dir='/tmp')
        mock_process.start.assert_called_once()

    @mock.patch('action.spawnprocessaction.RunCommandProcess')
    def test_spawnprocessaction_run_exception(self, mock_process_class):
        mock_process_class.side_effect = Exception('Process error')

        action = SpawnProcessAction('test_spawn_action')
        action.configure(run_command='echo hello')
        result = action.run()

        assert result == False
