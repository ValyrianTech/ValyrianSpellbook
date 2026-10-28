#!/usr/bin/env python
from unittest import mock

import pytest

from action.actiontype import ActionType
from action.commandaction import CommandAction
from helpers.actionhelpers import (
    delete_action,
    get_action,
    get_action_config,
    get_actions,
    get_reveal,
    redact_action_config,
    run_action,
    save_action,
)


class TestActionHelpers:
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
        mock_load.side_effect = OSError('File not found')
        result = get_action_config('nonexistent')
        assert result == {}

    def test_get_action_config_invalid_id(self):
        """Test getting config for a path-traversal action id returns empty dict"""
        result = get_action_config('../evil')
        assert result == {}

    def test_redact_action_config_revealsecret_not_allowed(self):
        """Test redacting a RevealSecret config when reveal is not allowed"""
        config = {
            'id': 'secret_action',
            'action_type': ActionType.REVEALSECRET,
            'reveal_text': 'secret text',
            'reveal_link': 'http://example.com',
            'allow_reveal': False,
        }
        result = redact_action_config(config)
        assert 'reveal_text' not in result
        assert 'reveal_link' not in result
        assert result['id'] == 'secret_action'
        assert result['action_type'] == ActionType.REVEALSECRET
        assert result['allow_reveal'] is False

    def test_redact_action_config_revealsecret_allowed(self):
        """Test redacting a RevealSecret config when reveal is allowed"""
        config = {
            'id': 'secret_action',
            'action_type': ActionType.REVEALSECRET,
            'reveal_text': 'secret text',
            'reveal_link': 'http://example.com',
            'allow_reveal': True,
        }
        result = redact_action_config(config)
        assert result['reveal_text'] == 'secret text'
        assert result['reveal_link'] == 'http://example.com'

    def test_redact_action_config_non_dict(self):
        """Test redacting a non-dict input returns it unchanged"""
        assert redact_action_config(None) is None
        assert redact_action_config(['reveal_text']) == ['reveal_text']

    def test_redact_action_config_non_revealsecret(self):
        """Test redacting a non-RevealSecret config returns it unchanged"""
        config = {
            'id': 'command_action',
            'action_type': ActionType.COMMAND,
            'run_command': 'echo test',
        }
        result = redact_action_config(config)
        assert result == config

    def test_redact_action_config_strips_private_key(self):
        """Test redacting a SendTransaction config removes its private key"""
        config = {
            'id': 'send_tx_action',
            'action_type': ActionType.SENDTRANSACTION,
            'private_key': 'L1234567890abcdef',
            'sending_address': 'send_addr',
        }
        result = redact_action_config(config)
        assert 'private_key' not in result
        assert result['id'] == 'send_tx_action'
        assert result['action_type'] == ActionType.SENDTRANSACTION
        assert result['sending_address'] == 'send_addr'

    def test_redact_action_config_strips_private_key_generic_dict(self):
        """Test redacting a generic dict removes its private key"""
        config = {'private_key': 'L1234567890abcdef', 'foo': 'bar'}
        result = redact_action_config(config)
        assert 'private_key' not in result
        assert result == {'foo': 'bar'}

    def test_redact_action_config_strips_mixed_case_private_key(self):
        """Test redacting a config removes a mixed-case private key"""
        config = {'Private_Key': 'L1234567890abcdef', 'foo': 'bar'}
        result = redact_action_config(config)
        assert 'Private_Key' not in result
        assert result == {'foo': 'bar'}

    def test_redact_action_config_strips_upper_case_private_key(self):
        """Test redacting a config removes an upper-case private key"""
        config = {'PRIVATE_KEY': 'L1234567890abcdef', 'foo': 'bar'}
        result = redact_action_config(config)
        assert 'PRIVATE_KEY' not in result
        assert result == {'foo': 'bar'}

    def test_redact_action_config_strips_other_sensitive_keys(self):
        """Test redacting a config removes other sensitive keys case-insensitively"""
        config = {
            'api_secret': 'api-secret-value',
            'Mnemonic': 'mnemonic-words',
            'foo': 'bar',
        }
        result = redact_action_config(config)
        assert 'api_secret' not in result
        assert 'Mnemonic' not in result
        assert result == {'foo': 'bar'}

    def test_redact_action_config_strips_secret_values(self):
        """Test redacted secret values are absent from the output"""
        config = {
            'private_key': 'L1234567890abcdef',
            'api_key': 'sk-1234567890',
            'mnemonic': 'abandon ability able',
            'foo': 'bar',
        }
        result = redact_action_config(config)
        assert result == {'foo': 'bar'}
        assert 'L1234567890abcdef' not in str(result)
        assert 'sk-1234567890' not in str(result)
        assert 'abandon ability able' not in str(result)

    def test_redact_action_config_sendtransaction_secret_value_absent(self):
        """Test redacting a SendTransaction config removes the secret value"""
        config = {
            'id': 'send_tx_action',
            'action_type': ActionType.SENDTRANSACTION,
            'private_key': 'L1234567890abcdef-SEKRET',
            'sending_address': 'send_addr',
            'recipient_address': 'recv_addr',
        }
        result = redact_action_config(config)
        assert 'private_key' not in result
        assert 'L1234567890abcdef-SEKRET' not in str(result)
        assert result['action_type'] == ActionType.SENDTRANSACTION
        assert result['sending_address'] == 'send_addr'
        assert result['recipient_address'] == 'recv_addr'
        assert result != config

    def test_redact_action_config_sendtransaction_multiple_secrets_absent(self):
        """Test redacting a SendTransaction config removes multiple secret values"""
        config = {
            'id': 'send_tx_action',
            'action_type': ActionType.SENDTRANSACTION,
            'private_key': 'L1234567890abcdef-SEKRET',
            'Mnemonic': 'send-tx-mnemonic-SEKRET',
            'sending_address': 'send_addr',
            'recipient_address': 'recv_addr',
        }
        result = redact_action_config(config)
        assert 'private_key' not in result
        assert 'Mnemonic' not in result
        assert 'L1234567890abcdef-SEKRET' not in str(result)
        assert 'send-tx-mnemonic-SEKRET' not in str(result)
        assert result['sending_address'] == 'send_addr'
        assert result['recipient_address'] == 'recv_addr'

    @mock.patch('helpers.actionhelpers.load_from_json_file')
    def test_get_action_unknown_id_returns_command_action(self, mock_load):
        """Test getting an action with an unknown id returns a CommandAction"""
        mock_load.side_effect = OSError('File not found')
        action = get_action('does_not_exist')
        assert isinstance(action, CommandAction)
        assert action.action_type == ActionType.COMMAND
        assert action.id == 'does_not_exist'

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

    def test_delete_action_invalid_id(self):
        """Test deleting a path-traversal action id returns an error"""
        result = delete_action('../evil')
        assert 'error' in result

    @mock.patch('helpers.actionhelpers.get_action')
    def test_run_action(self, mock_get_action):
        """Test running an action"""
        mock_action = mock.MagicMock()
        mock_action.run.return_value = True
        mock_get_action.return_value = mock_action
        
        result = run_action('test_action')
        
        mock_action.run.assert_called_once()
        assert result

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
