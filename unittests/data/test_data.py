#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock

from data import data
from data.explorer import ExplorerType


class TestInitializeExplorersFile(object):
    """Tests for initialize_explorers_file function"""

    @mock.patch('data.data.save_to_json_file')
    def test_initialize_explorers_file(self, mock_save):
        data.initialize_explorers_file()
        mock_save.assert_called_once()
        saved_data = mock_save.call_args[0][1]
        assert 'blockstream.info' in saved_data
        assert 'btc.com' in saved_data
        assert 'blockchain.info' in saved_data
        assert saved_data['blockstream.info']['priority'] == 1
        assert saved_data['btc.com']['priority'] == 2
        assert saved_data['blockchain.info']['priority'] == 3


class TestGetExplorers(object):
    """Tests for get_explorers function"""

    @mock.patch('data.data.os.path.isfile', return_value=False)
    @mock.patch('data.data.initialize_explorers_file')
    @mock.patch('data.data.load_from_json_file')
    def test_get_explorers_file_not_exists(self, mock_load, mock_init, mock_isfile):
        mock_load.return_value = {'explorer1': {'priority': 2}, 'explorer2': {'priority': 1}}
        result = data.get_explorers()
        mock_init.assert_called_once()
        assert result == ['explorer2', 'explorer1']

    @mock.patch('data.data.os.path.isfile', return_value=True)
    @mock.patch('data.data.load_from_json_file')
    def test_get_explorers_file_exists(self, mock_load, mock_isfile):
        mock_load.return_value = {'explorer1': {'priority': 2}, 'explorer2': {'priority': 1}}
        result = data.get_explorers()
        assert result == ['explorer2', 'explorer1']

    @mock.patch('data.data.os.path.isfile', return_value=True)
    @mock.patch('data.data.load_from_json_file')
    def test_get_explorers_none(self, mock_load, mock_isfile):
        mock_load.return_value = None
        result = data.get_explorers()
        assert result is None

    @mock.patch('data.data.os.path.isfile', return_value=True)
    @mock.patch('data.data.load_from_json_file')
    def test_get_explorers_not_dict(self, mock_load, mock_isfile):
        mock_load.return_value = []
        result = data.get_explorers()
        assert result is None


class TestGetExplorerConfig(object):
    """Tests for get_explorer_config function"""

    @mock.patch('data.data.load_from_json_file')
    def test_get_explorer_config_exists(self, mock_load):
        mock_load.return_value = {'myexplorer': {'type': 'Blockstream.info', 'priority': 1}}
        result = data.get_explorer_config('myexplorer')
        assert result == {'type': 'Blockstream.info', 'priority': 1}

    @mock.patch('data.data.load_from_json_file')
    def test_get_explorer_config_not_exists(self, mock_load):
        mock_load.return_value = {'other': {'type': 'Blockstream.info', 'priority': 1}}
        result = data.get_explorer_config('myexplorer')
        assert result is None


class TestSaveExplorer(object):
    """Tests for save_explorer function"""

    @mock.patch('data.data.save_to_json_file')
    @mock.patch('data.data.load_from_json_file')
    def test_save_explorer_full_config(self, mock_load, mock_save):
        mock_load.return_value = {}
        config = {'type': 'Blockstream.info', 'url': 'https://example.com',
                  'priority': '1', 'api_key': 'key123', 'testnet': True}
        data.save_explorer('myexplorer', config)
        saved = mock_save.call_args[0][1]
        assert 'myexplorer' in saved
        assert saved['myexplorer']['type'] == 'Blockstream.info'
        assert saved['myexplorer']['url'] == 'https://example.com'
        assert saved['myexplorer']['priority'] == 1
        assert saved['myexplorer']['api_key'] == 'key123'
        assert saved['myexplorer']['testnet'] is True

    @mock.patch('data.data.save_to_json_file')
    @mock.patch('data.data.load_from_json_file')
    def test_save_explorer_partial_config(self, mock_load, mock_save):
        mock_load.return_value = {}
        config = {'type': 'BTC.com'}
        data.save_explorer('myexplorer', config)
        saved = mock_save.call_args[0][1]
        assert saved['myexplorer']['type'] == 'BTC.com'
        assert saved['myexplorer']['url'] == ''
        assert saved['myexplorer']['priority'] == 0


