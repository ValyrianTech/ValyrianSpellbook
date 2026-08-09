#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for spellbook.py — the Valyrian Spellbook CLI interface.

spellbook.py runs argparse and command dispatch at module level, so we patch
sys.argv before importing to prevent it from consuming pytest arguments.
"""
import argparse
import importlib.util
import os
import sys

import mock
import pytest

# spellbook.py runs argparse and command dispatch at module level.
# The root __init__.py makes the directory a "spellbook" package, shadowing
# spellbook.py, so we load the file directly via importlib.
_SPELLBOOK_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'spellbook.py')

if 'spellbook' in sys.modules:
    del sys.modules['spellbook']

with mock.patch('sys.argv', ['spellbook.py']):
    _spec = importlib.util.spec_from_file_location('spellbook', _SPELLBOOK_PATH)
    assert _spec is not None
    assert _spec.loader is not None
    spellbook = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(spellbook)
    sys.modules['spellbook'] = spellbook

add_authentication_headers = spellbook.add_authentication_headers
specify_explorer = spellbook.specify_explorer
do_get_request = spellbook.do_get_request
do_post_request = spellbook.do_post_request
do_delete_request = spellbook.do_delete_request
get_llms = spellbook.get_llms
get_llm_config = spellbook.get_llm_config
save_llm_config = spellbook.save_llm_config
delete_llm = spellbook.delete_llm
get_explorers = spellbook.get_explorers
get_explorer_config = spellbook.get_explorer_config
save_explorer = spellbook.save_explorer
delete_explorer = spellbook.delete_explorer
get_latest_block = spellbook.get_latest_block
get_block = spellbook.get_block
get_prime_input_address = spellbook.get_prime_input_address
get_transaction = spellbook.get_transaction
get_transactions = spellbook.get_transactions
get_balance = spellbook.get_balance
get_utxos = spellbook.get_utxos
get_sil = spellbook.get_sil
get_profile = spellbook.get_profile
get_sul = spellbook.get_sul
get_lal = spellbook.get_lal
get_lbl = spellbook.get_lbl
get_lrl = spellbook.get_lrl
get_lsl = spellbook.get_lsl
get_random_address = spellbook.get_random_address
get_triggers = spellbook.get_triggers
get_trigger = spellbook.get_trigger
save_trigger = spellbook.save_trigger
delete_trigger = spellbook.delete_trigger
activate_trigger = spellbook.activate_trigger
send_signed_message = spellbook.send_signed_message
sign_message = spellbook.sign_message
check_triggers = spellbook.check_triggers
get_actions = spellbook.get_actions
get_action = spellbook.get_action
save_action = spellbook.save_action
delete_action = spellbook.delete_action
run_action = spellbook.run_action
get_reveal = spellbook.get_reveal
get_logs = spellbook.get_logs
get_hivemind = spellbook.get_hivemind


VALID_SECRET = 'test'  # length must be multiple of 4 for signature()


def make_args(**kwargs):
    """Create an argparse.Namespace with the given attributes."""
    return argparse.Namespace(**kwargs)


def get_call_url(mock_call):
    """Extract URL from a mock call, handling both positional and keyword args."""
    args, kwargs = mock_call.call_args
    return kwargs.get('url', args[0] if args else None)


def get_call_data(mock_call):
    """Extract data from a mock call, handling both positional and keyword args."""
    args, kwargs = mock_call.call_args
    return kwargs.get('data', {})


class TestAddAuthenticationHeaders(object):

    def test_with_default_headers(self):
        spellbook.args = make_args(api_key='test_key', api_secret=VALID_SECRET)
        headers = add_authentication_headers(data={'test': 1})
        assert headers['API_Key'] == 'test_key'
        assert 'API_Sign' in headers
        assert 'API_Nonce' in headers
        assert headers['Content-Type'] == 'application/json'

    def test_with_custom_headers(self):
        spellbook.args = make_args(api_key='mykey', api_secret=VALID_SECRET)
        custom = {'Custom': 'header'}
        headers = add_authentication_headers(headers=custom, data={'x': 1})
        assert headers['API_Key'] == 'mykey'
        assert headers['Custom'] == 'header'
        assert 'API_Sign' in headers

    def test_with_no_data(self):
        spellbook.args = make_args(api_key='k', api_secret=VALID_SECRET)
        headers = add_authentication_headers(data=None)
        assert headers['API_Key'] == 'k'
        assert 'API_Sign' in headers


class TestSpecifyExplorer(object):

    def test_with_explorer(self):
        spellbook.args = make_args(explorer='blockstream')
        result = specify_explorer('http://localhost/blocks/latest')
        assert 'explorer=blockstream' in result

    def test_without_explorer(self):
        spellbook.args = make_args(explorer=None)
        url = 'http://localhost/blocks/latest'
        result = specify_explorer(url)
        assert result == url

    def test_with_existing_query_param(self):
        spellbook.args = make_args(explorer='blockstream')
        result = specify_explorer('http://localhost/utxos?confirmations=5')
        assert 'explorer=blockstream' in result
        assert '?confirmations=5' in result
        assert '&explorer=blockstream' in result

    def test_no_explorer_attribute(self):
        spellbook.args = make_args()
        url = 'http://localhost/blocks/latest'
        result = specify_explorer(url)
        assert result == url


class TestDoGetRequest(object):

    @mock.patch('spellbook.requests')
    @mock.patch('spellbook.print')
    def test_basic_get(self, mock_print, mock_requests):
        mock_requests.get.return_value.text = 'response'
        do_get_request('http://localhost/test')
        mock_requests.get.assert_called_once()
        args, kwargs = mock_requests.get.call_args
        assert args[0] == 'http://localhost/test'
        assert kwargs['headers'] is None

    @mock.patch('spellbook.requests')
    @mock.patch('spellbook.print')
    def test_authenticated_get(self, mock_print, mock_requests):
        spellbook.args = make_args(api_key='k', api_secret=VALID_SECRET, explorer=None)
        mock_requests.get.return_value.text = 'response'
        do_get_request('http://localhost/test', authenticate=True)
        args, kwargs = mock_requests.get.call_args
        assert kwargs['headers'] is not None
        assert kwargs['headers']['API_Key'] == 'k'

    @mock.patch('spellbook.requests')
    @mock.patch('spellbook.print')
    def test_get_with_data(self, mock_print, mock_requests):
        spellbook.args = make_args(explorer=None)
        mock_requests.get.return_value.text = 'response'
        data = {'block_height': 100}
        do_get_request('http://localhost/test', data=data)
        args, kwargs = mock_requests.get.call_args
        assert kwargs['json'] == data

    @mock.patch('spellbook.requests')
    @mock.patch('spellbook.sys')
    @mock.patch('spellbook.print')
    def test_get_request_exception(self, mock_print, mock_sys, mock_requests):
        mock_requests.get.side_effect = Exception('connection error')
        do_get_request('http://localhost/test')
        mock_sys.exit.assert_called_once_with(1)


class TestDoPostRequest(object):

    @mock.patch('spellbook.requests')
    @mock.patch('spellbook.print')
    def test_basic_post(self, mock_print, mock_requests):
        spellbook.args = make_args(explorer=None)
        mock_requests.post.return_value.text = 'response'
        do_post_request('http://localhost/test', data={'key': 'value'})
        mock_requests.post.assert_called_once()
        args, kwargs = mock_requests.post.call_args
        assert kwargs['json'] == {'key': 'value'}

    @mock.patch('spellbook.requests')
    @mock.patch('spellbook.print')
    def test_authenticated_post(self, mock_print, mock_requests):
        spellbook.args = make_args(api_key='k', api_secret=VALID_SECRET, explorer=None)
        mock_requests.post.return_value.text = 'response'
        do_post_request('http://localhost/test', authenticate=True, data={'x': 1})
        args, kwargs = mock_requests.post.call_args
        assert kwargs['headers'] is not None

    @mock.patch('spellbook.requests')
    @mock.patch('spellbook.sys')
    @mock.patch('spellbook.print')
    def test_post_request_exception(self, mock_print, mock_sys, mock_requests):
        spellbook.args = make_args(explorer=None)
        mock_requests.post.side_effect = Exception('fail')
        do_post_request('http://localhost/test')
        mock_sys.exit.assert_called_once_with(1)


class TestDoDeleteRequest(object):

    @mock.patch('spellbook.requests')
    @mock.patch('spellbook.print')
    def test_basic_delete(self, mock_print, mock_requests):
        spellbook.args = make_args(explorer=None)
        mock_requests.delete.return_value.text = 'deleted'
        do_delete_request('http://localhost/test')
        mock_requests.delete.assert_called_once()

    @mock.patch('spellbook.requests')
    @mock.patch('spellbook.print')
    def test_authenticated_delete(self, mock_print, mock_requests):
        spellbook.args = make_args(api_key='k', api_secret=VALID_SECRET, explorer=None)
        mock_requests.delete.return_value.text = 'deleted'
        do_delete_request('http://localhost/test', authenticate=True)
        args, kwargs = mock_requests.delete.call_args
        assert kwargs['headers'] is not None

    @mock.patch('spellbook.requests')
    @mock.patch('spellbook.sys')
    @mock.patch('spellbook.print')
    def test_delete_request_exception(self, mock_print, mock_sys, mock_requests):
        spellbook.args = make_args(explorer=None)
        mock_requests.delete.side_effect = Exception('fail')
        do_delete_request('http://localhost/test')
        mock_sys.exit.assert_called_once_with(1)


# --------------------------------------------------------------------------------------------------
# LLM Commands
# --------------------------------------------------------------------------------------------------

class TestGetLlms(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_llms(self, mock_get):
        get_llms()
        url = get_call_url(mock_get)
        assert '/spellbook/llms' in url


class TestGetLlmConfig(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_llm_config(self, mock_get):
        spellbook.args = make_args(id='OpenAI:gpt-4o', explorer=None)
        get_llm_config()
        url = get_call_url(mock_get)
        assert '/spellbook/llms/OpenAI:gpt-4o' in url


class TestSaveLlmConfig(object):

    @mock.patch('spellbook.do_post_request')
    def test_save_llm_config(self, mock_post):
        spellbook.args = make_args(
            id='test-llm', host='localhost', port='5000',
            server_type='OpenAI', model_name='gpt-4o',
            description='test model', explorer=None,
            api_key='k', api_secret='s'
        )
        save_llm_config()
        url = get_call_url(mock_post)
        assert '/spellbook/llms/test-llm' in url
        data = get_call_data(mock_post)
        assert data['host'] == 'localhost'
        assert data['server_type'] == 'OpenAI'
        assert data['model_name'] == 'gpt-4o'


class TestDeleteLlm(object):

    @mock.patch('spellbook.do_delete_request')
    def test_delete_llm(self, mock_delete):
        spellbook.args = make_args(id='test-llm', explorer=None)
        delete_llm()
        url = get_call_url(mock_delete)
        assert '/spellbook/llms/test-llm' in url


# --------------------------------------------------------------------------------------------------
# Explorer Commands
# --------------------------------------------------------------------------------------------------

class TestGetExplorers(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_explorers(self, mock_get):
        get_explorers()
        url = get_call_url(mock_get)
        assert '/spellbook/explorers' in url


class TestGetExplorerConfig(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_explorer_config(self, mock_get):
        spellbook.args = make_args(name='blockstream', explorer=None, api_key='k', api_secret='s')
        get_explorer_config()
        url = get_call_url(mock_get)
        assert '/spellbook/explorers/blockstream' in url


class TestSaveExplorer(object):

    @mock.patch('spellbook.do_post_request')
    def test_save_explorer(self, mock_post):
        spellbook.args = make_args(
            name='blockstream', type='Blockstream', priority='1',
            testnet=False, url=None, blocktrail_key='',
            explorer=None, api_key='k', api_secret='s'
        )
        save_explorer()
        data = get_call_data(mock_post)
        assert data['type'] == 'Blockstream'
        assert data['priority'] == '1'
        assert data['testnet'] is False


class TestDeleteExplorer(object):

    @mock.patch('spellbook.do_delete_request')
    def test_delete_explorer(self, mock_delete):
        spellbook.args = make_args(name='blockstream', explorer=None, api_key='k', api_secret='s')
        delete_explorer()
        url = get_call_url(mock_delete)
        assert '/spellbook/explorers/blockstream' in url


# --------------------------------------------------------------------------------------------------
# Blockchain Data Commands
# --------------------------------------------------------------------------------------------------

class TestGetLatestBlock(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_latest_block(self, mock_get):
        get_latest_block()
        url = get_call_url(mock_get)
        assert '/spellbook/blocks/latest' in url


class TestGetBlock(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_block(self, mock_get):
        spellbook.args = make_args(id='1000', explorer=None)
        get_block()
        url = get_call_url(mock_get)
        assert '/spellbook/blocks/1000' in url


class TestGetPrimeInputAddress(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_prime_input_address(self, mock_get):
        spellbook.args = make_args(txid='abc123', explorer=None)
        get_prime_input_address()
        url = get_call_url(mock_get)
        assert '/spellbook/transactions/abc123/prime_input' in url


class TestGetTransaction(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_transaction(self, mock_get):
        spellbook.args = make_args(txid='abc123', explorer=None)
        get_transaction()
        url = get_call_url(mock_get)
        assert '/spellbook/transactions/abc123' in url


class TestGetTransactions(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_transactions(self, mock_get):
        spellbook.args = make_args(address='1ABC123', explorer=None)
        get_transactions()
        url = get_call_url(mock_get)
        assert '/spellbook/addresses/1ABC123/transactions' in url


class TestGetBalance(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_balance(self, mock_get):
        spellbook.args = make_args(address='1ABC123', explorer=None)
        get_balance()
        url = get_call_url(mock_get)
        assert '/spellbook/addresses/1ABC123/balance' in url


class TestGetUtxos(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_utxos(self, mock_get):
        spellbook.args = make_args(address='1ABC123', confirmations=3, explorer=None)
        get_utxos()
        url = get_call_url(mock_get)
        assert '/spellbook/addresses/1ABC123/utxos' in url
        assert 'confirmations=3' in url


class TestGetSil(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_sil(self, mock_get):
        spellbook.args = make_args(address='1ABC123', block_height=100, explorer=None)
        get_sil()
        url = get_call_url(mock_get)
        assert '/spellbook/addresses/1ABC123/SIL' in url
        data = get_call_data(mock_get)
        assert data['block_height'] == 100


class TestGetProfile(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_profile(self, mock_get):
        spellbook.args = make_args(address='1ABC123', block_height=0, explorer=None)
        get_profile()
        url = get_call_url(mock_get)
        assert '/spellbook/addresses/1ABC123/profile' in url


class TestGetSul(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_sul(self, mock_get):
        spellbook.args = make_args(address='1ABC123', confirmations=1, explorer=None)
        get_sul()
        url = get_call_url(mock_get)
        assert '/spellbook/addresses/1ABC123/SUL' in url
        data = get_call_data(mock_get)
        assert data['confirmations'] == 1


class TestGetLal(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_lal(self, mock_get):
        spellbook.args = make_args(address='1ABC123', xpub='xpub123', block_height=0, explorer=None)
        get_lal()
        url = get_call_url(mock_get)
        assert '/spellbook/addresses/1ABC123/LAL' in url
        data = get_call_data(mock_get)
        assert data['xpub'] == 'xpub123'


class TestGetLbl(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_lbl(self, mock_get):
        spellbook.args = make_args(address='1ABC123', xpub='xpub123', block_height=0, explorer=None)
        get_lbl()
        url = get_call_url(mock_get)
        assert '/spellbook/addresses/1ABC123/LBL' in url


class TestGetLrl(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_lrl(self, mock_get):
        spellbook.args = make_args(address='1ABC123', xpub='xpub123', block_height=0, explorer=None)
        get_lrl()
        url = get_call_url(mock_get)
        assert '/spellbook/addresses/1ABC123/LRL' in url


class TestGetLsl(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_lsl(self, mock_get):
        spellbook.args = make_args(address='1ABC123', xpub='xpub123', block_height=0, explorer=None)
        get_lsl()
        url = get_call_url(mock_get)
        assert '/spellbook/addresses/1ABC123/LSL' in url


class TestGetRandomAddress(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_random_address(self, mock_get):
        spellbook.args = make_args(
            source='SIL', address='1ABC123', rng_block_height='1000',
            xpub=None, block_height=0, explorer=None
        )
        get_random_address()
        url = get_call_url(mock_get)
        assert '/spellbook/addresses/1ABC123/random/SIL' in url
        data = get_call_data(mock_get)
        assert data['rng_block_height'] == '1000'


# --------------------------------------------------------------------------------------------------
# Trigger Commands
# --------------------------------------------------------------------------------------------------

class TestGetTriggers(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_triggers(self, mock_get):
        get_triggers()
        url = get_call_url(mock_get)
        assert '/spellbook/triggers' in url


class TestGetTrigger(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_trigger(self, mock_get):
        spellbook.args = make_args(trigger_id='trig1', explorer=None, api_key='k', api_secret='s')
        get_trigger()
        url = get_call_url(mock_get)
        assert '/spellbook/triggers/trig1' in url


class TestSaveTrigger(object):

    @mock.patch('spellbook.do_post_request')
    def test_save_trigger_minimal(self, mock_post):
        spellbook.args = make_args(
            trigger_id='trig1', type='Manual', script=None,
            address=None, amount=None, confirmations=3,
            block_height=None, txid=None, timestamp=None,
            begin_time=None, end_time=None, interval=None,
            timeout=None, warning_email=None, reset=False,
            multi=False, previous_trigger=None,
            previous_trigger_status=None, description=None,
            creator_name=None, creator_email=None, youtube=None,
            visibility=None, status=None, actions=None,
            explorer=None, api_key='k', api_secret='s'
        )
        save_trigger()
        url = get_call_url(mock_post)
        assert '/spellbook/triggers/trig1' in url
        data = get_call_data(mock_post)
        assert data['trigger_type'] == 'Manual'

    @mock.patch('spellbook.do_post_request')
    def test_save_trigger_full(self, mock_post):
        spellbook.args = make_args(
            trigger_id='trig2', type='Balance', script='myscript',
            address='1ABC123', amount=1000, confirmations=5,
            block_height=500, txid='abc123', timestamp=1234567890,
            begin_time='12:00', end_time='13:00', interval=60,
            timeout=300, warning_email='warn@example.com', reset=True,
            multi=True, previous_trigger='trig0',
            previous_trigger_status='Active', description='test trigger',
            creator_name='Wouter', creator_email='w@valyrian.tech',
            youtube='https://youtube.com/watch?v=abc', visibility='Public', status='Active',
            actions=['act1', 'act2'],
            explorer=None, api_key='k', api_secret='s'
        )
        save_trigger()
        data = get_call_data(mock_post)
        assert data['trigger_type'] == 'Balance'
        assert data['address'] == '1ABC123'
        assert data['amount'] == 1000
        assert data['confirmations'] == 5
        assert data['reset'] is True
        assert data['multi'] is True
        assert data['description'] == 'test trigger'
        assert data['visibility'] == 'Public'
        assert data['status'] == 'Active'
        assert data['actions'] == ['act1', 'act2']


class TestDeleteTrigger(object):

    @mock.patch('spellbook.do_delete_request')
    def test_delete_trigger(self, mock_delete):
        spellbook.args = make_args(trigger_id='trig1', explorer=None, api_key='k', api_secret='s')
        delete_trigger()
        url = get_call_url(mock_delete)
        assert '/spellbook/triggers/trig1' in url


class TestActivateTrigger(object):

    @mock.patch('spellbook.do_get_request')
    def test_activate_trigger(self, mock_get):
        spellbook.args = make_args(trigger_id='trig1', explorer=None, api_key='k', api_secret='s')
        activate_trigger()
        url = get_call_url(mock_get)
        assert '/spellbook/triggers/trig1/activate' in url


class TestSendSignedMessage(object):

    @mock.patch('spellbook.do_post_request')
    def test_send_signed_message_with_string(self, mock_post):
        spellbook.args = make_args(
            trigger_id='trig1', address='1ABC123',
            message='hello world', signature='sig123',
            explorer=None
        )
        send_signed_message()
        data = get_call_data(mock_post)
        assert data['address'] == '1ABC123'
        assert data['message'] == 'hello world'
        assert data['signature'] == 'sig123'

    @mock.patch('spellbook.do_post_request')
    def test_send_signed_message_with_file(self, mock_post, tmp_path):
        msg_file = tmp_path / "message.txt"
        msg_file.write_text("file message content")
        spellbook.args = make_args(
            trigger_id='trig1', address='1ABC123',
            message=str(msg_file), signature='sig123',
            explorer=None
        )
        send_signed_message()
        data = get_call_data(mock_post)
        assert data['message'] == 'file message content'


class TestSignMessage(object):

    @mock.patch('spellbook.do_post_request')
    def test_sign_message_with_string(self, mock_post):
        spellbook.args = make_args(
            address='1ABC123', message=['hello', 'world'],
            explorer=None, api_key='k', api_secret='s'
        )
        sign_message()
        data = get_call_data(mock_post)
        assert data['address'] == '1ABC123'
        assert data['message'] == 'hello world'

    @mock.patch('spellbook.do_post_request')
    def test_sign_message_with_file(self, mock_post, tmp_path):
        msg_file = tmp_path / "msg.txt"
        msg_file.write_text("file message")
        spellbook.args = make_args(
            address='1ABC123', message=[str(msg_file)],
            explorer=None, api_key='k', api_secret='s'
        )
        sign_message()
        data = get_call_data(mock_post)
        assert data['message'] == 'file message'

    @mock.patch('spellbook.do_post_request')
    @mock.patch('builtins.print')
    def test_sign_message_too_long(self, mock_print, mock_post):
        spellbook.args = make_args(
            address='1ABC123', message=['x' * 300],
            explorer=None, api_key='k', api_secret='s'
        )
        sign_message()
        mock_post.assert_not_called()


class TestCheckTriggers(object):

    @mock.patch('spellbook.do_get_request')
    def test_check_specific_trigger(self, mock_get):
        spellbook.args = make_args(trigger_id='trig1', explorer=None, api_key='k', api_secret='s')
        check_triggers()
        url = get_call_url(mock_get)
        assert '/spellbook/triggers/trig1/check' in url

    @mock.patch('spellbook.do_get_request')
    def test_check_all_triggers(self, mock_get):
        spellbook.args = make_args(trigger_id=None, explorer=None, api_key='k', api_secret='s')
        check_triggers()
        url = get_call_url(mock_get)
        assert '/spellbook/check_triggers' in url


# --------------------------------------------------------------------------------------------------
# Action Commands
# --------------------------------------------------------------------------------------------------

class TestGetActions(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_actions(self, mock_get):
        get_actions()
        url = get_call_url(mock_get)
        assert '/spellbook/actions' in url


class TestGetAction(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_action(self, mock_get):
        spellbook.args = make_args(action_id='act1', explorer=None, api_key='k', api_secret='s')
        get_action()
        url = get_call_url(mock_get)
        assert '/spellbook/actions/act1' in url


class TestSaveAction(object):

    @mock.patch('spellbook.do_post_request')
    def test_save_action_command_type(self, mock_post):
        spellbook.args = make_args(
            action_id='act1', type='Command', run_command='echo hello',
            job_config=None, mail_recipients=None, mail_subject=None,
            mail_body_template=None, webhook=None, reveal_text=None,
            reveal_link=None, fee_address=None, fee_percentage=None,
            wallet_type=None, sending_address=None, bip44_account=None,
            bip44_index=None, receiving_address=None, amount=None,
            minimum_amount=None, op_return_data=None, change_address=None,
            transaction_type=None, registration_address=None,
            registration_block_height=0, registration_xpub=None,
            tx_fee_type='Medium', tx_fee=None, distribution=None,
            explorer=None, api_key='k', api_secret='s'
        )
        save_action()
        url = get_call_url(mock_post)
        assert '/spellbook/actions/act1' in url
        data = get_call_data(mock_post)
        assert data['action_type'] == 'Command'
        assert data['run_command'] == 'echo hello'

    @mock.patch('spellbook.do_post_request')
    def test_save_action_send_transaction(self, mock_post):
        spellbook.args = make_args(
            action_id='act2', type='SendTransaction', run_command=None,
            job_config='job.json', mail_recipients='a@b.com',
            mail_subject='Test', mail_body_template='Body',
            webhook='http://webhook.example', reveal_text='secret',
            reveal_link='http://reveal.example', fee_address='1FeeAddr', fee_percentage=1.5,
            wallet_type='Single', sending_address='1Sender',
            bip44_account=0, bip44_index=0,
            receiving_address='1Receiver', amount=50000,
            minimum_amount=1000, op_return_data='hello',
            change_address='1Change', transaction_type='Send2Single',
            registration_address='1RegAddr', registration_block_height=100,
            registration_xpub='xpub123', tx_fee_type='Fixed', tx_fee=50,
            distribution=None, explorer=None, api_key='k', api_secret='s'
        )
        save_action()
        data = get_call_data(mock_post)
        assert data['action_type'] == 'SendTransaction'
        assert data['fee_address'] == '1FeeAddr'
        assert data['wallet_type'] == 'Single'
        assert data['sending_address'] == '1Sender'
        assert data['receiving_address'] == '1Receiver'
        assert data['amount'] == 50000
        assert data['tx_fee'] == 50
        assert data['tx_fee_type'] == 'Fixed'

    @mock.patch('spellbook.valid_distribution', return_value=True)
    @mock.patch('spellbook.do_post_request')
    def test_save_action_with_distribution_file(self, mock_post, mock_valid_dist, tmp_path):
        dist_file = tmp_path / "distribution.json"
        dist_file.write_text('{"1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa": 50, "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVX2": 50}')
        spellbook.args = make_args(
            action_id='act3', type='Send2Many', run_command=None,
            job_config=None, mail_recipients=None, mail_subject=None,
            mail_body_template=None, webhook=None, reveal_text=None,
            reveal_link=None, fee_address=None, fee_percentage=None,
            wallet_type=None, sending_address=None, bip44_account=None,
            bip44_index=None, receiving_address=None, amount=None,
            minimum_amount=None, op_return_data=None, change_address=None,
            transaction_type='Send2Many', registration_address=None,
            registration_block_height=0, registration_xpub=None,
            tx_fee_type='Medium', tx_fee=None, distribution=str(dist_file),
            explorer=None, api_key='k', api_secret='s'
        )
        save_action()
        data = get_call_data(mock_post)
        assert 'distribution' in data

    @mock.patch('spellbook.do_post_request')
    def test_save_action_with_invalid_distribution_file(self, mock_post, tmp_path):
        dist_file = tmp_path / "bad.json"
        dist_file.write_text('not valid json')
        spellbook.args = make_args(
            action_id='act4', type='Send2Many', run_command=None,
            job_config=None, mail_recipients=None, mail_subject=None,
            mail_body_template=None, webhook=None, reveal_text=None,
            reveal_link=None, fee_address=None, fee_percentage=None,
            wallet_type=None, sending_address=None, bip44_account=None,
            bip44_index=None, receiving_address=None, amount=None,
            minimum_amount=None, op_return_data=None, change_address=None,
            transaction_type='Send2Many', registration_address=None,
            registration_block_height=0, registration_xpub=None,
            tx_fee_type='Medium', tx_fee=None, distribution=str(dist_file),
            explorer=None, api_key='k', api_secret='s'
        )
        with pytest.raises(SystemExit) as exc_info:
            save_action()
        assert exc_info.value.code == 1
        mock_post.assert_not_called()

    @mock.patch('spellbook.do_post_request')
    def test_save_action_with_invalid_distribution_content(self, mock_post, tmp_path):
        dist_file = tmp_path / "bad_dist.json"
        dist_file.write_text('{"not_an_address": 50}')
        spellbook.args = make_args(
            action_id='act5', type='Send2Many', run_command=None,
            job_config=None, mail_recipients=None, mail_subject=None,
            mail_body_template=None, webhook=None, reveal_text=None,
            reveal_link=None, fee_address=None, fee_percentage=None,
            wallet_type=None, sending_address=None, bip44_account=None,
            bip44_index=None, receiving_address=None, amount=None,
            minimum_amount=None, op_return_data=None, change_address=None,
            transaction_type='Send2Many', registration_address=None,
            registration_block_height=0, registration_xpub=None,
            tx_fee_type='Medium', tx_fee=None, distribution=str(dist_file),
            explorer=None, api_key='k', api_secret='s'
        )
        with pytest.raises(SystemExit) as exc_info:
            save_action()
        assert exc_info.value.code == 1
        mock_post.assert_not_called()


class TestDeleteAction(object):

    @mock.patch('spellbook.do_delete_request')
    def test_delete_action(self, mock_delete):
        spellbook.args = make_args(action_id='act1', explorer=None, api_key='k', api_secret='s')
        delete_action()
        url = get_call_url(mock_delete)
        assert '/spellbook/actions/act1' in url


class TestRunAction(object):

    @mock.patch('spellbook.do_get_request')
    def test_run_action(self, mock_get):
        spellbook.args = make_args(action_id='act1', explorer=None, api_key='k', api_secret='s')
        run_action()
        url = get_call_url(mock_get)
        assert '/spellbook/actions/act1/run' in url


class TestGetReveal(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_reveal(self, mock_get):
        spellbook.args = make_args(action_id='act1', explorer=None)
        get_reveal()
        url = get_call_url(mock_get)
        assert '/spellbook/actions/act1/reveal' in url


class TestGetLogs(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_logs(self, mock_get):
        spellbook.args = make_args(
            filter_string=['error', 'timeout'],
            explorer=None, api_key='k', api_secret='s'
        )
        get_logs()
        url = get_call_url(mock_get)
        assert '/spellbook/logs/' in url
        assert 'error timeout' in url


class TestGetHivemind(object):

    @mock.patch('spellbook.do_get_request')
    def test_get_hivemind(self, mock_get):
        spellbook.args = make_args(hivemind_id='hive1', explorer=None)
        get_hivemind()
        url = get_call_url(mock_get)
        assert '/spellbook/hiveminds/hive1' in url


class TestCommandDispatch(object):
    """Test module-level command dispatch by re-importing spellbook.py with subcommands."""

    def _reload_with_command(self, command, extra_args=None):
        argv = ['spellbook.py', command]
        if extra_args:
            argv.extend(extra_args)
        with mock.patch('sys.argv', argv):
            _spec = importlib.util.spec_from_file_location('spellbook_dispatch_' + command, _SPELLBOOK_PATH)
            _mod = importlib.util.module_from_spec(_spec)
            with mock.patch('requests.get') as mock_get, \
                 mock.patch('requests.post') as mock_post, \
                 mock.patch('requests.delete') as mock_delete:
                mock_get.return_value.text = '{}'
                mock_post.return_value.text = '{}'
                mock_delete.return_value.text = '{}'
                _spec.loader.exec_module(_mod)
                return mock_get, mock_post, mock_delete

    def test_dispatch_get_llms(self):
        mock_get, _, _ = self._reload_with_command('get_llms')
        mock_get.assert_called_once()

    def test_dispatch_get_explorers(self):
        mock_get, _, _ = self._reload_with_command('get_explorers')
        mock_get.assert_called_once()

    def test_dispatch_get_latest_block(self):
        mock_get, _, _ = self._reload_with_command('get_latest_block')
        mock_get.assert_called_once()

    def test_dispatch_get_triggers(self):
        mock_get, _, _ = self._reload_with_command('get_triggers')
        mock_get.assert_called_once()

    def test_dispatch_get_actions(self):
        mock_get, _, _ = self._reload_with_command('get_actions')
        mock_get.assert_called_once()

    def test_dispatch_get_block(self):
        mock_get, _, _ = self._reload_with_command('get_block', ['1000'])
        mock_get.assert_called_once()

    def test_dispatch_get_transaction(self):
        mock_get, _, _ = self._reload_with_command('get_transaction', ['abc123'])
        mock_get.assert_called_once()

    def test_dispatch_get_balance(self):
        mock_get, _, _ = self._reload_with_command('get_balance', ['1ABC123'])
        mock_get.assert_called_once()

    def test_dispatch_get_utxos(self):
        mock_get, _, _ = self._reload_with_command('get_utxos', ['1ABC123'])
        mock_get.assert_called_once()

    def test_dispatch_get_sil(self):
        mock_get, _, _ = self._reload_with_command('get_sil', ['1ABC123'])
        mock_get.assert_called_once()

    def test_dispatch_get_profile(self):
        mock_get, _, _ = self._reload_with_command('get_profile', ['1ABC123'])
        mock_get.assert_called_once()

    def test_dispatch_get_sul(self):
        mock_get, _, _ = self._reload_with_command('get_sul', ['1ABC123'])
        mock_get.assert_called_once()

    def test_dispatch_get_lal(self):
        mock_get, _, _ = self._reload_with_command('get_lal', ['1ABC123', 'xpub123'])
        mock_get.assert_called_once()

    def test_dispatch_get_lbl(self):
        mock_get, _, _ = self._reload_with_command('get_lbl', ['1ABC123', 'xpub123'])
        mock_get.assert_called_once()

    def test_dispatch_get_lrl(self):
        mock_get, _, _ = self._reload_with_command('get_lrl', ['1ABC123', 'xpub123'])
        mock_get.assert_called_once()

    def test_dispatch_get_lsl(self):
        mock_get, _, _ = self._reload_with_command('get_lsl', ['1ABC123', 'xpub123'])
        mock_get.assert_called_once()

    def test_dispatch_get_random_address(self):
        mock_get, _, _ = self._reload_with_command('get_random_address', ['SIL', '1ABC123', '1000'])
        mock_get.assert_called_once()

    def test_dispatch_get_trigger_config(self):
        mock_get, _, _ = self._reload_with_command('get_trigger_config', ['trig1'])
        mock_get.assert_called_once()

    def test_dispatch_activate_trigger(self):
        mock_get, _, _ = self._reload_with_command('activate_trigger', ['trig1'])
        mock_get.assert_called_once()

    def test_dispatch_check_triggers(self):
        mock_get, _, _ = self._reload_with_command('check_triggers')
        mock_get.assert_called_once()

    def test_dispatch_get_action_config(self):
        mock_get, _, _ = self._reload_with_command('get_action_config', ['act1'])
        mock_get.assert_called_once()

    def test_dispatch_run_action(self):
        mock_get, _, _ = self._reload_with_command('run_action', ['act1'])
        mock_get.assert_called_once()

    def test_dispatch_get_reveal(self):
        mock_get, _, _ = self._reload_with_command('get_reveal', ['act1'])
        mock_get.assert_called_once()

    def test_dispatch_get_logs(self):
        mock_get, _, _ = self._reload_with_command('get_logs', ['error'])
        mock_get.assert_called_once()

    def test_dispatch_get_llm_config(self):
        mock_get, _, _ = self._reload_with_command('get_llm_config', ['OpenAI:gpt-4o'])
        mock_get.assert_called_once()

    def test_dispatch_get_explorer_config(self):
        mock_get, _, _ = self._reload_with_command('get_explorer_config', ['blockstream'])
        mock_get.assert_called_once()

    def test_dispatch_get_hivemind(self):
        mock_get, _, _ = self._reload_with_command('get_hivemind', ['hive1'])
        mock_get.assert_called_once()

    def test_dispatch_get_prime_input_address(self):
        mock_get, _, _ = self._reload_with_command('get_prime_input_address', ['abc123'])
        mock_get.assert_called_once()

    def test_dispatch_get_transactions(self):
        mock_get, _, _ = self._reload_with_command('get_transactions', ['1ABC123'])
        mock_get.assert_called_once()

    def test_dispatch_save_explorer(self):
        _, mock_post, _ = self._reload_with_command('save_explorer', ['test', 'Blockchain.info', '1'])
        mock_post.assert_called_once()

    def test_dispatch_delete_explorer(self):
        _, _, mock_delete = self._reload_with_command('delete_explorer', ['test'])
        mock_delete.assert_called_once()

    def test_dispatch_save_trigger(self):
        _, mock_post, _ = self._reload_with_command('save_trigger', ['trig1', '--type', 'Manual'])
        mock_post.assert_called_once()

    def test_dispatch_delete_trigger(self):
        _, _, mock_delete = self._reload_with_command('delete_trigger', ['trig1'])
        mock_delete.assert_called_once()

    def test_dispatch_send_signed_message(self):
        _, mock_post, _ = self._reload_with_command('send_signed_message', ['trig1', '1ABC123', 'hello', 'sig123'])
        mock_post.assert_called_once()

    def test_dispatch_sign_message(self):
        _, mock_post, _ = self._reload_with_command('sign_message', ['1ABC123', 'hello'])
        mock_post.assert_called_once()

    def test_dispatch_save_action(self):
        _, mock_post, _ = self._reload_with_command('save_action', ['act1', '--type', 'Command', '--run_command', 'echo hi'])
        mock_post.assert_called_once()

    def test_dispatch_delete_action(self):
        _, _, mock_delete = self._reload_with_command('delete_action', ['act1'])
        mock_delete.assert_called_once()

    def test_dispatch_save_llm_config(self):
        _, mock_post, _ = self._reload_with_command('save_llm_config', ['test-llm', 'localhost', '-t', 'OpenAI', '-m', 'gpt-4o'])
        mock_post.assert_called_once()

    def test_dispatch_delete_llm(self):
        _, _, mock_delete = self._reload_with_command('delete_llm', ['test-llm'])
        mock_delete.assert_called_once()
