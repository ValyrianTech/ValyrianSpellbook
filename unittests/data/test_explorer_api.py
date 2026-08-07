#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mock

from data.explorer_api import ExplorerAPI


class ConcreteExplorerAPI(ExplorerAPI):
    """Concrete implementation of ExplorerAPI for testing"""

    def get_latest_block(self):
        return {'block': {'height': 100000}}

    def get_block_by_height(self, height):
        return {'block': {'height': height}}

    def get_block_by_hash(self, block_hash):
        return {'block': {'hash': block_hash}}

    def get_transactions(self, address):
        return []

    def get_balance(self, address):
        return 0

    def get_utxos(self, address, confirmations=3):
        return []

    def get_transaction(self, txid):
        return {}

    def get_prime_input_address(self, txid):
        return ''


class TestExplorerAPI(object):
    """Tests for ExplorerAPI abstract class"""

    def test_explorer_api_init(self):
        api = ConcreteExplorerAPI()
        assert api.error == ''
        assert api.url == ''
        assert api.key == ''
        assert not api.testnet

    def test_explorer_api_init_with_params(self):
        api = ConcreteExplorerAPI(url='https://test.com', key='api_key', testnet=True)
        assert api.url == 'https://test.com'
        assert api.key == 'api_key'
        assert api.testnet

    def test_get_block_by_height(self):
        api = ConcreteExplorerAPI()
        result = api.get_block(100)
        assert result['block']['height'] == 100

    def test_get_block_by_hash(self):
        api = ConcreteExplorerAPI()
        result = api.get_block('abc123')
        assert result['block']['hash'] == 'abc123'

    def test_get_latest_block_height(self):
        api = ConcreteExplorerAPI()
        result = api.get_latest_block_height()
        assert result == 100000

    def test_get_latest_block_height_missing_data(self):
        api = ConcreteExplorerAPI()
        api.get_latest_block = mock.MagicMock(return_value={})
        result = api.get_latest_block_height()
        assert result is None

    def test_get_latest_block_height_missing_block_key(self):
        api = ConcreteExplorerAPI()
        api.get_latest_block = mock.MagicMock(return_value={'error': 'fail'})
        result = api.get_latest_block_height()
        assert result is None

    def test_abstract_methods_return_none(self):
        """Test that the abstract method 'pass' bodies are reachable"""
        # In Python 3, __metaclass__ is ignored so ExplorerAPI can be instantiated directly
        api = ExplorerAPI()
        assert api.get_latest_block() is None
        assert api.get_block_by_height(100) is None
        assert api.get_block_by_hash('abc') is None
        assert api.get_transactions('addr') is None
        assert api.get_balance('addr') is None
        assert api.get_utxos('addr') is None
        assert api.get_transaction('txid') is None
        assert api.get_prime_input_address('txid') is None