class TestDeleteExplorer(object):
    """Tests for delete_explorer function"""

    @mock.patch('data.data.save_to_json_file')
    @mock.patch('data.data.load_from_json_file')
    def test_delete_explorer_exists(self, mock_load, mock_save):
        mock_load.return_value = {'myexplorer': {'type': 'Blockstream.info'}, 'other': {'type': 'BTC.com'}}
        data.delete_explorer('myexplorer')
        saved = mock_save.call_args[0][1]
        assert 'myexplorer' not in saved
        assert 'other' in saved

    @mock.patch('data.data.save_to_json_file')
    @mock.patch('data.data.load_from_json_file')
    def test_delete_explorer_not_exists(self, mock_load, mock_save):
        mock_load.return_value = {'other': {'type': 'BTC.com'}}
        data.delete_explorer('nonexistent')
        mock_save.assert_not_called()


class TestGetExplorerAPI(object):
    """Tests for get_explorer_api function"""

    @mock.patch('data.data.load_from_json_file')
    def test_get_explorer_api_blockchain_info(self, mock_load):
        mock_load.return_value = {'test': {'type': ExplorerType.BLOCKCHAIN_INFO, 'testnet': False}}
        result = data.get_explorer_api('test')
        assert result is not None

    @mock.patch('data.data.load_from_json_file')
    def test_get_explorer_api_insight(self, mock_load):
        mock_load.return_value = {'test': {'type': ExplorerType.INSIGHT, 'url': 'http://example.com', 'testnet': False}}
        result = data.get_explorer_api('test')
        assert result is not None

    @mock.patch('data.data.load_from_json_file')
    def test_get_explorer_api_blocktrail(self, mock_load):
        mock_load.return_value = {'test': {'type': ExplorerType.BLOCKTRAIL_COM, 'api_key': 'key', 'testnet': False}}
        result = data.get_explorer_api('test')
        assert result is not None

    @mock.patch('data.data.load_from_json_file')
    def test_get_explorer_api_chainso(self, mock_load):
        mock_load.return_value = {'test': {'type': ExplorerType.CHAIN_SO, 'url': 'http://example.com', 'testnet': False}}
        result = data.get_explorer_api('test')
        assert result is not None

    @mock.patch('data.data.load_from_json_file')
    def test_get_explorer_api_btc_com(self, mock_load):
        mock_load.return_value = {'test': {'type': ExplorerType.BTC_COM, 'url': 'http://example.com', 'testnet': False}}
        result = data.get_explorer_api('test')
        assert result is not None

    @mock.patch('data.data.load_from_json_file')
    def test_get_explorer_api_blockstream(self, mock_load):
        mock_load.return_value = {'test': {'type': ExplorerType.BLOCKSTREAM, 'url': 'http://example.com', 'testnet': False}}
        result = data.get_explorer_api('test')
        assert result is not None

    @mock.patch('data.data.load_from_json_file')
    def test_get_explorer_api_unknown_type(self, mock_load):
        mock_load.return_value = {'test': {'type': 'UnknownExplorer', 'url': '', 'testnet': False}}
        with pytest.raises(NotImplementedError):
            data.get_explorer_api('test')

    @mock.patch('data.data.load_from_json_file')
    def test_get_explorer_api_not_found(self, mock_load):
        mock_load.return_value = {'other': {'type': ExplorerType.BLOCKSTREAM, 'url': '', 'testnet': False}}
        result = data.get_explorer_api('nonexistent')
        assert result is None


