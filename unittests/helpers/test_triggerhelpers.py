#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock

from helpers.triggerhelpers import (
    get_triggers,
    get_trigger_config,
    get_trigger,
    save_trigger,
    delete_trigger,
    activate_trigger,
    check_triggers,
    verify_signed_message,
    sign_message,
    http_get_request,
    http_post_request,
    http_delete_request,
    signed_message_request,
    file_download,
    TRIGGERS_DIR,
)
from trigger.triggertype import TriggerType


class TestTriggerHelpers(object):
    """Tests for trigger helper functions"""

    @mock.patch('helpers.triggerhelpers.glob.glob')
    def test_get_triggers(self, mock_glob):
        """Test getting list of trigger IDs"""
        mock_glob.return_value = [
            'json/public/triggers/trigger1.json',
            'json/public/triggers/trigger2.json',
        ]
        result = get_triggers()
        assert 'trigger1' in result
        assert 'trigger2' in result

    @mock.patch('helpers.triggerhelpers.load_from_json_file')
    def test_get_trigger_config(self, mock_load):
        """Test getting trigger configuration"""
        mock_load.return_value = {'trigger_type': 'Manual'}
        result = get_trigger_config('test_trigger')
        assert result['trigger_type'] == 'Manual'

    @mock.patch('helpers.triggerhelpers.load_from_json_file')
    def test_get_trigger_config_not_found(self, mock_load):
        """Test getting config for non-existent trigger"""
        mock_load.side_effect = IOError('File not found')
        result = get_trigger_config('nonexistent')
        assert result == {}

    @mock.patch('helpers.triggerhelpers.load_from_json_file')
    def test_get_trigger_manual(self, mock_load):
        """Test getting a Manual trigger"""
        mock_load.return_value = {'trigger_type': TriggerType.MANUAL}
        trigger = get_trigger('test_trigger')
        assert trigger.trigger_type == TriggerType.MANUAL

    @mock.patch('helpers.triggerhelpers.load_from_json_file')
    def test_get_trigger_balance(self, mock_load):
        """Test getting a Balance trigger"""
        mock_load.return_value = {'trigger_type': TriggerType.BALANCE}
        trigger = get_trigger('test_trigger')
        assert trigger.trigger_type == TriggerType.BALANCE

    @mock.patch('helpers.triggerhelpers.load_from_json_file')
    def test_get_trigger_received(self, mock_load):
        """Test getting a Received trigger"""
        mock_load.return_value = {'trigger_type': TriggerType.RECEIVED}
        trigger = get_trigger('test_trigger')
        assert trigger.trigger_type == TriggerType.RECEIVED

    @mock.patch('helpers.triggerhelpers.load_from_json_file')
    def test_get_trigger_sent(self, mock_load):
        """Test getting a Sent trigger"""
        mock_load.return_value = {'trigger_type': TriggerType.SENT}
        trigger = get_trigger('test_trigger')
        assert trigger.trigger_type == TriggerType.SENT

    @mock.patch('helpers.triggerhelpers.load_from_json_file')
    def test_get_trigger_block_height(self, mock_load):
        """Test getting a BlockHeight trigger"""
        mock_load.return_value = {'trigger_type': TriggerType.BLOCK_HEIGHT}
        trigger = get_trigger('test_trigger')
        assert trigger.trigger_type == TriggerType.BLOCK_HEIGHT

    @mock.patch('helpers.triggerhelpers.load_from_json_file')
    def test_get_trigger_tx_confirmation(self, mock_load):
        """Test getting a TxConfirmation trigger"""
        mock_load.return_value = {'trigger_type': TriggerType.TX_CONFIRMATION}
        trigger = get_trigger('test_trigger')
        assert trigger.trigger_type == TriggerType.TX_CONFIRMATION

    @mock.patch('helpers.triggerhelpers.load_from_json_file')
    def test_get_trigger_timestamp(self, mock_load):
        """Test getting a Timestamp trigger"""
        mock_load.return_value = {'trigger_type': TriggerType.TIMESTAMP}
        trigger = get_trigger('test_trigger')
        assert trigger.trigger_type == TriggerType.TIMESTAMP

    @mock.patch('helpers.triggerhelpers.load_from_json_file')
    def test_get_trigger_recurring(self, mock_load):
        """Test getting a Recurring trigger"""
        mock_load.return_value = {'trigger_type': TriggerType.RECURRING}
        trigger = get_trigger('test_trigger')
        assert trigger.trigger_type == TriggerType.RECURRING

    @mock.patch('helpers.triggerhelpers.load_from_json_file')
    def test_get_trigger_triggerstatus(self, mock_load):
        """Test getting a TriggerStatus trigger"""
        mock_load.return_value = {'trigger_type': TriggerType.TRIGGERSTATUS}
        trigger = get_trigger('test_trigger')
        assert trigger.trigger_type == TriggerType.TRIGGERSTATUS

    @mock.patch('helpers.triggerhelpers.load_from_json_file')
    def test_get_trigger_deadmansswitch(self, mock_load):
        """Test getting a DeadMansSwitch trigger"""
        mock_load.return_value = {'trigger_type': TriggerType.DEADMANSSWITCH}
        trigger = get_trigger('test_trigger')
        assert trigger.trigger_type == TriggerType.DEADMANSSWITCH

    @mock.patch('helpers.triggerhelpers.load_from_json_file')
    def test_get_trigger_signedmessage(self, mock_load):
        """Test getting a SignedMessage trigger"""
        mock_load.return_value = {'trigger_type': TriggerType.SIGNEDMESSAGE}
        trigger = get_trigger('test_trigger')
        assert trigger.trigger_type == TriggerType.SIGNEDMESSAGE

    @mock.patch('helpers.triggerhelpers.load_from_json_file')
    def test_get_trigger_httpget(self, mock_load):
        """Test getting a HTTPGetRequest trigger"""
        mock_load.return_value = {'trigger_type': TriggerType.HTTPGETREQUEST}
        trigger = get_trigger('test_trigger')
        assert trigger.trigger_type == TriggerType.HTTPGETREQUEST

    @mock.patch('helpers.triggerhelpers.load_from_json_file')
    def test_get_trigger_httppost(self, mock_load):
        """Test getting a HTTPPostRequest trigger"""
        mock_load.return_value = {'trigger_type': TriggerType.HTTPPOSTREQUEST}
        trigger = get_trigger('test_trigger')
        assert trigger.trigger_type == TriggerType.HTTPPOSTREQUEST

    @mock.patch('helpers.triggerhelpers.load_from_json_file')
    def test_get_trigger_httpdelete(self, mock_load):
        """Test getting a HTTPDeleteRequest trigger"""
        mock_load.return_value = {'trigger_type': TriggerType.HTTPDELETEREQUEST}
        trigger = get_trigger('test_trigger')
        assert trigger.trigger_type == TriggerType.HTTPDELETEREQUEST

    @mock.patch('helpers.triggerhelpers.load_from_json_file')
    def test_get_trigger_unknown_type(self, mock_load):
        """Test getting a trigger with unknown type raises error"""
        mock_load.return_value = {'trigger_type': 'UnknownType'}
        with pytest.raises(NotImplementedError):
            get_trigger('test_trigger')

    @mock.patch('helpers.triggerhelpers.load_from_json_file')
    def test_get_trigger_with_type_override(self, mock_load):
        """Test getting a trigger with type override"""
        mock_load.return_value = {'trigger_type': TriggerType.MANUAL}
        trigger = get_trigger('test_trigger', trigger_type=TriggerType.BALANCE)
        assert trigger.trigger_type == TriggerType.BALANCE

    @mock.patch('helpers.triggerhelpers.get_trigger')
    def test_save_trigger(self, mock_get_trigger):
        """Test saving a trigger"""
        mock_trigger = mock.MagicMock()
        mock_get_trigger.return_value = mock_trigger
        
        save_trigger('test_trigger', trigger_type=TriggerType.MANUAL)
        
        mock_trigger.configure.assert_called()
        mock_trigger.save.assert_called_once()

    @mock.patch('helpers.triggerhelpers.get_trigger')
    def test_save_trigger_without_type(self, mock_get_trigger):
        """Test saving a trigger without specifying type"""
        mock_trigger = mock.MagicMock()
        mock_get_trigger.return_value = mock_trigger
        
        save_trigger('test_trigger')
        
        mock_trigger.configure.assert_called()
        mock_trigger.save.assert_called_once()

    @mock.patch('os.path.isfile', return_value=True)
    @mock.patch('os.remove')
    def test_delete_trigger(self, mock_remove, mock_isfile):
        """Test deleting a trigger"""
        result = delete_trigger('test_trigger')
        mock_remove.assert_called_once()
        assert result is None

    @mock.patch('os.path.isfile', return_value=False)
    def test_delete_trigger_not_found(self, mock_isfile):
        """Test deleting a non-existent trigger"""
        result = delete_trigger('nonexistent')
        assert 'error' in result

    @mock.patch('os.path.isfile', return_value=False)
    def test_activate_trigger_not_found(self, mock_isfile):
        """Test activating a non-existent trigger"""
        result = activate_trigger('nonexistent')
        assert 'error' in result

    @mock.patch('os.path.isfile', return_value=True)
    @mock.patch('helpers.triggerhelpers.get_trigger')
    def test_activate_trigger_manual(self, mock_get_trigger, mock_isfile):
        """Test activating a Manual trigger"""
        mock_trigger = mock.MagicMock()
        mock_trigger.trigger_type = TriggerType.MANUAL
        mock_get_trigger.return_value = mock_trigger
        
        activate_trigger('test_trigger')
        mock_trigger.activate.assert_called_once()

    @mock.patch('os.path.isfile', return_value=True)
    @mock.patch('helpers.triggerhelpers.get_trigger')
    def test_activate_trigger_deadmansswitch(self, mock_get_trigger, mock_isfile):
        """Test activating a DeadMansSwitch trigger"""
        mock_trigger = mock.MagicMock()
        mock_trigger.trigger_type = TriggerType.DEADMANSSWITCH
        mock_get_trigger.return_value = mock_trigger
        
        activate_trigger('test_trigger')
        mock_trigger.arm.assert_called_once()

    @mock.patch('os.path.isfile', return_value=True)
    @mock.patch('helpers.triggerhelpers.get_trigger')
    def test_activate_trigger_wrong_type(self, mock_get_trigger, mock_isfile):
        """Test activating a trigger of wrong type"""
        mock_trigger = mock.MagicMock()
        mock_trigger.trigger_type = TriggerType.BALANCE
        mock_get_trigger.return_value = mock_trigger
        
        result = activate_trigger('test_trigger')
        assert 'error' in result

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=['trigger1'])
    @mock.patch('helpers.triggerhelpers.get_trigger')
    def test_check_triggers(self, mock_get_trigger, mock_get_triggers):
        """Test checking triggers"""
        mock_trigger = mock.MagicMock()
        mock_trigger.status = 'Active'
        mock_trigger.conditions_fulfilled.return_value = True
        mock_trigger.self_destruct = None
        mock_get_trigger.return_value = mock_trigger
        
        check_triggers()
        mock_trigger.conditions_fulfilled.assert_called_once()
        mock_trigger.activate.assert_called_once()

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=['trigger1'])
    @mock.patch('helpers.triggerhelpers.get_trigger')
    def test_check_triggers_specific(self, mock_get_trigger, mock_get_triggers):
        """Test checking a specific trigger"""
        mock_trigger = mock.MagicMock()
        mock_trigger.status = 'Active'
        mock_trigger.conditions_fulfilled.return_value = False
        mock_trigger.self_destruct = None
        mock_get_trigger.return_value = mock_trigger
        
        check_triggers(trigger_id='trigger1')
        mock_trigger.conditions_fulfilled.assert_called_once()

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=['trigger1'])
    def test_check_triggers_unknown(self, mock_get_triggers):
        """Test checking an unknown trigger"""
        result = check_triggers(trigger_id='unknown')
        assert 'error' in result

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=['trigger1'])
    @mock.patch('helpers.triggerhelpers.get_trigger')
    def test_http_get_request(self, mock_get_trigger, mock_get_triggers):
        """Test HTTP GET request trigger"""
        mock_trigger = mock.MagicMock()
        mock_trigger.trigger_type = TriggerType.HTTPGETREQUEST
        mock_trigger.status = 'Active'
        mock_get_trigger.return_value = mock_trigger
        
        http_get_request('trigger1', key='value')
        mock_trigger.set_json_data.assert_called_once()
        mock_trigger.activate.assert_called_once()

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=[])
    def test_http_get_request_unknown(self, mock_get_triggers):
        """Test HTTP GET request with unknown trigger"""
        result = http_get_request('unknown')
        assert 'error' in result

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=['trigger1'])
    @mock.patch('helpers.triggerhelpers.get_trigger')
    def test_http_get_request_wrong_type(self, mock_get_trigger, mock_get_triggers):
        """Test HTTP GET request with wrong trigger type"""
        mock_trigger = mock.MagicMock()
        mock_trigger.trigger_type = TriggerType.MANUAL
        mock_get_trigger.return_value = mock_trigger
        
        result = http_get_request('trigger1')
        assert 'error' in result

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=['trigger1'])
    @mock.patch('helpers.triggerhelpers.get_trigger')
    def test_http_post_request(self, mock_get_trigger, mock_get_triggers):
        """Test HTTP POST request trigger"""
        mock_trigger = mock.MagicMock()
        mock_trigger.trigger_type = TriggerType.HTTPPOSTREQUEST
        mock_trigger.status = 'Active'
        mock_get_trigger.return_value = mock_trigger
        
        http_post_request('trigger1', key='value')
        mock_trigger.set_json_data.assert_called_once()
        mock_trigger.activate.assert_called_once()

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=[])
    def test_http_post_request_unknown(self, mock_get_triggers):
        """Test HTTP POST request with unknown trigger"""
        result = http_post_request('unknown')
        assert 'error' in result

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=['trigger1'])
    @mock.patch('helpers.triggerhelpers.get_trigger')
    def test_http_post_request_wrong_type(self, mock_get_trigger, mock_get_triggers):
        """Test HTTP POST request with wrong trigger type"""
        mock_trigger = mock.MagicMock()
        mock_trigger.trigger_type = TriggerType.MANUAL
        mock_get_trigger.return_value = mock_trigger
        
        result = http_post_request('trigger1')
        assert 'error' in result

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=['trigger1'])
    @mock.patch('helpers.triggerhelpers.get_trigger')
    def test_http_delete_request(self, mock_get_trigger, mock_get_triggers):
        """Test HTTP DELETE request trigger"""
        mock_trigger = mock.MagicMock()
        mock_trigger.trigger_type = TriggerType.HTTPDELETEREQUEST
        mock_trigger.status = 'Active'
        mock_get_trigger.return_value = mock_trigger
        
        http_delete_request('trigger1', key='value')
        mock_trigger.set_json_data.assert_called_once()
        mock_trigger.activate.assert_called_once()

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=[])
    def test_http_delete_request_unknown(self, mock_get_triggers):
        """Test HTTP DELETE request with unknown trigger"""
        result = http_delete_request('unknown')
        assert 'error' in result

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=['trigger1'])
    @mock.patch('helpers.triggerhelpers.get_trigger')
    def test_http_delete_request_wrong_type(self, mock_get_trigger, mock_get_triggers):
        """Test HTTP DELETE request with wrong trigger type"""
        mock_trigger = mock.MagicMock()
        mock_trigger.trigger_type = TriggerType.MANUAL
        mock_get_trigger.return_value = mock_trigger
        
        result = http_delete_request('trigger1')
        assert 'error' in result

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=['trigger1'])
    @mock.patch('helpers.triggerhelpers.get_trigger')
    def test_signed_message_request(self, mock_get_trigger, mock_get_triggers):
        """Test SignedMessage request trigger"""
        mock_trigger = mock.MagicMock()
        mock_trigger.trigger_type = TriggerType.SIGNEDMESSAGE
        mock_trigger.status = 'Active'
        mock_get_trigger.return_value = mock_trigger
        
        signed_message_request('trigger1', message='test', message_address='addr', message_signature='sig')
        mock_trigger.activate.assert_called_once()

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=[])
    def test_signed_message_request_unknown(self, mock_get_triggers):
        """Test SignedMessage request with unknown trigger"""
        result = signed_message_request('unknown')
        assert 'error' in result

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=['trigger1'])
    @mock.patch('helpers.triggerhelpers.get_trigger')
    def test_signed_message_request_wrong_type(self, mock_get_trigger, mock_get_triggers):
        """Test SignedMessage request with wrong trigger type"""
        mock_trigger = mock.MagicMock()
        mock_trigger.trigger_type = TriggerType.MANUAL
        mock_get_trigger.return_value = mock_trigger
        
        result = signed_message_request('trigger1')
        assert 'error' in result

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=['trigger1'])
    @mock.patch('helpers.triggerhelpers.get_trigger')
    def test_file_download(self, mock_get_trigger, mock_get_triggers):
        """Test file download trigger"""
        mock_trigger = mock.MagicMock()
        mock_trigger.trigger_type = TriggerType.HTTPGETREQUEST
        mock_trigger.status = 'Active'
        mock_get_trigger.return_value = mock_trigger
        
        file_download('trigger1', key='value')
        mock_trigger.set_json_data.assert_called_once()
        mock_trigger.activate.assert_called_once()

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=[])
    def test_file_download_unknown(self, mock_get_triggers):
        """Test file download with unknown trigger"""
        result = file_download('unknown')
        assert 'error' in result

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=['trigger1'])
    @mock.patch('helpers.triggerhelpers.get_trigger')
    def test_file_download_wrong_type(self, mock_get_trigger, mock_get_triggers):
        """Test file download with wrong trigger type"""
        mock_trigger = mock.MagicMock()
        mock_trigger.trigger_type = TriggerType.MANUAL
        mock_get_trigger.return_value = mock_trigger
        
        result = file_download('trigger1')
        assert 'error' in result


