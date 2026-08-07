#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for spellbookserver.py — the Valyrian Spellbook REST API server (Bottle).

The SpellbookRESTAPI.__init__ starts a web server via self.run(), so we mock
that out and test the endpoint callbacks as static methods.
"""
import logging
import sys
from unittest.mock import patch, MagicMock, mock_open

import pytest

# --- Module loading -----------------------------------------------------------
# spellbookserver.py imports heavy dependencies at module level (faster_whisper,
# hot wallet, etc.).  We patch the problematic ones before importing.

# Prevent WhisperModel from loading at import time
_transcribe_patcher = patch('spellbookserver.get_enable_transcribe', return_value=False)
_transcribe_patcher.start()

# Prevent server startup side-effects during import
_wallet_patcher = patch('spellbookserver.get_enable_wallet', return_value=False)
_wallet_patcher.start()

import spellbookserver as srv
from spellbookserver import (
    enable_cors,
    SpellbookRESTAPI,
    convert_aac_to_opus,
)

# Re-enable for individual tests if needed
_transcribe_patcher.stop()
_wallet_patcher.stop()


@pytest.fixture(autouse=True)
def _passthrough_output_json():
    """Make @output_json decorator return raw objects instead of JSON strings."""
    with patch('decorators.simplejson.dumps', side_effect=lambda x, **kw: x):
        yield


# --- Fixtures -----------------------------------------------------------------
@pytest.fixture
def mock_bottle_request():
    """Patch bottle.request for endpoint tests."""
    with patch('spellbookserver.request') as mock_req:
        mock_req.json = None
        mock_req.query = MagicMock()
        mock_req.query.explorer = ''
        mock_req.query.confirmations = '6'
        mock_req.method = 'GET'
        mock_req.remote_addr = '127.0.0.1'
        mock_req.url = 'http://localhost/test'
        mock_req.headers = {}
        mock_req.files = MagicMock()
        yield mock_req


@pytest.fixture
def mock_bottle_response():
    """Patch bottle.response for endpoint tests."""
    with patch('spellbookserver.response') as mock_resp:
        mock_resp.content_type = 'text/html'
        mock_resp.status = 200
        mock_resp.headers = MagicMock()
        yield mock_resp


# --- enable_cors tests --------------------------------------------------------
class TestEnableCors:
    def test_cors_headers_set(self):
        """Test that enable_cors sets the correct CORS headers."""
        with patch('spellbookserver.response') as mock_resp:
            mock_resp.headers = {}

            @enable_cors
            def dummy():
                return 'ok'

            result = dummy()
            assert result == 'ok'
            assert mock_resp.headers['Access-Control-Allow-Origin'] == '*'
            assert mock_resp.headers['Access-Control-Allow-Credentials'] is True
            assert 'GET' in mock_resp.headers['Access-Control-Allow-Methods']


# --- log_to_logger tests ------------------------------------------------------
class TestLogToLogger:
    def test_log_to_logger_success(self):
        """Test log_to_logger wrapper logs request and response."""
        with patch('spellbookserver.request') as mock_req, \
             patch('spellbookserver.response') as mock_resp, \
             patch('spellbookserver.REQUESTS_LOG') as mock_req_log, \
             patch('spellbookserver.LOG') as mock_log:
            mock_req.remote_addr = '127.0.0.1'
            mock_req.method = 'GET'
            mock_req.url = 'http://localhost/ping'
            mock_req.headers = {'X-Test': 'val'}
            mock_req.json = None
            mock_resp.status = '200 OK'

            api = MagicMock(spec=SpellbookRESTAPI)
            # Bypass __init__ which starts the server
            wrapper = SpellbookRESTAPI.log_to_logger(api, lambda: {'ok': True})
            result = wrapper()
            assert result == {'ok': True}
            assert mock_req_log.info.call_count >= 3

    def test_log_to_logger_with_json_body(self):
        """Test log_to_logger logs JSON body when present."""
        with patch('spellbookserver.request') as mock_req, \
             patch('spellbookserver.response') as mock_resp, \
             patch('spellbookserver.REQUESTS_LOG') as mock_req_log, \
             patch('spellbookserver.LOG'):
            mock_req.remote_addr = '127.0.0.1'
            mock_req.method = 'POST'
            mock_req.url = 'http://localhost/save'
            mock_req.headers = {}
            mock_req.json = {'key': 'value'}
            mock_resp.status = '200 OK'

            api = MagicMock(spec=SpellbookRESTAPI)
            wrapper = SpellbookRESTAPI.log_to_logger(api, lambda: 'done')
            wrapper()
            # Should have logged the body key
            body_calls = [str(c) for c in mock_req_log.info.call_args_list]
            assert any('BODY' in b for b in body_calls)

    def test_log_to_logger_exception(self):
        """Test log_to_logger handles exceptions and logs them."""
        with patch('spellbookserver.request') as mock_req, \
             patch('spellbookserver.response') as mock_resp, \
             patch('spellbookserver.REQUESTS_LOG') as mock_req_log, \
             patch('spellbookserver.LOG') as mock_log, \
             patch('spellbookserver.get_mail_on_exception', return_value=False):
            mock_req.remote_addr = '127.0.0.1'
            mock_req.method = 'GET'
            mock_req.url = 'http://localhost/bad'
            mock_req.headers = {}
            mock_req.json = None
            mock_resp.status = '200 OK'

            def boom():
                raise ValueError('test error')

            api = MagicMock(spec=SpellbookRESTAPI)
            wrapper = SpellbookRESTAPI.log_to_logger(api, boom)
            result = wrapper()
            # Should return the default response object, not raise
            assert result is mock_resp
            mock_log.error.assert_called()

    def test_log_to_logger_exception_with_mail(self):
        """Test log_to_logger sends mail on exception when enabled."""
        with patch('spellbookserver.request') as mock_req, \
             patch('spellbookserver.response') as mock_resp, \
             patch('spellbookserver.REQUESTS_LOG'), \
             patch('spellbookserver.LOG'), \
             patch('spellbookserver.get_mail_on_exception', return_value=True), \
             patch('spellbookserver.get_notification_email', return_value='a@b.c'), \
             patch('spellbookserver.get_host', return_value='localhost'), \
             patch('spellbookserver.sendmail') as mock_send:
            mock_req.remote_addr = '127.0.0.1'
            mock_req.method = 'GET'
            mock_req.url = 'http://localhost/bad'
            mock_req.headers = {}
            mock_req.json = None
            mock_resp.status = '200 OK'

            api = MagicMock(spec=SpellbookRESTAPI)
            wrapper = SpellbookRESTAPI.log_to_logger(api, lambda: (_ for _ in ()).throw(ValueError('boom')))
            wrapper()
            mock_send.assert_called_once()


# --- Static endpoint tests ----------------------------------------------------
class TestPing:
    @patch('spellbookserver.LOG')
    @patch('spellbookserver.response')
    def test_ping(self, mock_resp, mock_log):
        result = SpellbookRESTAPI.ping()
        assert result == {'success': True}
        assert mock_resp.content_type == 'application/json'


class TestGetLlms:
    @patch('spellbookserver.response')
    @patch('spellbookserver.load_llms')
    def test_get_llms_with_data(self, mock_load, mock_resp):
        mock_load.return_value = {'OpenAI:gpt-4o': {}, 'Anthropic:claude': {}}
        result = SpellbookRESTAPI.get_llms()
        assert 'OpenAI:gpt-4o' in result
        assert 'Anthropic:claude' in result

    @patch('spellbookserver.response')
    @patch('spellbookserver.load_llms')
    def test_get_llms_none(self, mock_load, mock_resp):
        mock_load.return_value = None
        result = SpellbookRESTAPI.get_llms()
        assert 'error' in result


class TestGetLlmConfig:
    @patch('spellbookserver.response')
    @patch('spellbookserver.get_llm_config')
    def test_get_llm_config_with_api_key(self, mock_get, mock_resp):
        mock_get.return_value = {'name': 'test', 'api_key': 'secret123'}
        result = SpellbookRESTAPI.get_llm_config('test-llm')
        assert result['api_key'] == '********'

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_llm_config')
    def test_get_llm_config_without_api_key(self, mock_get, mock_resp):
        mock_get.return_value = {'name': 'test'}
        result = SpellbookRESTAPI.get_llm_config('test-llm')
        assert result['name'] == 'test'

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_llm_config')
    def test_get_llm_config_empty_api_key(self, mock_get, mock_resp):
        mock_get.return_value = {'name': 'test', 'api_key': ''}
        result = SpellbookRESTAPI.get_llm_config('test-llm')
        assert result['api_key'] == ''

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_llm_config')
    def test_get_llm_config_none_api_key(self, mock_get, mock_resp):
        mock_get.return_value = {'name': 'test', 'api_key': None}
        result = SpellbookRESTAPI.get_llm_config('test-llm')
        assert result['api_key'] is None

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_llm_config')
    def test_get_llm_config_not_found(self, mock_get, mock_resp):
        mock_get.return_value = None
        result = SpellbookRESTAPI.get_llm_config('nope')
        assert 'error' in result


class TestSaveLlmConfig:
    @patch('spellbookserver.save_llm_config')
    @patch('spellbookserver.request')
    def test_save_llm_config(self, mock_req, mock_save):
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            mock_req.json = {'name': 'test'}
            SpellbookRESTAPI.save_llm_config('test-llm')
            mock_save.assert_called_once_with('test-llm', {'name': 'test'})


class TestDeleteLlm:
    @patch('spellbookserver.delete_llm')
    def test_delete_llm(self, mock_del):
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            SpellbookRESTAPI.delete_llm('test-llm')
            mock_del.assert_called_once_with('test-llm')


class TestGetExplorers:
    @patch('spellbookserver.response')
    @patch('spellbookserver.get_explorers')
    def test_get_explorers_with_data(self, mock_get, mock_resp):
        mock_get.return_value = {'blockstream': {}, 'blockchain.info': {}}
        result = SpellbookRESTAPI.get_explorers()
        assert 'blockstream' in result

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_explorers')
    def test_get_explorers_none(self, mock_get, mock_resp):
        mock_get.return_value = None
        result = SpellbookRESTAPI.get_explorers()
        assert 'error' in result


class TestGetExplorerConfig:
    @patch('spellbookserver.response')
    @patch('spellbookserver.get_explorer_config')
    def test_get_explorer_config_found(self, mock_get, mock_resp):
        mock_get.return_value = {'name': 'blockstream'}
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            result = SpellbookRESTAPI.get_explorer_config('blockstream')
            assert result['name'] == 'blockstream'

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_explorer_config')
    def test_get_explorer_config_not_found(self, mock_get, mock_resp):
        mock_get.return_value = None
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            result = SpellbookRESTAPI.get_explorer_config('nope')
            assert 'error' in result


class TestSaveExplorer:
    @patch('spellbookserver.response')
    @patch('spellbookserver.save_explorer')
    @patch('spellbookserver.request')
    def test_save_explorer(self, mock_req, mock_save, mock_resp):
        mock_req.json = {'name': 'blockstream'}
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            SpellbookRESTAPI.save_explorer('blockstream')
            mock_save.assert_called_once_with('blockstream', {'name': 'blockstream'})


class TestDeleteExplorer:
    @patch('spellbookserver.response')
    @patch('spellbookserver.delete_explorer')
    def test_delete_explorer(self, mock_delete, mock_resp):
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            SpellbookRESTAPI.delete_explorer('blockstream')
            mock_delete.assert_called_once_with('blockstream')


class TestIndexAndFavicon:
    def test_index(self):
        instance = MagicMock(spec=SpellbookRESTAPI)
        result = SpellbookRESTAPI.index(instance)
        assert result is None

    @patch('spellbookserver.static_file')
    def test_get_favicon(self, mock_static):
        SpellbookRESTAPI.get_favicon()
        mock_static.assert_called_once_with('favicon.ico', root='.')


class TestBlockchainEndpoints:
    @patch('spellbookserver.response')
    @patch('spellbookserver.latest_block')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_get_latest_block(self, mock_req, mock_set, mock_clear, mock_last, mock_block, mock_resp):
        mock_req.query.explorer = ''
        mock_block.return_value = {'height': 800000}
        result = SpellbookRESTAPI.get_latest_block()
        assert result['height'] == 800000

    @patch('spellbookserver.response')
    @patch('spellbookserver.block_by_height')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_get_block_by_height(self, mock_req, mock_set, mock_clear, mock_last, mock_block, mock_resp):
        mock_req.query.explorer = ''
        mock_block.return_value = {'hash': 'abc'}
        result = SpellbookRESTAPI.get_block_by_height(800000)
        assert result['hash'] == 'abc'

    @patch('spellbookserver.response')
    @patch('spellbookserver.block_by_hash')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_get_block_by_hash(self, mock_req, mock_set, mock_clear, mock_last, mock_block, mock_resp):
        mock_req.query.explorer = ''
        mock_block.return_value = {'height': 800000}
        result = SpellbookRESTAPI.get_block_by_hash('abcdef')
        assert result['height'] == 800000

    @patch('spellbookserver.response')
    @patch('spellbookserver.prime_input_address')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_get_prime_input_address(self, mock_req, mock_set, mock_clear, mock_last, mock_prime, mock_resp):
        mock_req.query.explorer = ''
        mock_prime.return_value = {'address': '1abc'}
        result = SpellbookRESTAPI.get_prime_input_address('txid123')
        assert result['address'] == '1abc'

    @patch('spellbookserver.response')
    @patch('spellbookserver.transaction')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_get_transaction(self, mock_req, mock_set, mock_clear, mock_last, mock_tx, mock_resp):
        mock_req.query.explorer = ''
        mock_tx.return_value = {'txid': 'abc'}
        result = SpellbookRESTAPI.get_transaction('txid123')
        assert result['txid'] == 'abc'

    @patch('spellbookserver.response')
    @patch('spellbookserver.transactions')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_get_transactions(self, mock_req, mock_set, mock_clear, mock_last, mock_txs, mock_resp):
        mock_req.query.explorer = ''
        mock_txs.return_value = [{'txid': 'abc'}]
        result = SpellbookRESTAPI.get_transactions('1abc')
        assert result[0]['txid'] == 'abc'

    @patch('spellbookserver.response')
    @patch('spellbookserver.balance')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_get_balance(self, mock_req, mock_set, mock_clear, mock_last, mock_bal, mock_resp):
        mock_req.query.explorer = ''
        mock_bal.return_value = {'balance': 1000}
        result = SpellbookRESTAPI.get_balance('1abc')
        assert result['balance'] == 1000

    @patch('spellbookserver.response')
    @patch('spellbookserver.utxos')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_get_utxos(self, mock_req, mock_set, mock_clear, mock_last, mock_utxos, mock_resp):
        mock_req.query.explorer = ''
        mock_req.query.confirmations = '6'
        mock_utxos.return_value = [{'txid': 'abc'}]
        result = SpellbookRESTAPI.get_utxos('1abc')
        assert result[0]['txid'] == 'abc'


class TestInputEndpoints:
    @patch('spellbookserver.response')
    @patch('spellbookserver.get_sil')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_get_sil(self, mock_req, mock_set, mock_clear, mock_last, mock_sil, mock_resp):
        mock_req.query.explorer = ''
        mock_req.json = {'block_height': 800000}
        mock_sil.return_value = {'sil': []}
        result = SpellbookRESTAPI.get_sil('1abc')
        mock_sil.assert_called_once_with('1abc', 800000)

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_profile')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_get_profile(self, mock_req, mock_set, mock_clear, mock_last, mock_prof, mock_resp):
        mock_req.query.explorer = ''
        mock_req.json = {'block_height': 800000}
        mock_prof.return_value = {'profile': {}}
        SpellbookRESTAPI.get_profile('1abc')
        mock_prof.assert_called_once_with('1abc', 800000)

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_sul')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_get_sul(self, mock_req, mock_set, mock_clear, mock_last, mock_sul, mock_resp):
        mock_req.query.explorer = ''
        mock_req.json = {'confirmations': 6}
        mock_sul.return_value = {'sul': []}
        SpellbookRESTAPI.get_sul('1abc')
        mock_sul.assert_called_once_with('1abc', 6)


class TestLinkedListEndpoints:
    def _setup_linked_list_test(self, mock_fn, mock_req, mock_resp, fn_name):
        mock_req.query.explorer = ''
        mock_req.json = {'block_height': 800000, 'xpub': 'xpub123'}
        mock_fn.return_value = {'data': 'test'}
        return mock_fn

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_lal')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_get_lal(self, mock_req, mock_set, mock_clear, mock_last, mock_lal, mock_resp):
        self._setup_linked_list_test(mock_lal, mock_req, mock_resp, 'lal')
        SpellbookRESTAPI.get_lal('1abc')
        mock_lal.assert_called_once_with('1abc', 'xpub123', 800000)

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_lbl')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_get_lbl(self, mock_req, mock_set, mock_clear, mock_last, mock_lbl, mock_resp):
        self._setup_linked_list_test(mock_lbl, mock_req, mock_resp, 'lbl')
        SpellbookRESTAPI.get_lbl('1abc')
        mock_lbl.assert_called_once_with('1abc', 'xpub123', 800000)

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_lrl')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_get_lrl(self, mock_req, mock_set, mock_clear, mock_last, mock_lrl, mock_resp):
        self._setup_linked_list_test(mock_lrl, mock_req, mock_resp, 'lrl')
        SpellbookRESTAPI.get_lrl('1abc')
        mock_lrl.assert_called_once_with('1abc', 'xpub123', 800000)

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_lsl')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_get_lsl(self, mock_req, mock_set, mock_clear, mock_last, mock_lsl, mock_resp):
        self._setup_linked_list_test(mock_lsl, mock_req, mock_resp, 'lsl')
        SpellbookRESTAPI.get_lsl('1abc')
        mock_lsl.assert_called_once_with('1abc', 'xpub123', 800000)


class TestRandomAddressEndpoints:
    @patch('spellbookserver.response')
    @patch('spellbookserver.random_address_from_sil')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_get_random_address_from_sil(self, mock_req, mock_set, mock_clear, mock_last, mock_rand, mock_resp):
        mock_req.query.explorer = ''
        mock_req.json = {'rng_block_height': 800000, 'sil_block_height': 799999}
        mock_rand.return_value = {'address': '1xyz'}
        SpellbookRESTAPI.get_random_address_from_sil('1abc')
        mock_rand.assert_called_once_with(address='1abc', sil_block_height=799999, rng_block_height=800000)

    @patch('spellbookserver.response')
    @patch('spellbookserver.random_address_from_lbl')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_get_random_address_from_lbl(self, mock_req, mock_set, mock_clear, mock_last, mock_rand, mock_resp):
        mock_req.query.explorer = ''
        mock_req.json = {'rng_block_height': 800000, 'sil_block_height': 799999, 'xpub': 'xpub123'}
        mock_rand.return_value = {'address': '1xyz'}
        SpellbookRESTAPI.get_random_address_from_lbl('1abc')
        mock_rand.assert_called_once_with(address='1abc', xpub='xpub123', sil_block_height=799999, rng_block_height=800000)

    @patch('spellbookserver.response')
    @patch('spellbookserver.random_address_from_lrl')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_get_random_address_from_lrl(self, mock_req, mock_set, mock_clear, mock_last, mock_rand, mock_resp):
        mock_req.query.explorer = ''
        mock_req.json = {'rng_block_height': 800000, 'sil_block_height': 799999, 'xpub': 'xpub123'}
        mock_rand.return_value = {'address': '1xyz'}
        SpellbookRESTAPI.get_random_address_from_lrl('1abc')
        mock_rand.assert_called_once_with(address='1abc', xpub='xpub123', sil_block_height=799999, rng_block_height=800000)

    @patch('spellbookserver.response')
    @patch('spellbookserver.random_address_from_lsl')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_get_random_address_from_lsl(self, mock_req, mock_set, mock_clear, mock_last, mock_rand, mock_resp):
        mock_req.query.explorer = ''
        mock_req.json = {'rng_block_height': 800000, 'sil_block_height': 799999, 'xpub': 'xpub123'}
        mock_rand.return_value = {'address': '1xyz'}
        SpellbookRESTAPI.get_random_address_from_lsl('1abc')
        mock_rand.assert_called_once_with(address='1abc', xpub='xpub123', sil_block_height=799999, rng_block_height=800000)


class TestTriggerEndpoints:
    @patch('spellbookserver.response')
    @patch('spellbookserver.get_triggers')
    def test_get_triggers_with_data(self, mock_get, mock_resp):
        mock_get.return_value = {'trig1': {}}
        result = SpellbookRESTAPI.get_triggers()
        assert 'trig1' in result

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_triggers')
    def test_get_triggers_none(self, mock_get, mock_resp):
        mock_get.return_value = None
        result = SpellbookRESTAPI.get_triggers()
        assert 'error' in result

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_trigger_config')
    def test_get_trigger_found(self, mock_get, mock_resp):
        mock_get.return_value = {'type': 'Manual'}
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            result = SpellbookRESTAPI.get_trigger('trig1')
            assert result['type'] == 'Manual'

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_trigger_config')
    def test_get_trigger_not_found(self, mock_get, mock_resp):
        mock_get.return_value = None
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            result = SpellbookRESTAPI.get_trigger('nope')
            assert 'error' in result

    @patch('spellbookserver.response')
    @patch('spellbookserver.save_trigger')
    @patch('spellbookserver.request')
    def test_save_trigger(self, mock_req, mock_save, mock_resp):
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            mock_req.json = {'type': 'Manual'}
            mock_save.return_value = {'success': True}
            SpellbookRESTAPI.save_trigger('trig1')
            mock_save.assert_called_once_with('trig1', type='Manual')

    @patch('spellbookserver.response')
    @patch('spellbookserver.delete_trigger')
    def test_delete_trigger(self, mock_del, mock_resp):
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            mock_del.return_value = {'success': True}
            SpellbookRESTAPI.delete_trigger('trig1')
            mock_del.assert_called_once_with('trig1')

    @patch('spellbookserver.response')
    @patch('spellbookserver.activate_trigger')
    def test_activate_trigger(self, mock_act, mock_resp):
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            mock_act.return_value = {'success': True}
            SpellbookRESTAPI.activate_trigger('trig1')
            mock_act.assert_called_once_with('trig1')

    @patch('spellbookserver.response')
    @patch('spellbookserver.verify_signed_message')
    @patch('spellbookserver.request')
    def test_verify_signed_message(self, mock_req, mock_verify, mock_resp):
        mock_req.json = {'message': 'hello', 'signature': 'sig123'}
        mock_req.query = {}
        mock_verify.return_value = {'valid': True}
        result = SpellbookRESTAPI.verify_signed_message('trig1')
        assert result['valid'] is True

    @patch('spellbookserver.response')
    @patch('spellbookserver.verify_signed_message')
    @patch('spellbookserver.request')
    def test_verify_signed_message_no_json(self, mock_req, mock_verify, mock_resp):
        mock_req.json = None
        mock_req.query = {}
        mock_verify.return_value = {'valid': False}
        result = SpellbookRESTAPI.verify_signed_message('trig1')
        assert result['valid'] is False

    @patch('spellbookserver.response')
    @patch('spellbookserver.sign_message')
    @patch('spellbookserver.request')
    def test_sign_message(self, mock_req, mock_sign, mock_resp):
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            mock_req.json = {'message': 'hello'}
            mock_sign.return_value = {'signature': 'abc'}
            SpellbookRESTAPI.sign_message()
            mock_sign.assert_called_once_with(message='hello')


class TestHttpRequestEndpoints:
    @patch('spellbookserver.response')
    @patch('spellbookserver.http_get_request')
    @patch('spellbookserver.request')
    def test_http_get_request(self, mock_req, mock_get, mock_resp):
        mock_req.json = {'key': 'val'}
        mock_req.query = {}
        mock_get.return_value = {'data': 'ok'}
        result = SpellbookRESTAPI.http_get_request('trig1')
        mock_get.assert_called_once_with('trig1', key='val')

    @patch('spellbookserver.response')
    @patch('spellbookserver.http_post_request')
    @patch('spellbookserver.request')
    def test_http_post_request(self, mock_req, mock_post, mock_resp):
        mock_req.json = {'key': 'val'}
        mock_req.query = {}
        mock_post.return_value = {'data': 'ok'}
        result = SpellbookRESTAPI.http_post_request('trig1')
        mock_post.assert_called_once_with('trig1', key='val')

    @patch('spellbookserver.response')
    @patch('spellbookserver.http_delete_request')
    @patch('spellbookserver.request')
    def test_http_delete_request(self, mock_req, mock_del, mock_resp):
        mock_req.json = {'key': 'val'}
        mock_req.query = {}
        mock_del.return_value = {'data': 'ok'}
        result = SpellbookRESTAPI.http_delete_request('trig1')
        mock_del.assert_called_once_with('trig1', key='val')

    @patch('spellbookserver.response')
    @patch('spellbookserver.http_options_request')
    @patch('spellbookserver.request')
    def test_http_options_request(self, mock_req, mock_opt, mock_resp):
        mock_req.json = {'key': 'val'}
        mock_req.query = {}
        mock_opt.return_value = {'data': 'ok'}
        result = SpellbookRESTAPI.http_options_request('trig1')
        mock_opt.assert_called_once_with('trig1', key='val')

    @patch('spellbookserver.response')
    @patch('spellbookserver.http_get_request')
    @patch('spellbookserver.request')
    def test_html_request(self, mock_req, mock_get, mock_resp):
        mock_req.json = None
        mock_req.query = {}
        mock_get.return_value = '<html>ok</html>'
        result = SpellbookRESTAPI.html_request('trig1')
        assert result == '<html>ok</html>'
        assert mock_resp.content_type == 'text/html'

    @patch('spellbookserver.response')
    @patch('spellbookserver.http_get_request')
    @patch('spellbookserver.request')
    def test_http_request_with_query_params(self, mock_req, mock_get, mock_resp):
        """Test that query string params are merged into data."""
        mock_req.json = None
        mock_req.query = {'param1': 'val1'}
        mock_get.return_value = {'ok': True}
        SpellbookRESTAPI.http_get_request('trig1')
        mock_get.assert_called_once_with('trig1', param1='val1')

    @patch('spellbookserver.response')
    @patch('spellbookserver.http_get_request')
    @patch('spellbookserver.request')
    def test_http_request_query_overrides_json(self, mock_req, mock_get, mock_resp):
        """Test that query string params override json body params."""
        mock_req.json = {'param1': 'from_json'}
        mock_req.query = {'param1': 'from_query'}
        mock_get.return_value = {'ok': True}
        SpellbookRESTAPI.http_get_request('trig1')
        mock_get.assert_called_once_with('trig1', param1='from_query')


class TestQrEndpoint:
    @patch('spellbookserver.response')
    @patch('spellbookserver.generate_qr')
    @patch('spellbookserver.request')
    def test_qr_with_json(self, mock_req, mock_qr, mock_resp):
        mock_req.json = {'data': 'test'}
        mock_req.query = {}
        mock_qr.return_value = b'png_data'
        result = SpellbookRESTAPI.qr()
        assert result == b'png_data'
        assert mock_resp.content_type == 'image/png'

    @patch('spellbookserver.response')
    @patch('spellbookserver.generate_qr')
    @patch('spellbookserver.request')
    def test_qr_with_query(self, mock_req, mock_qr, mock_resp):
        mock_req.json = None
        mock_req.query = {'text': 'hello'}
        mock_qr.return_value = b'png_data'
        SpellbookRESTAPI.qr()
        mock_qr.assert_called_once_with(text='hello')


class TestActionEndpoints:
    @patch('spellbookserver.response')
    @patch('spellbookserver.get_actions')
    def test_get_actions_with_data(self, mock_get, mock_resp):
        mock_get.return_value = {'act1': {}}
        result = SpellbookRESTAPI.get_actions()
        assert 'act1' in result

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_actions')
    def test_get_actions_none(self, mock_get, mock_resp):
        mock_get.return_value = None
        result = SpellbookRESTAPI.get_actions()
        assert 'error' in result

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_action_config')
    def test_get_action_found(self, mock_get, mock_resp):
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            mock_get.return_value = {'type': 'Command'}
            result = SpellbookRESTAPI.get_action('act1')
            assert result['type'] == 'Command'

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_action_config')
    def test_get_action_not_found(self, mock_get, mock_resp):
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            mock_get.return_value = None
            result = SpellbookRESTAPI.get_action('nope')
            assert 'error' in result

    @patch('spellbookserver.response')
    @patch('spellbookserver.save_action')
    @patch('spellbookserver.request')
    def test_save_action(self, mock_req, mock_save, mock_resp):
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            mock_req.json = {'type': 'Command'}
            mock_save.return_value = {'success': True}
            SpellbookRESTAPI.save_action('act1')
            mock_save.assert_called_once_with('act1', type='Command')

    @patch('spellbookserver.response')
    @patch('spellbookserver.delete_action')
    def test_delete_action(self, mock_del, mock_resp):
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            mock_del.return_value = {'success': True}
            SpellbookRESTAPI.delete_action('act1')
            mock_del.assert_called_once_with('act1')

    @patch('spellbookserver.response')
    @patch('spellbookserver.run_action')
    def test_run_action(self, mock_run, mock_resp):
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            mock_run.return_value = {'result': 'ok'}
            SpellbookRESTAPI.run_action('act1')
            mock_run.assert_called_once_with('act1')

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_reveal')
    def test_get_reveal(self, mock_reveal, mock_resp):
        mock_reveal.return_value = {'secret': 's3cr3t'}
        result = SpellbookRESTAPI.get_reveal('act1')
        assert result['secret'] == 's3cr3t'


class TestLogsEndpoint:
    @patch('spellbookserver.response')
    @patch('spellbookserver.get_logs')
    def test_get_logs(self, mock_get_logs, mock_resp):
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            mock_get_logs.return_value = ['log1', 'log2']
            result = SpellbookRESTAPI.get_logs('error')
            mock_get_logs.assert_called_once_with(filter_string='error')


class TestFileDownload:
    @patch('spellbookserver.response')
    @patch('spellbookserver.file_download')
    @patch('spellbookserver.request')
    def test_file_download(self, mock_req, mock_dl, mock_resp):
        mock_req.json = {'key': 'val'}
        mock_req.query = {}
        mock_dl.return_value = b'file_data'
        result = SpellbookRESTAPI.file_download('trig1')
        assert result == b'file_data'
        assert mock_resp.content_type == 'image/png'


class TestCheckTriggers:
    @patch('spellbookserver.response')
    @patch('spellbookserver.check_triggers')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_check_trigger(self, mock_req, mock_set, mock_clear, mock_last, mock_check, mock_resp):
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            mock_req.query.explorer = ''
            mock_check.return_value = {'triggered': True}
            result = SpellbookRESTAPI.check_trigger('trig1')
            mock_check.assert_called_once_with('trig1')

    @patch('spellbookserver.response')
    @patch('spellbookserver.check_triggers')
    @patch('decorators.get_last_explorer', return_value='blockstream')
    @patch('decorators.clear_explorer')
    @patch('decorators.set_explorer')
    @patch('spellbookserver.request')
    def test_check_all_triggers(self, mock_req, mock_set, mock_clear, mock_last, mock_check, mock_resp):
        with patch('decorators.check_authentication') as mock_dec:
            mock_dec.return_value = 'OK'
            mock_req.query.explorer = ''
            mock_check.return_value = {'triggered': []}
            result = SpellbookRESTAPI.check_all_triggers()
            mock_check.assert_called_once_with()


class TestUploadFile:
    @patch('spellbookserver.response')
    @patch('spellbookserver.get_enable_uploads', return_value=False)
    @patch('spellbookserver.LOG')
    def test_upload_disabled(self, mock_log, mock_enable, mock_resp):
        result = SpellbookRESTAPI.upload_file()
        assert 'error' in result
        assert mock_resp.status == 403

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_enable_uploads', return_value=True)
    @patch('spellbookserver.get_uploads_dir', return_value='/tmp/uploads')
    @patch('spellbookserver.os.path.exists', return_value=False)
    @patch('spellbookserver.os.makedirs')
    @patch('spellbookserver.request')
    @patch('spellbookserver.LOG')
    def test_upload_no_file(self, mock_log, mock_req, mock_makedirs, mock_exists, mock_dir, mock_enable, mock_resp):
        mock_req.files.get.return_value = None
        result = SpellbookRESTAPI.upload_file()
        assert 'error' in result
        assert mock_resp.status == 400

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_enable_uploads', return_value=True)
    @patch('spellbookserver.get_uploads_dir', return_value='/tmp/uploads')
    @patch('spellbookserver.os.path.exists', return_value=True)
    @patch('spellbookserver.request')
    @patch('spellbookserver.get_allowed_extensions', return_value='jpg,jpeg,png')
    @patch('spellbookserver.LOG')
    def test_upload_bad_extension(self, mock_log, mock_ext, mock_req, mock_exists, mock_dir, mock_enable, mock_resp):
        mock_file = MagicMock()
        mock_file.filename = 'test.exe'
        mock_req.files.get.return_value = mock_file
        result = SpellbookRESTAPI.upload_file()
        assert 'error' in result
        assert mock_resp.status == 403

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_enable_uploads', return_value=True)
    @patch('spellbookserver.get_uploads_dir', return_value='/tmp/uploads')
    @patch('spellbookserver.os.path.exists', return_value=True)
    @patch('spellbookserver.request')
    @patch('spellbookserver.get_allowed_extensions', return_value='jpg,jpeg,png')
    @patch('spellbookserver.magic.Magic')
    @patch('spellbookserver.LOG')
    def test_upload_bad_mime_type(self, mock_log, mock_magic_cls, mock_ext, mock_req, mock_exists, mock_dir, mock_enable, mock_resp):
        mock_file = MagicMock()
        mock_file.filename = 'test.jpg'
        mock_file.file.read.return_value = b'fake_data'
        mock_req.files.get.return_value = mock_file
        mock_mime = MagicMock()
        mock_mime.from_buffer.return_value = 'application/exe'
        mock_magic_cls.return_value = mock_mime
        result = SpellbookRESTAPI.upload_file()
        assert 'error' in result
        assert mock_resp.status == 403

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_enable_uploads', return_value=True)
    @patch('spellbookserver.get_uploads_dir', return_value='/tmp/uploads')
    @patch('spellbookserver.os.path.exists', return_value=True)
    @patch('spellbookserver.request')
    @patch('spellbookserver.get_allowed_extensions', return_value='jpg,jpeg,png')
    @patch('spellbookserver.get_max_file_size', return_value=100)
    @patch('spellbookserver.magic.Magic')
    @patch('spellbookserver.LOG')
    def test_upload_file_too_large(self, mock_log, mock_magic_cls, mock_max, mock_ext, mock_req, mock_exists, mock_dir, mock_enable, mock_resp):
        mock_file = MagicMock()
        mock_file.filename = 'test.jpg'
        mock_file.file.read.return_value = b'x' * 200
        mock_req.files.get.return_value = mock_file
        mock_mime = MagicMock()
        mock_mime.from_buffer.return_value = 'image/jpeg'
        mock_magic_cls.return_value = mock_mime
        result = SpellbookRESTAPI.upload_file()
        assert 'error' in result
        assert mock_resp.status == 413

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_enable_uploads', return_value=True)
    @patch('spellbookserver.get_uploads_dir', return_value='/tmp/uploads')
    @patch('spellbookserver.os.path.exists', return_value=True)
    @patch('spellbookserver.request')
    @patch('spellbookserver.get_allowed_extensions', return_value='jpg,jpeg,png')
    @patch('spellbookserver.get_max_file_size', return_value=1000000)
    @patch('spellbookserver.magic.Magic')
    @patch('spellbookserver.uuid')
    @patch('spellbookserver.LOG')
    def test_upload_success(self, mock_log, mock_uuid, mock_magic_cls, mock_max, mock_ext, mock_req, mock_exists, mock_dir, mock_enable, mock_resp):
        mock_uuid.uuid4.return_value = 'test-uuid'
        mock_file = MagicMock()
        mock_file.filename = 'test.jpg'
        mock_file.file.read.return_value = b'valid_image_data'
        mock_req.files.get.return_value = mock_file
        mock_mime = MagicMock()
        mock_mime.from_buffer.return_value = 'image/jpeg'
        mock_magic_cls.return_value = mock_mime
        result = SpellbookRESTAPI.upload_file()
        assert result['file_id'] == 'test-uuid.jpg'
        assert result['file_name'] == 'test.jpg'
        mock_file.save.assert_called_once()

    @patch('spellbookserver.response')
    @patch('spellbookserver.get_enable_uploads', return_value=True)
    @patch('spellbookserver.get_uploads_dir', return_value='/tmp/uploads')
    @patch('spellbookserver.os.path.exists', return_value=True)
    @patch('spellbookserver.request')
    @patch('spellbookserver.get_allowed_extensions', return_value='jpg,jpeg,png')
    @patch('spellbookserver.get_max_file_size', return_value=1000000)
    @patch('spellbookserver.magic.Magic')
    @patch('spellbookserver.uuid')
    @patch('spellbookserver.LOG')
    def test_upload_save_exception(self, mock_log, mock_uuid, mock_magic_cls, mock_max, mock_ext, mock_req, mock_exists, mock_dir, mock_enable, mock_resp):
        mock_uuid.uuid4.return_value = 'test-uuid'
        mock_file = MagicMock()
        mock_file.filename = 'test.jpg'
        mock_file.file.read.return_value = b'valid_image_data'
        mock_file.save.side_effect = OSError('disk full')
        mock_req.files.get.return_value = mock_file
        mock_mime = MagicMock()
        mock_mime.from_buffer.return_value = 'image/jpeg'
        mock_magic_cls.return_value = mock_mime
        result = SpellbookRESTAPI.upload_file()
        assert 'error' in result
        assert mock_resp.status == 500


class TestTranscribe:
    @patch('spellbookserver.request')
    @patch('spellbookserver.get_enable_transcribe', return_value=False)
    def test_transcribe_disabled(self, mock_enable, mock_req):
        mock_req.method = 'POST'
        result = SpellbookRESTAPI.transcribe()
        assert '403' in str(result.status)

    @patch('spellbookserver.request')
    def test_transcribe_options(self, mock_req):
        mock_req.method = 'OPTIONS'
        result = SpellbookRESTAPI.transcribe()
        assert result == {}

    @patch('spellbookserver.request')
    @patch('spellbookserver.get_enable_transcribe', return_value=True)
    def test_transcribe_no_file(self, mock_enable, mock_req):
        mock_req.method = 'POST'
        mock_req.files.get.return_value = None
        result = SpellbookRESTAPI.transcribe()
        assert '400' in str(result.status)

    @patch('spellbookserver.request')
    @patch('spellbookserver.get_enable_transcribe', return_value=True)
    @patch('spellbookserver.get_allowed_extensions_transcribe', return_value='mp3')
    def test_transcribe_bad_extension(self, mock_ext, mock_enable, mock_req):
        mock_req.method = 'POST'
        mock_file = MagicMock()
        mock_file.filename = 'test.exe'
        mock_req.files.get.return_value = mock_file
        result = SpellbookRESTAPI.transcribe()
        assert '403' in str(result.status)

    @patch('spellbookserver.request')
    @patch('spellbookserver.get_enable_transcribe', return_value=True)
    @patch('spellbookserver.get_allowed_extensions_transcribe', return_value='mp3')
    @patch('spellbookserver.magic.Magic')
    @patch('spellbookserver.LOG')
    def test_transcribe_bad_mime_type(self, mock_log, mock_magic_cls, mock_ext, mock_enable, mock_req):
        mock_req.method = 'POST'
        mock_file = MagicMock()
        mock_file.filename = 'test.mp3'
        mock_file.file.read.return_value = b'fake_data'
        mock_req.files.get.return_value = mock_file
        mock_mime = MagicMock()
        mock_mime.from_buffer.return_value = 'text/plain'
        mock_magic_cls.return_value = mock_mime
        result = SpellbookRESTAPI.transcribe()
        assert '403' in str(result.status)

    @patch('spellbookserver.request')
    @patch('spellbookserver.get_enable_transcribe', return_value=True)
    @patch('spellbookserver.get_allowed_extensions_transcribe', return_value='mp3')
    @patch('spellbookserver.get_max_file_size_transcribe', return_value=100)
    @patch('spellbookserver.magic.Magic')
    @patch('spellbookserver.LOG')
    def test_transcribe_file_too_large(self, mock_log, mock_magic_cls, mock_max, mock_ext, mock_enable, mock_req):
        mock_req.method = 'POST'
        mock_file = MagicMock()
        mock_file.filename = 'test.mp3'
        mock_file.file.read.return_value = b'x' * 200
        mock_req.files.get.return_value = mock_file
        mock_mime = MagicMock()
        mock_mime.from_buffer.return_value = 'audio/mpeg'
        mock_magic_cls.return_value = mock_mime
        result = SpellbookRESTAPI.transcribe()
        assert '413' in str(result.status)

    @patch('spellbookserver.request')
    @patch('spellbookserver.time.time', side_effect=[1000.0, 1001.0])
    @patch('spellbookserver.get_enable_transcribe', return_value=True)
    @patch('spellbookserver.get_allowed_extensions_transcribe', return_value='mp3')
    @patch('spellbookserver.get_max_file_size_transcribe', return_value=1000000)
    @patch('spellbookserver.magic.Magic')
    @patch('spellbookserver.LOG')
    def test_transcribe_success(self, mock_log, mock_magic_cls, mock_max, mock_ext, mock_enable, mock_time, mock_req):
        mock_req.method = 'POST'
        mock_file = MagicMock()
        mock_file.filename = 'test.mp3'
        mock_file.file.read.return_value = b'audio_data'
        mock_req.files.get.return_value = mock_file
        mock_mime = MagicMock()
        mock_mime.from_buffer.return_value = 'audio/mpeg'
        mock_magic_cls.return_value = mock_mime

        mock_segment1 = MagicMock()
        mock_segment1.start = 0.0
        mock_segment1.end = 1.0
        mock_segment1.text = 'Hello world'

        with patch('spellbookserver.WHISPER_MODEL') as mock_whisper:
            mock_whisper.transcribe.return_value = ([mock_segment1], MagicMock())
            result = SpellbookRESTAPI.transcribe()
            assert result['full_text'] == 'Hello world'
            assert result['calculation_time'] == 1.0
            assert len(result['segments']) == 1

    @patch('spellbookserver.request')
    @patch('spellbookserver.get_enable_transcribe', return_value=True)
    @patch('spellbookserver.get_allowed_extensions_transcribe', return_value='mp3,mp4')
    @patch('spellbookserver.get_max_file_size_transcribe', return_value=1000000)
    @patch('spellbookserver.magic.Magic')
    @patch('spellbookserver.os.path.exists', return_value=False)
    @patch('spellbookserver.os.remove')
    @patch('spellbookserver.convert_aac_to_opus')
    @patch('spellbookserver.LOG')
    def test_transcribe_mp4_conversion(self, mock_log, mock_convert, mock_remove, mock_exists, mock_magic_cls, mock_max, mock_ext, mock_enable, mock_req):
        mock_req.method = 'POST'
        mock_file = MagicMock()
        mock_file.filename = 'test.mp4'
        mock_file.file.read.return_value = b'video_data'
        mock_req.files.get.return_value = mock_file
        mock_mime = MagicMock()
        mock_mime.from_buffer.return_value = 'video/mp4'
        mock_magic_cls.return_value = mock_mime

        mock_segment1 = MagicMock()
        mock_segment1.start = 0.0
        mock_segment1.end = 2.0
        mock_segment1.text = 'Converted audio'

        with patch('spellbookserver.WHISPER_MODEL') as mock_whisper, \
             patch('builtins.open', mock_open(read_data=b'opus_data')):
            mock_whisper.transcribe.return_value = ([mock_segment1], MagicMock())
            result = SpellbookRESTAPI.transcribe()
            mock_convert.assert_called_once()
            assert result['full_text'] == 'Converted audio'

    @patch('spellbookserver.request')
    @patch('spellbookserver.get_enable_transcribe', return_value=True)
    @patch('spellbookserver.get_allowed_extensions_transcribe', return_value='mp3,mp4')
    @patch('spellbookserver.get_max_file_size_transcribe', return_value=1000000)
    @patch('spellbookserver.magic.Magic')
    @patch('spellbookserver.os.path.exists', return_value=True)
    @patch('spellbookserver.os.remove')
    @patch('spellbookserver.convert_aac_to_opus')
    @patch('spellbookserver.LOG')
    def test_transcribe_mp4_cleanup_old_files(self, mock_log, mock_convert, mock_remove, mock_exists, mock_magic_cls, mock_max, mock_ext, mock_enable, mock_req):
        """Test that old temp files are cleaned up before MP4 conversion (lines 875, 878)."""
        mock_req.method = 'POST'
        mock_file = MagicMock()
        mock_file.filename = 'test.mp4'
        mock_file.file.read.return_value = b'video_data'
        mock_req.files.get.return_value = mock_file
        mock_mime = MagicMock()
        mock_mime.from_buffer.return_value = 'video/mp4'
        mock_magic_cls.return_value = mock_mime

        mock_segment1 = MagicMock()
        mock_segment1.start = 0.0
        mock_segment1.end = 2.0
        mock_segment1.text = 'Converted audio'

        with patch('spellbookserver.WHISPER_MODEL') as mock_whisper, \
             patch('builtins.open', mock_open(read_data=b'opus_data')):
            mock_whisper.transcribe.return_value = ([mock_segment1], MagicMock())
            SpellbookRESTAPI.transcribe()
            # Verify old files were removed
            remove_calls = [str(c) for c in mock_remove.call_args_list]
            assert any('tmp_audio.mp3' in c for c in remove_calls)
            assert any('opus_audio.opus' in c for c in remove_calls)


class TestConvertAacToOpus:
    @patch('spellbookserver.subprocess.run')
    @patch('builtins.open', mock_open(read_data=b'data'))
    def test_convert_aac_to_opus(self, mock_subprocess):
        convert_aac_to_opus('input.mp3', 'output.opus')
        mock_subprocess.assert_called_once()
        args = mock_subprocess.call_args[0][0]
        assert 'ffmpeg' in args
        assert 'input.mp3' in args
        assert 'output.opus' in args


class TestInitializeRequestsLog:
    @patch('spellbookserver.RotatingFileHandler')
    @patch('spellbookserver.logging.getLogger')
    def test_initialize_requests_log(self, mock_get_logger, mock_handler):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        result = SpellbookRESTAPI.initialize_requests_log('/tmp/logs')
        assert result is mock_logger
        mock_handler.assert_called_once()
        mock_logger.addHandler.assert_called_once()
        mock_logger.setLevel.assert_called_once_with(logging.DEBUG)


class TestSSLWebServer:
    @patch('spellbookserver.LOG')
    def test_ssl_web_server_run(self, mock_log):
        """Test SSLWebServer.run starts CherryPy server with SSL adapter."""
        from spellbookserver import SSLWebServer
        adapter = SSLWebServer(host='0.0.0.0', port=443)
        with patch('cheroot.wsgi.Server') as mock_server_cls, \
             patch('cheroot.ssl.builtin.BuiltinSSLAdapter') as mock_ssl_adapter, \
             patch('spellbookserver.get_ssl_certificate', return_value='cert.pem'), \
             patch('spellbookserver.get_ssl_private_key', return_value='key.pem'), \
             patch('spellbookserver.get_ssl_certificate_chain', return_value=''):
            mock_server = MagicMock()
            mock_server_cls.return_value = mock_server
            adapter.run('handler')
            mock_server_cls.assert_called_once_with(('0.0.0.0', 443), 'handler')
            mock_ssl_adapter.assert_called_once()
            mock_server.start.assert_called_once()

    @patch('spellbookserver.LOG')
    def test_ssl_web_server_run_exception(self, mock_log):
        """Test SSLWebServer.run handles start exception."""
        from spellbookserver import SSLWebServer
        adapter = SSLWebServer(host='0.0.0.0', port=443)
        with patch('cheroot.wsgi.Server') as mock_server_cls, \
             patch('cheroot.ssl.builtin.BuiltinSSLAdapter'), \
             patch('spellbookserver.get_ssl_certificate', return_value='cert.pem'), \
             patch('spellbookserver.get_ssl_private_key', return_value='key.pem'), \
             patch('spellbookserver.get_ssl_certificate_chain', return_value=''):
            mock_server = MagicMock()
            mock_server.start.side_effect = Exception('bind failed')
            mock_server_cls.return_value = mock_server
            adapter.run('handler')
            mock_server.stop.assert_called_once()
            mock_log.error.assert_called_once()


class TestSpellbookInit:
    """Tests for SpellbookRESTAPI.__init__ to cover uncovered runtime paths."""

    @patch('spellbookserver.get_enable_ssl', return_value=False)
    @patch('spellbookserver.get_enable_wallet', return_value=False)
    @patch('spellbookserver.get_explorers', return_value={'blockstream': {}})
    @patch('spellbookserver.get_host', return_value='localhost')
    @patch('spellbookserver.get_port', return_value=8080)
    @patch('spellbookserver.os.path.isfile', return_value=True)
    @patch('bottle.Bottle.run')
    @patch('spellbookserver.LOG')
    def test_init_api_keys_not_present(self, mock_log, mock_run, mock_isfile, mock_port, mock_host, mock_explorers, mock_wallet, mock_ssl):
        """Test __init__ generates API keys when file doesn't exist (lines 113-114)."""
        mock_isfile.return_value = False
        with patch('spellbookserver.initialize_api_keys_file') as mock_init:
            SpellbookRESTAPI()
            mock_init.assert_called_once()

    @patch('spellbookserver.get_enable_ssl', return_value=False)
    @patch('spellbookserver.get_explorers', return_value={'blockstream': {}})
    @patch('spellbookserver.get_host', return_value='localhost')
    @patch('spellbookserver.get_port', return_value=8080)
    @patch('spellbookserver.os.path.isfile', return_value=True)
    @patch('bottle.Bottle.run')
    @patch('spellbookserver.LOG')
    @patch('spellbookserver.get_hot_wallet', side_effect=Exception('decryption failed'))
    @patch('spellbookserver.get_enable_wallet', return_value=True)
    def test_init_wallet_decryption_failure(self, mock_wallet, mock_get_wallet, mock_log, mock_run, mock_isfile, mock_port, mock_host, mock_explorers, mock_ssl):
        """Test __init__ handles hot wallet decryption failure (lines 120-123)."""
        with pytest.raises(SystemExit) as exc_info:
            SpellbookRESTAPI()
        assert exc_info.value.code == 1

    @patch('spellbookserver.get_enable_ssl', return_value=False)
    @patch('spellbookserver.get_enable_wallet', return_value=False)
    @patch('spellbookserver.get_explorers', return_value={})
    @patch('spellbookserver.get_host', return_value='localhost')
    @patch('spellbookserver.get_port', return_value=8080)
    @patch('spellbookserver.os.path.isfile', return_value=True)
    @patch('bottle.Bottle.run')
    @patch('spellbookserver.LOG')
    def test_init_no_explorers(self, mock_log, mock_run, mock_isfile, mock_port, mock_host, mock_explorers, mock_wallet, mock_ssl):
        """Test __init__ warns when no explorers configured (line 231)."""
        SpellbookRESTAPI()
        mock_log.warning.assert_called_once_with('No block explorers configured!')

    @patch('spellbookserver.get_enable_ssl', return_value=True)
    @patch('spellbookserver.get_enable_wallet', return_value=False)
    @patch('spellbookserver.get_explorers', return_value={'blockstream': {}})
    @patch('spellbookserver.get_host', return_value='localhost')
    @patch('spellbookserver.get_port', return_value=8080)
    @patch('spellbookserver.os.path.isfile', return_value=True)
    @patch('bottle.Bottle.run')
    @patch('spellbookserver.LOG')
    def test_init_ssl_enabled(self, mock_log, mock_run, mock_isfile, mock_port, mock_host, mock_explorers, mock_wallet, mock_ssl):
        """Test __init__ starts SSL server when enabled (line 236)."""
        SpellbookRESTAPI()
        mock_run.assert_called_once_with(host='localhost', port=8080, debug=False, server='sslwebserver')

    @patch('spellbookserver.get_enable_ssl', return_value=False)
    @patch('spellbookserver.get_enable_wallet', return_value=False)
    @patch('spellbookserver.get_explorers', return_value={'blockstream': {}})
    @patch('spellbookserver.get_host', return_value='localhost')
    @patch('spellbookserver.get_port', return_value=8080)
    @patch('spellbookserver.os.path.isfile', return_value=True)
    @patch('bottle.Bottle.run', side_effect=Exception('server crashed'))
    @patch('spellbookserver.get_mail_on_exception', return_value=False)
    @patch('spellbookserver.LOG')
    def test_init_server_exception_no_mail(self, mock_log, mock_mail, mock_run, mock_isfile, mock_port, mock_host, mock_explorers, mock_wallet, mock_ssl):
        """Test __init__ handles server exception without sending mail (lines 240-244)."""
        SpellbookRESTAPI()
        mock_log.error.assert_any_call('An exception occurred in the main loop: server crashed')

    @patch('spellbookserver.get_enable_ssl', return_value=False)
    @patch('spellbookserver.get_enable_wallet', return_value=False)
    @patch('spellbookserver.get_explorers', return_value={'blockstream': {}})
    @patch('spellbookserver.get_host', return_value='localhost')
    @patch('spellbookserver.get_port', return_value=8080)
    @patch('spellbookserver.os.path.isfile', return_value=True)
    @patch('bottle.Bottle.run', side_effect=Exception('server crashed'))
    @patch('spellbookserver.get_mail_on_exception', return_value=True)
    @patch('spellbookserver.get_notification_email', return_value='admin@test.com')
    @patch('spellbookserver.sendmail')
    @patch('spellbookserver.LOG')
    def test_init_server_exception_with_mail(self, mock_log, mock_sendmail, mock_email, mock_mail, mock_run, mock_isfile, mock_port, mock_host, mock_explorers, mock_wallet, mock_ssl):
        """Test __init__ handles server exception and sends mail (lines 240-253)."""
        SpellbookRESTAPI()
        mock_log.error.assert_any_call('An exception occurred in the main loop: server crashed')
        mock_sendmail.assert_called_once()


