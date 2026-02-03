#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock
import time
from datetime import datetime

from trigger.trigger import Trigger, TRIGGERS_DIR
from trigger.triggertype import TriggerType


class ConcreteTrigger(Trigger):
    """Concrete implementation of Trigger for testing the abstract base class"""

    def conditions_fulfilled(self):
        return True


class TestTriggerType(object):
    """Tests for TriggerType constants"""

    def test_trigger_type_constants(self):
        assert TriggerType.MANUAL == 'Manual'
        assert TriggerType.BALANCE == 'Balance'
        assert TriggerType.RECEIVED == 'Received'
        assert TriggerType.SENT == 'Sent'
        assert TriggerType.BLOCK_HEIGHT == 'Block_height'
        assert TriggerType.TX_CONFIRMATION == 'Tx_confirmation'
        assert TriggerType.TIMESTAMP == 'Timestamp'
        assert TriggerType.RECURRING == 'Recurring'
        assert TriggerType.TRIGGERSTATUS == 'TriggerStatus'
        assert TriggerType.DEADMANSSWITCH == 'DeadMansSwitch'
        assert TriggerType.SIGNEDMESSAGE == 'SignedMessage'
        assert TriggerType.HTTPGETREQUEST == 'HTTPGetRequest'
        assert TriggerType.HTTPPOSTREQUEST == 'HTTPPostRequest'
        assert TriggerType.HTTPDELETEREQUEST == 'HTTPDeleteRequest'
        assert TriggerType.HTTPOPTIONSREQUEST == 'HTTPOptionsRequest'