class TestQuery(object):
    """Tests for query function"""

    def setup_method(self, method):
        data.EXPLORER = None

    @mock.patch('data.data.get_explorer_api')
    @mock.patch('data.data.get_explorers')
    def test_query_block(self, mock_get_explorers, mock_get_api):
        mock_get_explorers.return_value = ['explorer1']
        mock_api = mock.MagicMock()
        mock_api.get_block.return_value = {'block': {'height': 100}}
        mock_get_api.return_value = mock_api
        result = data.query('block', [100])
        assert result == {'block': {'height': 100}}

    @mock.patch('data.data.get_explorer_api')
    @mock.patch('data.data.get_explorers')
    def test_query_block_by_height(self, mock_get_explorers, mock_get_api):
        mock_get_explorers.return_value = ['explorer1']
        mock_api = mock.MagicMock()
        mock_api.get_block_by_height.return_value = {'block': {'height': 100}}
        mock_get_api.return_value = mock_api
        result = data.query('block_by_height', [100])
        assert result == {'block': {'height': 100}}

    @mock.patch('data.data.get_explorer_api')
    @mock.patch('data.data.get_explorers')
    def test_query_block_by_hash(self, mock_get_explorers, mock_get_api):
        mock_get_explorers.return_value = ['explorer1']
        mock_api = mock.MagicMock()
        mock_api.get_block_by_hash.return_value = {'block': {'hash': 'abc'}}
        mock_get_api.return_value = mock_api
        result = data.query('block_by_hash', ['abc'])
        assert result == {'block': {'hash': 'abc'}}

    @mock.patch('data.data.get_explorer_api')
    @mock.patch('data.data.get_explorers')
    def test_query_latest_block(self, mock_get_explorers, mock_get_api):
        mock_get_explorers.return_value = ['explorer1']
        mock_api = mock.MagicMock()
        mock_api.get_latest_block.return_value = {'block': {'height': 100}}
        mock_get_api.return_value = mock_api
        result = data.query('latest_block', None)
        assert result == {'block': {'height': 100}}

    @mock.patch('data.data.get_explorer_api')
    @mock.patch('data.data.get_explorers')
    def test_query_transaction(self, mock_get_explorers, mock_get_api):
        mock_get_explorers.return_value = ['explorer1']
        mock_api = mock.MagicMock()
        mock_api.get_transaction.return_value = {'txid': 'abc'}
        mock_get_api.return_value = mock_api
        result = data.query('transaction', ['abc'])
        assert result == {'txid': 'abc'}

    @mock.patch('data.data.get_explorer_api')
    @mock.patch('data.data.get_explorers')
    def test_query_prime_input_address(self, mock_get_explorers, mock_get_api):
        mock_get_explorers.return_value = ['explorer1']
        mock_api = mock.MagicMock()
        mock_api.get_prime_input_address.return_value = {'address': 'addr1'}
        mock_get_api.return_value = mock_api
        result = data.query('prime_input_address', ['abc'])
        assert result == {'address': 'addr1'}

    @mock.patch('data.data.get_explorer_api')
    @mock.patch('data.data.get_explorers')
    def test_query_balance(self, mock_get_explorers, mock_get_api):
        mock_get_explorers.return_value = ['explorer1']
        mock_api = mock.MagicMock()
        mock_api.get_balance.return_value = {'balance': 100}
        mock_get_api.return_value = mock_api
        result = data.query('balance', ['addr'])
        assert result == {'balance': 100}

    @mock.patch('data.data.get_explorer_api')
    @mock.patch('data.data.get_explorers')
    def test_query_transactions(self, mock_get_explorers, mock_get_api):
        mock_get_explorers.return_value = ['explorer1']
        mock_api = mock.MagicMock()
        mock_api.get_transactions.return_value = {'transactions': []}
        mock_get_api.return_value = mock_api
        result = data.query('transactions', ['addr'])
        assert result == {'transactions': []}

    @mock.patch('data.data.get_explorer_api')
    @mock.patch('data.data.get_explorers')
    def test_query_utxos(self, mock_get_explorers, mock_get_api):
        mock_get_explorers.return_value = ['explorer1']
        mock_api = mock.MagicMock()
        mock_api.get_utxos.return_value = {'utxos': []}
        mock_get_api.return_value = mock_api
        result = data.query('utxos', ['addr', 3])
        assert result == {'utxos': []}

    @mock.patch('data.data.get_explorer_api')
    @mock.patch('data.data.get_explorers')
    def test_query_push_tx(self, mock_get_explorers, mock_get_api):
        mock_get_explorers.return_value = ['explorer1']
        mock_api = mock.MagicMock()
        mock_api.push_tx.return_value = {'success': True}
        mock_get_api.return_value = mock_api
        result = data.query('push_tx', ['rawtx'])
        assert result == {'success': True}

    @mock.patch('data.data.get_explorer_api')
    @mock.patch('data.data.get_explorers')
    def test_query_unknown_type(self, mock_get_explorers, mock_get_api):
        mock_get_explorers.return_value = ['explorer1']
        mock_api = mock.MagicMock()
        mock_get_api.return_value = mock_api
        with pytest.raises(NotImplementedError):
            data.query('unknown_type', ['param'])

    @mock.patch('data.data.get_explorer_api')
    @mock.patch('data.data.get_explorers')
    def test_query_error_fallback(self, mock_get_explorers, mock_get_api):
        mock_get_explorers.return_value = ['explorer1', 'explorer2']
        mock_api1 = mock.MagicMock()
        mock_api1.get_balance.return_value = {'error': 'failed'}
        mock_api2 = mock.MagicMock()
        mock_api2.get_balance.return_value = {'balance': 100}
        mock_get_api.side_effect = [mock_api1, mock_api2]
        result = data.query('balance', ['addr'])
        assert result == {'balance': 100}

    @mock.patch('data.data.get_explorer_api')
    @mock.patch('data.data.get_explorers')
    def test_query_all_explorers_fail(self, mock_get_explorers, mock_get_api):
        mock_get_explorers.return_value = ['explorer1', 'explorer2']
        mock_api = mock.MagicMock()
        mock_api.get_balance.return_value = {'error': 'failed'}
        mock_get_api.return_value = mock_api
        result = data.query('balance', ['addr'])
        assert 'error' in result
        assert 'Failed to retrieve data from all explorers' in result['error']

    @mock.patch('data.data.get_explorer_api')
    @mock.patch('data.data.get_explorers')
    def test_query_single_explorer_fail(self, mock_get_explorers, mock_get_api):
        mock_get_explorers.return_value = ['explorer1']
        mock_api = mock.MagicMock()
        mock_api.get_balance.return_value = {'error': 'failed'}
        mock_get_api.return_value = mock_api
        result = data.query('balance', ['addr'])
        assert 'error' in result
        assert 'explorer1 failed' in result['error']

    @mock.patch('data.data.get_explorer_api')
    @mock.patch('data.data.get_explorers')
    def test_query_with_specific_explorer(self, mock_get_explorers, mock_get_api):
        data.EXPLORER = 'specific_explorer'
        mock_api = mock.MagicMock()
        mock_api.get_balance.return_value = {'balance': 50}
        mock_get_api.return_value = mock_api
        result = data.query('balance', ['addr'])
        mock_get_explorers.assert_not_called()
        assert result == {'balance': 50}
        data.EXPLORER = None

    @mock.patch('data.data.get_explorer_api')
    @mock.patch('data.data.get_explorers')
    def test_query_param_defaults_to_list(self, mock_get_explorers, mock_get_api):
        mock_get_explorers.return_value = ['explorer1']
        mock_api = mock.MagicMock()
        mock_api.get_latest_block.return_value = {'block': {'height': 100}}
        mock_get_api.return_value = mock_api
        result = data.query('latest_block')
        assert result == {'block': {'height': 100}}

    @mock.patch('data.data.get_explorer_api')
    @mock.patch('data.data.get_explorers')
    def test_query_error_with_empty_param(self, mock_get_explorers, mock_get_api):
        mock_get_explorers.return_value = ['explorer1']
        mock_api = mock.MagicMock()
        mock_api.get_latest_block.return_value = {'error': 'fail'}
        mock_get_api.return_value = mock_api
        result = data.query('latest_block', '')
        assert 'error' in result


