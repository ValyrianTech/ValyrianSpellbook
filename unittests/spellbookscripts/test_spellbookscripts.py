#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the spellbookscripts package: SpellbookScript base class, Echo, and Template.
"""
import hashlib

import mock
import pytest
import simplejson

from spellbookscripts.spellbookscript import SpellbookScript
from spellbookscripts.Echo import Echo
from spellbookscripts.Template import Template


class ConcreteScript(SpellbookScript):
    """Concrete implementation for testing the abstract base class."""

    def run(self):
        self.http_response = {'ran': True}

    def cleanup(self):
        pass


class TestSpellbookScriptInit:
    """Tests for SpellbookScript.__init__"""

    def test_default_init(self):
        script = ConcreteScript()
        assert script.address is None
        assert script.message is None
        assert script.signature is None
        assert script.trigger_id is None
        assert script.trigger_type is None
        assert script.script is None
        assert script.data is None
        assert script.triggered is None
        assert script.multi is None
        assert script.description is None
        assert script.creator_name is None
        assert script.creator_email is None
        assert script.youtube is None
        assert script.status is None
        assert script.visibility is None
        assert script.created is None
        assert script.actions is None
        assert script.json is None
        assert script.ipfs_hash is None
        assert script.ipfs_object is None
        assert script.text is None
        assert script.sha256_hash is None
        assert script.http_response is None
        assert script.new_actions == []

    def test_init_with_kwargs(self):
        script = ConcreteScript(
            address=None,
            message=None,
            signature='sig',
            trigger_id='tid',
            trigger_type='Manual',
            script='Echo.py',
            data={'key': 'value'},
            triggered=3,
            multi=True,
            description='desc',
            creator_name='Alice',
            creator_email='alice@example.com',
            youtube='https://youtube.com',
            status='Active',
            visibility='public',
            created='2024-01-01',
            actions=['a1', 'a2'],
        )
        assert script.signature == 'sig'
        assert script.trigger_id == 'tid'
        assert script.trigger_type == 'Manual'
        assert script.script == 'Echo.py'
        assert script.data == {'key': 'value'}
        assert script.triggered == 3
        assert script.multi is True
        assert script.description == 'desc'
        assert script.creator_name == 'Alice'
        assert script.creator_email == 'alice@example.com'
        assert script.youtube == 'https://youtube.com'
        assert script.status == 'Active'
        assert script.visibility == 'public'
        assert script.created == '2024-01-01'
        assert script.actions == ['a1', 'a2']

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_init_with_valid_address(self, _mock_va):
        script = ConcreteScript(address='1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2')
        assert script.address == '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2'

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=False)
    def test_init_with_invalid_address_raises(self, _mock_va):
        with pytest.raises(Exception, match='is not a valid address'):
            ConcreteScript(address='invalidaddress')

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_init_with_message_calls_process_message(self, _mock_va):
        script = ConcreteScript(message='hello')
        assert script.text == 'hello'

    def test_init_without_message_does_not_process(self):
        script = ConcreteScript()
        assert script.text is None
        assert script.json is None
        assert script.ipfs_hash is None


class TestProcessMessage:
    """Tests for process_message routing"""

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_ipfs_message(self, _mock_va):
        with mock.patch('spellbookscripts.spellbookscript.get_json', return_value={'key': 'val'}):
            script = ConcreteScript(message='/ipfs/QmHash123')
        assert script.ipfs_hash == 'QmHash123'
        assert script.json == {'key': 'val'}

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_sha256_message_with_matching_data(self, _mock_va):
        data = {'key': 'value'}
        control_hash = hashlib.sha256(
            simplejson.dumps(data, sort_keys=True, indent=2, ensure_ascii=False).encode('utf-8')
        ).hexdigest()
        script = ConcreteScript(message='/sha256/' + control_hash, data=data)
        assert script.sha256_hash == control_hash
        assert script.json == data

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_sha256_message_without_data(self, _mock_va):
        script = ConcreteScript(message='/sha256/abc123')
        assert script.sha256_hash == 'abc123'
        assert script.json is None

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_sha256_message_with_mismatched_data(self, _mock_va):
        script = ConcreteScript(message='/sha256/wronghash', data={'key': 'value'})
        assert script.sha256_hash == 'wronghash'
        assert script.json is None

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_sha256_message_with_string_data(self, _mock_va):
        data = {'key': 'value'}
        data_str = simplejson.dumps(data)
        control_hash = hashlib.sha256(
            simplejson.dumps(data, sort_keys=True, indent=2, ensure_ascii=False).encode('utf-8')
        ).hexdigest()
        script = ConcreteScript(message='/sha256/' + control_hash, data=data_str)
        assert script.json == data

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_sha256_message_with_invalid_json_string_data(self, _mock_va):
        script = ConcreteScript(message='/sha256/somehash', data='not json')
        assert script.json is None

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_json_message(self, _mock_va):
        json_str = '{"key": "value"}'
        script = ConcreteScript(message=json_str)
        assert script.json == {'key': 'value'}
        assert script.text is None

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_plain_text_message(self, _mock_va):
        script = ConcreteScript(message='hello world')
        assert script.text == 'hello world'
        assert script.json is None


class TestProcessIpfsHash:
    """Tests for process_ipfs_hash"""

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_process_ipfs_hash_with_dict(self, _mock_va):
        with mock.patch('spellbookscripts.spellbookscript.get_json', return_value={'key': 'val'}):
            script = ConcreteScript(message='/ipfs/QmHash')
        assert script.json == {'key': 'val'}

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_process_ipfs_hash_with_json_string(self, _mock_va):
        with mock.patch('spellbookscripts.spellbookscript.get_json', return_value='{"key": "val"}'):
            script = ConcreteScript(message='/ipfs/QmHash')
        assert script.json == {'key': 'val'}

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_process_ipfs_hash_with_invalid_data_type(self, _mock_va):
        with mock.patch('spellbookscripts.spellbookscript.get_json', return_value=12345):
            script = ConcreteScript(message='/ipfs/QmHash')
        assert script.json is None

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_process_ipfs_hash_get_json_raises(self, _mock_va):
        with mock.patch('spellbookscripts.spellbookscript.get_json', side_effect=Exception('network error')):
            script = ConcreteScript(message='/ipfs/QmHash')
        assert script.json is None

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_process_ipfs_hash_with_matching_ipfs_object(self, _mock_va):
        obj = {'key': 'val'}
        with mock.patch('spellbookscripts.spellbookscript.add_json', return_value='/ipfs/QmMatch'):
            with mock.patch('spellbookscripts.spellbookscript.get_json', return_value=obj):
                script = ConcreteScript(message='/ipfs/QmMatch', ipfs_object=obj)
        assert script.json == obj

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_process_ipfs_hash_with_mismatched_ipfs_object(self, _mock_va):
        obj = {'key': 'val'}
        with mock.patch('spellbookscripts.spellbookscript.add_json', return_value='/ipfs/QmDifferent'):
            with mock.patch('spellbookscripts.spellbookscript.get_json') as mock_get:
                script = ConcreteScript(message='/ipfs/QmMatch', ipfs_object=obj)
        assert script.json is None
        mock_get.assert_not_called()


class TestProcessSha256Hash:
    """Tests for process_sha256_hash"""

    def test_sha256_no_data(self):
        script = ConcreteScript()
        result = script.process_sha256_hash('somehash')
        assert result is False

    def test_sha256_matching_hash(self):
        data = {'a': 1, 'b': 2}
        control_hash = hashlib.sha256(
            simplejson.dumps(data, sort_keys=True, indent=2, ensure_ascii=False).encode('utf-8')
        ).hexdigest()
        script = ConcreteScript(data=data)
        result = script.process_sha256_hash(control_hash)
        assert result is True
        assert script.json == data

    def test_sha256_mismatched_hash(self):
        script = ConcreteScript(data={'a': 1})
        result = script.process_sha256_hash('wronghash')
        assert result is False
        assert script.json is None

    def test_sha256_with_string_data_valid_json(self):
        data = {'a': 1}
        data_str = simplejson.dumps(data)
        control_hash = hashlib.sha256(
            simplejson.dumps(data, sort_keys=True, indent=2, ensure_ascii=False).encode('utf-8')
        ).hexdigest()
        script = ConcreteScript(data=data_str)
        result = script.process_sha256_hash(control_hash)
        assert result is True
        assert script.json == data

    def test_sha256_with_string_data_invalid_json(self):
        script = ConcreteScript(data='not json')
        result = script.process_sha256_hash('somehash')
        assert result is False


class TestProcessJsonData:
    """Tests for process_json_data"""

    def test_process_json_data(self):
        script = ConcreteScript()
        script.process_json_data({'key': 'val'})
        assert script.json == {'key': 'val'}


class TestProcessText:
    """Tests for process_text"""

    def test_process_text(self):
        script = ConcreteScript()
        script.process_text('hello')
        assert script.text == 'hello'


class TestAttachAction:
    """Tests for attach_action"""

    def test_attach_action(self):
        script = ConcreteScript()
        assert script.new_actions == []
        script.attach_action('action1')
        assert script.new_actions == ['action1']
        script.attach_action('action2')
        assert script.new_actions == ['action1', 'action2']


class TestExitWithError:
    """Tests for exit_with_error"""

    def test_exit_with_error(self):
        script = ConcreteScript()
        assert script.http_response is None
        script.exit_with_error('something went wrong')
        assert script.http_response == {'error': 'something went wrong'}


class TestEcho:
    """Tests for the Echo script"""

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_echo_run_with_data(self, _mock_va):
        echo = Echo(data={'echo': 'test'})
        echo.run()
        assert echo.http_response == {'echo': 'test'}

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_echo_run_without_data(self, _mock_va):
        echo = Echo()
        echo.run()
        assert echo.http_response is None

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_echo_cleanup(self, _mock_va):
        echo = Echo()
        echo.cleanup()

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_echo_init_with_kwargs(self, _mock_va):
        echo = Echo(trigger_id='tid', description='echo script')
        assert echo.trigger_id == 'tid'
        assert echo.description == 'echo script'


class TestTemplate:
    """Tests for the Template script"""

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_template_run_without_json(self, _mock_va):
        tmpl = Template()
        tmpl.run()
        assert tmpl.http_response == {'status': 'success'}

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_template_run_with_json_no_address(self, _mock_va):
        tmpl = Template(message='{"key": "value"}')
        tmpl.run()
        assert tmpl.http_response is None

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_template_run_with_json_containing_address(self, _mock_va):
        tmpl = Template(message='{"address": "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2"}')
        tmpl.run()
        assert tmpl.http_response == {'status': 'success'}

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    def test_template_cleanup(self, _mock_va):
        tmpl = Template()
        tmpl.cleanup()

    @mock.patch('spellbookscripts.spellbookscript.valid_address', return_value=True)
    @mock.patch('spellbookscripts.Template.get_action')
    @mock.patch('spellbookscripts.Template.get_trigger')
    def test_template_run_with_action_and_trigger(self, _mock_gt, _mock_ga, _mock_va):
        mock_action = mock.MagicMock()
        _mock_ga.return_value = mock_action
        mock_trigger = mock.MagicMock()
        _mock_gt.return_value = mock_trigger

        tmpl = Template()
        tmpl.run()

        _mock_ga.assert_called_once()
        _mock_gt.assert_called_once()
        mock_action.save.assert_called_once()
        mock_trigger.save.assert_called_once()
        assert tmpl.http_response == {'status': 'success'}