class TestVerifySignedMessage(object):
    """Tests for verify_signed_message function"""

    def test_verify_signed_message_missing_keys(self):
        """Test verify_signed_message with missing keys"""
        result = verify_signed_message('trigger1', address='addr')
        assert 'error' in result
        assert 'required keys' in result['error']

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=[])
    def test_verify_signed_message_unknown_trigger(self, mock_get_triggers):
        """Test verify_signed_message with unknown trigger"""
        result = verify_signed_message('unknown', address='addr', message='msg', signature='sig')
        assert 'error' in result

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=['trigger1'])
    @mock.patch('helpers.triggerhelpers.get_trigger')
    def test_verify_signed_message_wrong_type(self, mock_get_trigger, mock_get_triggers):
        """Test verify_signed_message with wrong trigger type"""
        mock_trigger = mock.MagicMock()
        mock_trigger.trigger_type = TriggerType.MANUAL
        mock_get_trigger.return_value = mock_trigger
        
        result = verify_signed_message('trigger1', address='addr', message='msg', signature='sig')
        assert 'error' in result

    @mock.patch('helpers.triggerhelpers.get_triggers', return_value=['trigger1'])
    @mock.patch('helpers.triggerhelpers.get_trigger')
    def test_verify_signed_message_wrong_address(self, mock_get_trigger, mock_get_triggers):
        """Test verify_signed_message with wrong address"""
        mock_trigger = mock.MagicMock()
        mock_trigger.trigger_type = TriggerType.SIGNEDMESSAGE
        mock_trigger.address = 'expected_addr'
        mock_trigger.id = 'trigger1'
        mock_get_trigger.return_value = mock_trigger
        
        result = verify_signed_message('trigger1', address='wrong_addr', message='msg', signature='sig')
        assert 'error' in result