class TestMainBlock:
    """Tests for the main() function in spellbookserver.py."""

    @patch('spellbookserver.get_enable_ssl', return_value=False)
    @patch('spellbookserver.get_enable_wallet', return_value=False)
    @patch('spellbookserver.get_enable_transcribe', return_value=False)
    @patch('spellbookserver.get_explorers', return_value={'blockstream': {}})
    @patch('spellbookserver.get_host', return_value='localhost')
    @patch('spellbookserver.get_port', return_value=8080)
    @patch('bottle.Bottle.run')
    @patch('spellbookserver.argparse.ArgumentParser')
    @patch('spellbookserver.ConfigParser')
    @patch('spellbookserver.what_is_my_ip', return_value='1.2.3.4')
    @patch('spellbookserver.os.path.isfile', return_value=True)
    @patch('builtins.open', mock_open())
    @patch('spellbookserver.LOG')
    def test_main_with_empty_host(self, mock_log, mock_isfile, mock_ip, mock_config_cls, mock_parser_cls, mock_run, mock_port, mock_host, mock_explorers, mock_transcribe, mock_wallet, mock_ssl):
        """Test main() when host is empty (sets IP from what_is_my_ip)."""
        mock_config = MagicMock()
        mock_config.get.return_value = ''
        mock_config_cls.return_value = mock_config

        original_argv = sys.argv
        try:
            sys.argv = ['spellbookserver.py']
            srv.main()
        except SystemExit:
            pass
        finally:
            sys.argv = original_argv

        mock_config.set.assert_called_once_with(section='RESTAPI', option='host', value='1.2.3.4')

    @patch('spellbookserver.get_enable_ssl', return_value=False)
    @patch('spellbookserver.get_enable_wallet', return_value=False)
    @patch('spellbookserver.get_enable_transcribe', return_value=False)
    @patch('spellbookserver.get_explorers', return_value={'blockstream': {}})
    @patch('spellbookserver.get_host', return_value='localhost')
    @patch('spellbookserver.get_port', return_value=8080)
    @patch('bottle.Bottle.run')
    @patch('spellbookserver.argparse.ArgumentParser')
    @patch('spellbookserver.ConfigParser')
    @patch('spellbookserver.what_is_my_ip', return_value='1.2.3.4')
    @patch('spellbookserver.os.path.isfile', return_value=True)
    @patch('builtins.open', mock_open())
    @patch('spellbookserver.LOG')
    def test_main_with_host_set(self, mock_log, mock_isfile, mock_ip, mock_config_cls, mock_parser_cls, mock_run, mock_port, mock_host, mock_explorers, mock_transcribe, mock_wallet, mock_ssl):
        """Test main() when host is already set (no update needed)."""
        mock_config = MagicMock()
        mock_config.get.return_value = '192.168.1.1'
        mock_config_cls.return_value = mock_config

        original_argv = sys.argv
        try:
            sys.argv = ['spellbookserver.py']
            srv.main()
        except SystemExit:
            pass
        finally:
            sys.argv = original_argv

        mock_config.set.assert_not_called()
