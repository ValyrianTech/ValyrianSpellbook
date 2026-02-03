#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import os
import tempfile
import mock

from helpers.actionhelpers import (
    get_actions,
    get_action_config,
    get_action,
    save_action,
    delete_action,
    run_action,
    get_reveal,
    ACTIONS_DIR,
)
from action.actiontype import ActionType


class TestActionHelpers(object):
    """Tests for action helper functions"""

    @mock.patch('helpers.actionhelpers.glob.glob')
    def test_get_actions(self, mock_glob):
        """Test getting list of action IDs"""
        mock_glob.return_value = [
            'json/public/actions/action1.json',
            'json/public/actions/action2.json',
        ]
        result = get_actions()
        assert 'action1' in result
        assert 'action2' in result

    @mock.patch('helpers.actionhelpers.load_from_json_file')
    def test_get_action_config(self, mock_load):
        """Test getting action configuration"""
        mock_load.return_value = {'action_type': 'Command', 'run_command': 'echo test'}
        result = get_action_config('test_action')
        assert result['action_type'] == 'Command'

    @mock.patch('helpers.actionhelpers.load_from_json_file')
    def test_get_action_config_not_found(self, mock_load):
        """Test getting config for non-existent action"""
        mock_load.side_effect = IOError('File not found')
        result = get_action_config('nonexistent')
        assert result == {}

    @mock.patch('helpers.actionhelpers.load_from_json_file')
    def test_get_action_command(self, mock_load):
        """Test getting a Command action"""
        mock_load.return_value = {'action_type': ActionType.COMMAND}
        action = get_action('test_action')
        assert action.action_type == ActionType.COMMAND

    @mock.patch('helpers.actionhelpers.load_from_json_file')
    def test_get_action_spawnprocess(self, mock_load):
        """Test getting a SpawnProcess action"""
        mock_load.return_value = {'action_type': ActionType.SPAWNPROCESS}
        action = get_action('test_action')
        assert action.action_type == ActionType.SPAWNPROCESS

    @mock.patch('helpers.actionhelpers.load_from_json_file')
    def test_get_action_sendtransaction(self, mock_load):
        """Test getting a SendTransaction action"""
        mock_load.return_value = {'action_type': ActionType.SENDTRANSACTION}
        action = get_action('test_action')
        assert action.action_type == ActionType.SENDTRANSACTION

    @mock.patch('helpers.actionhelpers.load_from_json_file')
    def test_get_action_revealsecret(self, mock_load):
        """Test getting a RevealSecret action"""
        mock_load.return_value = {'action_type': ActionType.REVEALSECRET}
        action = get_action('test_action')
        assert action.action_type == ActionType.REVEALSECRET

    @mock.patch('helpers.actionhelpers.load_from_json_file')
    def test_get_action_sendmail(self, mock_load):
        """Test getting a SendMail action"""
        mock_load.return_value = {'action_type': ActionType.SENDMAIL}
        action = get_action('test_action')
        assert action.action_type == ActionType.SENDMAIL

    @mock.patch('helpers.actionhelpers.load_from_json_file')
    def test_get_action_webhook(self, mock_load):
        """Test getting a Webhook action"""
        mock_load.return_value = {'action_type': ActionType.WEBHOOK}
        action = get_action('test_action')
        assert action.action_type == ActionType.WEBHOOK

    @mock.patch('helpers.actionhelpers.load_from_json_file')
    def test_get_action_deletetrigger(self, mock_load):
        """Test getting a DeleteTrigger action"""
        mock_load.return_value = {'action_type': ActionType.DELETETRIGGER}
        action = get_action('test_action')
        assert action.action_type == ActionType.DELETETRIGGER

    @mock.patch('helpers.actionhelpers.load_from_json_file')
    def test_get_action_launchevolver(self, mock_load):
        """Test getting a LaunchEvolver action"""
        mock_load.return_value = {'action_type': ActionType.LAUNCHEVOLVER}
        action = get_action('test_action')
        assert action.action_type == ActionType.LAUNCHEVOLVER

    @mock.patch('helpers.actionhelpers.load_from_json_file')
    def test_get_action_unknown_type(self, mock_load):
        """Test getting an action with unknown type raises error"""
        mock_load.return_value = {'action_type': 'UnknownType'}
        with pytest.raises(NotImplementedError):
            get_action('test_action')

    @mock.patch('helpers.actionhelpers.load_from_json_file')
    def test_get_action_with_type_override(self, mock_load):
        """Test getting an action with type override"""
        mock_load.return_value = {'action_type': ActionType.COMMAND}
        action = get_action('test_action', action_type=ActionType.WEBHOOK)
        assert action.action_type == ActionType.WEBHOOK

    @mock.patch('helpers.actionhelpers.get_action')
    def test_save_action(self, mock_get_action):
        """Test saving an action"""
        mock_action = mock.MagicMock()
        mock_get_action.return_value = mock_action
        
        save_action('test_action', action_type=ActionType.COMMAND, run_command='echo test')
        
        mock_action.configure.assert_called()
        mock_action.save.assert_called_once()

    @mock.patch('helpers.actionhelpers.get_action')
    def test_save_action_without_type(self, mock_get_action):
        """Test saving an action without specifying type"""
        mock_action = mock.MagicMock()
        mock_get_action.return_value = mock_action
        
        save_action('test_action', run_command='echo test')
        
        mock_action.configure.assert_called()
        mock_action.save.assert_called_once()

    @mock.patch('os.path.isfile', return_value=True)
    @mock.patch('os.remove')
    def test_delete_action(self, mock_remove, mock_isfile):
        """Test deleting an action"""
        result = delete_action('test_action')
        mock_remove.assert_called_once()
        assert result is None

    @mock.patch('os.path.isfile', return_value=False)
    def test_delete_action_not_found(self, mock_isfile):
        """Test deleting a non-existent action"""
        result = delete_action('nonexistent')
        assert 'error' in result

    @mock.patch('helpers.actionhelpers.get_action')
    def test_run_action(self, mock_get_action):
        """Test running an action"""
        mock_action = mock.MagicMock()
        mock_action.run.return_value = True
        mock_get_action.return_value = mock_action
        
        result = run_action('test_action')
        
        mock_action.run.assert_called_once()
        assert result == True

    @mock.patch('helpers.actionhelpers.get_action')
    def test_get_reveal_not_allowed(self, mock_get_action):
        """Test get_reveal when reveal is not allowed"""
        mock_action = mock.MagicMock()
        mock_action.allow_reveal = False
        mock_get_action.return_value = mock_action
        
        result = get_reveal('test_action')
        assert result is None

    @mock.patch('helpers.actionhelpers.get_action')
    def test_get_reveal_allowed(self, mock_get_action):
        """Test get_reveal when reveal is allowed"""
        mock_action = mock.MagicMock()
        mock_action.allow_reveal = True
        mock_action.reveal_text = 'secret text'
        mock_action.reveal_link = 'http://example.com'
        mock_get_action.return_value = mock_action
        
        result = get_reveal('test_action')
        assert result['reveal_text'] == 'secret text'
        assert result['reveal_link'] == 'http://example.com'