class TestSignMessage(object):
    """Tests for sign_message function"""

    def test_sign_message_missing_keys(self):
        """Test sign_message with missing keys"""
        result = sign_message(address='addr')
        assert result['success'] == False
        assert 'required keys' in result['error']

    @mock.patch('helpers.triggerhelpers.valid_address', return_value=False)
    def test_sign_message_invalid_address(self, mock_valid):
        """Test sign_message with invalid address"""
        result = sign_message(address='invalid', message='test')
        assert result['success'] == False
        assert 'Invalid address' in result['error']

    @mock.patch('helpers.triggerhelpers.valid_address', return_value=True)
    def test_sign_message_too_long(self, mock_valid):
        """Test sign_message with message too long"""
        result = sign_message(address='addr', message='x' * 300)
        assert result['success'] == False
        assert 'too long' in result['error']

    @mock.patch('helpers.triggerhelpers.valid_address', return_value=True)
    @mock.patch('helpers.triggerhelpers.find_address_in_wallet', return_value=(None, None))
    @mock.patch('helpers.triggerhelpers.find_single_address_in_wallet', return_value=None)
    def test_sign_message_address_not_found(self, mock_find_single, mock_find, mock_valid):
        """Test sign_message when address not in wallet"""
        result = sign_message(address='addr', message='test')
        assert result['success'] == False
        assert 'not found in hot wallet' in result['error']

    @mock.patch('helpers.triggerhelpers.valid_address', return_value=True)
    @mock.patch('helpers.triggerhelpers.find_address_in_wallet', return_value=(0, 0))
    @mock.patch('helpers.triggerhelpers.get_private_key_from_wallet', return_value={'addr': 'privkey'})
    @mock.patch('helpers.triggerhelpers.sign_and_verify', return_value='signature')
    def test_sign_message_success(self, mock_sign, mock_get_key, mock_find, mock_valid):
        """Test successful sign_message"""
        result = sign_message(address='addr', message='test')
        assert result['success'] == True
        assert result['signature'] == 'signature'

    @mock.patch('helpers.triggerhelpers.valid_address', return_value=True)
    @mock.patch('helpers.triggerhelpers.find_address_in_wallet', return_value=(None, None))
    @mock.patch('helpers.triggerhelpers.find_single_address_in_wallet', return_value='privkey')
    @mock.patch('helpers.triggerhelpers.sign_and_verify', return_value='signature')
    def test_sign_message_single_address(self, mock_sign, mock_find_single, mock_find, mock_valid):
        """Test sign_message with single address wallet"""
        result = sign_message(address='addr', message='test')
        assert result['success'] == True

    @mock.patch('helpers.triggerhelpers.valid_address', return_value=True)
    @mock.patch('helpers.triggerhelpers.find_address_in_wallet', return_value=(0, 0))
    @mock.patch('helpers.triggerhelpers.get_private_key_from_wallet', return_value={'addr': 'privkey'})
    @mock.patch('helpers.triggerhelpers.sign_and_verify', side_effect=Exception('Sign error'))
    def test_sign_message_error(self, mock_sign, mock_get_key, mock_find, mock_valid):
        """Test sign_message when signing fails"""
        result = sign_message(address='addr', message='test')
        assert result['success'] == False
        assert 'Unable to sign' in result['error']