class TestWrapperFunctions(object):
    """Tests for wrapper functions (block, block_by_height, etc.)"""

    def setup_method(self, method):
        data.EXPLORER = None

    @mock.patch('data.data.query')
    def test_block(self, mock_query):
        data.block(100)
        mock_query.assert_called_once_with('block', [100])

    @mock.patch('data.data.query')
    def test_block_by_height(self, mock_query):
        data.block_by_height(100)
        mock_query.assert_called_once_with('block_by_height', [100])

    @mock.patch('data.data.query')
    def test_block_by_hash(self, mock_query):
        data.block_by_hash('abc')
        mock_query.assert_called_once_with('block_by_hash', ['abc'])

    @mock.patch('data.data.query')
    def test_latest_block(self, mock_query):
        data.latest_block()
        mock_query.assert_called_once_with('latest_block', None)

    @mock.patch('data.data.query')
    def test_transaction(self, mock_query):
        data.transaction('txid')
        mock_query.assert_called_once_with('transaction', ['txid'])

    @mock.patch('data.data.query')
    def test_prime_input_address(self, mock_query):
        data.prime_input_address('txid')
        mock_query.assert_called_once_with('prime_input_address', ['txid'])

    @mock.patch('data.data.query')
    def test_balance(self, mock_query):
        data.balance('addr')
        mock_query.assert_called_once_with('balance', ['addr'])

    @mock.patch('data.data.query')
    def test_utxos(self, mock_query):
        data.utxos('addr', 3)
        mock_query.assert_called_once_with('utxos', ['addr', 3])

    @mock.patch('data.data.query')
    def test_push_tx(self, mock_query):
        data.push_tx('rawtx')
        mock_query.assert_called_once_with('push_tx', ['rawtx'])

    @mock.patch('data.data.query')
    def test_transactions_valid_address(self, mock_query):
        mock_query.return_value = {'transactions': [{'block_height': 2, 'txid': 'b'}, {'block_height': 1, 'txid': 'a'}]}
        with mock.patch('data.data.valid_address', return_value=True):
            result = data.transactions('1validAddress')
        assert result['transactions'] == [{'block_height': 1, 'txid': 'a'}, {'block_height': 2, 'txid': 'b'}]

    @mock.patch('data.data.valid_address', return_value=False)
    def test_transactions_invalid_address(self, mock_valid):
        result = data.transactions('invalid')
        assert result['error'] == 'Invalid address'
        assert result['success'] == 0

    @mock.patch('data.data.query')
    def test_transactions_no_transactions_key(self, mock_query):
        mock_query.return_value = {'balance': 100}
        with mock.patch('data.data.valid_address', return_value=True):
            result = data.transactions('1validAddress')
        assert 'transactions' not in result


class TestExplorerGlobalFunctions(object):
    """Tests for set_explorer, clear_explorer, get_last_explorer"""

    def setup_method(self, method):
        data.EXPLORER = None

    def test_set_explorer(self):
        data.set_explorer('myexplorer')
        assert data.EXPLORER == 'myexplorer'

    def test_clear_explorer(self):
        data.EXPLORER = 'myexplorer'
        data.clear_explorer()
        assert data.EXPLORER is None

    def test_get_last_explorer(self):
        data.EXPLORER = 'myexplorer'
        assert data.get_last_explorer() == 'myexplorer'

    def test_get_last_explorer_none(self):
        data.EXPLORER = None
        assert data.get_last_explorer() is None