class TestTrigger(object):
    """Tests for the Trigger base class"""

    def test_trigger_init(self):
        trigger = ConcreteTrigger('test_trigger_id')
        assert trigger.id == 'test_trigger_id'
        assert trigger.trigger_type is None
        assert trigger.script is None
        assert trigger.triggered == 0
        assert trigger.multi == False
        assert trigger.actions == []

    def test_trigger_configure_created_timestamp(self):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(created=1609459200)
        assert trigger.created == datetime.fromtimestamp(1609459200)

    def test_trigger_configure_created_default(self):
        trigger = ConcreteTrigger('test_trigger_id')
        before = datetime.now()
        trigger.configure()
        after = datetime.now()
        assert before <= trigger.created <= after

    @mock.patch('trigger.trigger.valid_trigger_type', return_value=True)
    def test_trigger_configure_trigger_type(self, mock_valid):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(trigger_type='Manual')
        assert trigger.trigger_type == 'Manual'

    @mock.patch('trigger.trigger.valid_script', return_value=True)
    def test_trigger_configure_script(self, mock_valid):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(script='Echo.py')
        assert trigger.script == 'Echo.py'

    def test_trigger_configure_data(self):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(data={'key': 'value'})
        assert trigger.data == {'key': 'value'}

    def test_trigger_configure_multi(self):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(multi=True)
        assert trigger.multi == True

    @mock.patch('trigger.trigger.valid_status', return_value=True)
    def test_trigger_configure_status(self, mock_valid):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(status='Active')
        assert trigger.status == 'Active'

    def test_trigger_configure_reset(self):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.triggered = 5
        trigger.status = 'Failed'
        trigger.configure(reset=True)
        assert trigger.triggered == 0
        assert trigger.status == 'Active'

    @mock.patch('trigger.trigger.valid_amount', return_value=True)
    def test_trigger_configure_triggered(self, mock_valid):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(triggered=3)
        assert trigger.triggered == 3

    @mock.patch('trigger.trigger.valid_description', return_value=True)
    def test_trigger_configure_description(self, mock_valid):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(description='Test description')
        assert trigger.description == 'Test description'

    @mock.patch('trigger.trigger.valid_creator', return_value=True)
    def test_trigger_configure_creator_name(self, mock_valid):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(creator_name='Test Creator')
        assert trigger.creator_name == 'Test Creator'

    @mock.patch('trigger.trigger.valid_email', return_value=True)
    def test_trigger_configure_creator_email(self, mock_valid):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(creator_email='test@example.com')
        assert trigger.creator_email == 'test@example.com'

    @mock.patch('trigger.trigger.valid_youtube_id', return_value=True)
    def test_trigger_configure_youtube(self, mock_valid):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(youtube='dQw4w9WgXcQ')
        assert trigger.youtube == 'dQw4w9WgXcQ'

    @mock.patch('trigger.trigger.valid_visibility', return_value=True)
    def test_trigger_configure_visibility(self, mock_valid):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(visibility='Public')
        assert trigger.visibility == 'Public'

    @mock.patch('trigger.trigger.get_actions', return_value={'action1': {}})
    @mock.patch('trigger.trigger.valid_actions', return_value=True)
    def test_trigger_configure_actions(self, mock_valid, mock_get):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(actions=['action1'])
        assert trigger.actions == ['action1']

    @mock.patch('trigger.trigger.valid_timestamp', return_value=True)
    def test_trigger_configure_self_destruct(self, mock_valid):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(self_destruct=1609459200)
        assert trigger.self_destruct == 1609459200

    def test_trigger_configure_destruct_actions(self):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(destruct_actions=True)
        assert trigger.destruct_actions == True

    def test_trigger_json_encodable(self):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(created=1609459200)
        trigger.trigger_type = 'Manual'
        result = trigger.json_encodable()
        assert result['trigger_id'] == 'test_trigger_id'
        assert result['trigger_type'] == 'Manual'
        assert result['created'] == 1609459200

    @mock.patch('trigger.trigger.save_to_json_file')
    def test_trigger_save(self, mock_save):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(created=1609459200)
        trigger.save()
        mock_save.assert_called_once()

    def test_trigger_get_script_variables(self):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(created=1609459200)
        result = trigger.get_script_variables()
        assert result == trigger.json_encodable()

    def test_trigger_load_script_none(self):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.script = None
        result = trigger.load_script()
        assert result is None

    @mock.patch('trigger.trigger.valid_script', return_value=False)
    def test_trigger_load_script_invalid(self, mock_valid):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.script = 'invalid.py'
        result = trigger.load_script()
        assert result is None

    @mock.patch('trigger.trigger.save_to_json_file')
    @mock.patch('trigger.trigger.get_action')
    @mock.patch('trigger.trigger.get_actions', return_value={'action1': {}})
    def test_trigger_activate_success(self, mock_get_actions, mock_get_action, mock_save):
        mock_action = mock.MagicMock()
        mock_action.run.return_value = True
        mock_get_action.return_value = mock_action
        
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(created=1609459200)
        trigger.actions = ['action1']
        trigger.activate()
        
        assert trigger.triggered == 1
        assert trigger.status == 'Succeeded'
        mock_action.run.assert_called_once()

    @mock.patch('trigger.trigger.save_to_json_file')
    @mock.patch('trigger.trigger.get_action')
    @mock.patch('trigger.trigger.get_actions', return_value={'action1': {}})
    def test_trigger_activate_failure(self, mock_get_actions, mock_get_action, mock_save):
        mock_action = mock.MagicMock()
        mock_action.run.return_value = False
        mock_get_action.return_value = mock_action
        
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(created=1609459200)
        trigger.actions = ['action1']
        trigger.activate()
        
        assert trigger.triggered == 1
        assert trigger.status == 'Failed'

    @mock.patch('trigger.trigger.save_to_json_file')
    @mock.patch('trigger.trigger.get_action')
    @mock.patch('trigger.trigger.get_actions', return_value={'action1': {}})
    def test_trigger_activate_multi_success(self, mock_get_actions, mock_get_action, mock_save):
        mock_action = mock.MagicMock()
        mock_action.run.return_value = True
        mock_get_action.return_value = mock_action
        
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(created=1609459200)
        trigger.actions = ['action1']
        trigger.multi = True
        trigger.activate()
        
        assert trigger.triggered == 1
        assert trigger.status == 'Active'

    @mock.patch('trigger.trigger.get_actions', return_value={})
    def test_trigger_activate_unknown_action(self, mock_get_actions):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(created=1609459200)
        trigger.actions = ['unknown_action']
        result = trigger.activate()
        assert result is None

    @mock.patch('trigger.trigger.get_actions', return_value={'action1': {}})
    @mock.patch('trigger.trigger.valid_actions', return_value=True)
    def test_trigger_configure_actions_with_warning(self, mock_valid, mock_get):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(actions=['action1', 'unknown_action'])
        assert trigger.actions == ['action1', 'unknown_action']

    @mock.patch('trigger.trigger.save_to_json_file')
    @mock.patch('trigger.trigger.get_action')
    @mock.patch('trigger.trigger.get_actions', return_value={'action1': {}})
    def test_trigger_activate_with_script(self, mock_get_actions, mock_get_action, mock_save):
        mock_action = mock.MagicMock()
        mock_action.run.return_value = True
        mock_get_action.return_value = mock_action
        
        mock_script = mock.MagicMock()
        mock_script.new_actions = ['action1']
        mock_script.http_response = {'status': 'ok'}
        
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(created=1609459200)
        trigger.actions = []
        
        with mock.patch.object(trigger, 'load_script', return_value=mock_script):
            result = trigger.activate()
        
        mock_script.run.assert_called_once()
        mock_script.cleanup.assert_called_once()
        assert result == {'status': 'ok'}

    @mock.patch('trigger.trigger.valid_script', return_value=True)
    @mock.patch('os.path.isfile', return_value=False)
    def test_trigger_load_script_not_found(self, mock_isfile, mock_valid):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.script = 'nonexistent.py'
        result = trigger.load_script()
        assert result is None

    @mock.patch('trigger.trigger.valid_script', return_value=True)
    @mock.patch('os.path.isfile', return_value=True)
    @mock.patch('importlib.import_module')
    @mock.patch('platform.system', return_value='Linux')
    def test_trigger_load_script_success(self, mock_platform, mock_import, mock_isfile, mock_valid):
        mock_script_class = mock.MagicMock()
        mock_script_instance = mock.MagicMock()
        mock_script_class.return_value = mock_script_instance
        mock_module = mock.MagicMock()
        setattr(mock_module, 'testscript', mock_script_class)
        mock_import.return_value = mock_module
        
        # Mock isinstance to return True for SpellbookScript check
        with mock.patch('trigger.trigger.isinstance', return_value=True):
            trigger = ConcreteTrigger('test_trigger_id')
            trigger.configure(created=1609459200)
            trigger.script = 'testscript.py'
            result = trigger.load_script()
        
        mock_import.assert_called_once()

    @mock.patch('trigger.trigger.valid_script', return_value=True)
    @mock.patch('os.path.isfile', return_value=True)
    @mock.patch('importlib.import_module', side_effect=Exception('Import error'))
    @mock.patch('platform.system', return_value='Linux')
    def test_trigger_load_script_import_error(self, mock_platform, mock_import, mock_isfile, mock_valid):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.script = 'testscript.py'
        result = trigger.load_script()
        assert result is None

    @mock.patch('trigger.trigger.valid_script', return_value=True)
    @mock.patch('os.path.isfile', return_value=True)
    @mock.patch('platform.system', return_value='Windows')
    def test_trigger_load_script_windows(self, mock_platform, mock_isfile, mock_valid):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.script = 'subdir\\testscript.py'
        
        with mock.patch('importlib.import_module') as mock_import:
            mock_script_class = mock.MagicMock()
            mock_script_instance = mock.MagicMock()
            mock_script_class.return_value = mock_script_instance
            mock_module = mock.MagicMock()
            setattr(mock_module, 'testscript', mock_script_class)
            mock_import.return_value = mock_module
            
            with mock.patch('trigger.trigger.isinstance', return_value=True):
                trigger.configure(created=1609459200)
                result = trigger.load_script()
            
            # Verify Windows path handling
            call_args = mock_import.call_args[0][0]
            assert '.' in call_args

    @mock.patch('trigger.trigger.valid_script', return_value=True)
    @mock.patch('os.path.isfile', return_value=True)
    @mock.patch('platform.system', return_value='Darwin')
    def test_trigger_load_script_unsupported_platform(self, mock_platform, mock_isfile, mock_valid):
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.script = 'testscript.py'
        
        with pytest.raises(NotImplementedError):
            trigger.load_script()

    @mock.patch('trigger.trigger.valid_script', return_value=True)
    @mock.patch('os.path.isfile', return_value=True)
    @mock.patch('importlib.import_module')
    @mock.patch('platform.system', return_value='Linux')
    def test_trigger_load_script_invalid_script_type(self, mock_platform, mock_import, mock_isfile, mock_valid):
        mock_script_class = mock.MagicMock()
        mock_script_instance = mock.MagicMock()
        mock_script_class.return_value = mock_script_instance
        mock_module = mock.MagicMock()
        setattr(mock_module, 'testscript', mock_script_class)
        mock_import.return_value = mock_module
        
        trigger = ConcreteTrigger('test_trigger_id')
        trigger.configure(created=1609459200)
        trigger.script = 'testscript.py'
        result = trigger.load_script()
        assert result is None
