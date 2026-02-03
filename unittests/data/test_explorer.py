#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from data.explorer import Explorer, ExplorerType


class TestExplorerType(object):
    """Tests for ExplorerType constants"""

    def test_explorer_type_constants(self):
        assert ExplorerType.BLOCKCHAIN_INFO == 'Blockchain.info'
        assert ExplorerType.BLOCKTRAIL_COM == 'Blocktrail.com'
        assert ExplorerType.INSIGHT == 'Insight'
        assert ExplorerType.CHAIN_SO == 'Chain.so'
        assert ExplorerType.BTC_COM == 'BTC.com'
        assert ExplorerType.BLOCKSTREAM == 'Blockstream.info'


class TestExplorer(object):
    """Tests for Explorer class"""

    def test_explorer_init(self):
        explorer = Explorer()
        assert explorer.api_key == ''
        assert explorer.url == ''
        assert explorer.explorer_type is None
        assert explorer.priority == 0
        assert explorer.testnet == False

    def test_explorer_json_encodable(self):
        explorer = Explorer()
        explorer.explorer_type = ExplorerType.BLOCKSTREAM
        explorer.priority = 1
        explorer.url = 'https://blockstream.info'
        explorer.api_key = 'test_key'
        explorer.testnet = True

        result = explorer.json_encodable()
        assert result['type'] == ExplorerType.BLOCKSTREAM
        assert result['priority'] == 1
        assert result['url'] == 'https://blockstream.info'
        assert result['api_key'] == 'test_key'
        assert result['testnet'] == True

    def test_explorer_json_encodable_defaults(self):
        explorer = Explorer()
        result = explorer.json_encodable()
        assert result['type'] is None
        assert result['priority'] == 0
        assert result['url'] == ''
        assert result['api_key'] == ''
        assert result['testnet'] == False
