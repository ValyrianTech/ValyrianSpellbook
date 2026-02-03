#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
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
        assert api.testnet == False

    def test_explorer_api_init_with_params(self):
        api = ConcreteExplorerAPI(url='https://test.com', key='api_key', testnet=True)
        assert api.url == 'https://test.com'
        assert api.key == 'api_key'
        assert api.testnet == True

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
