#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for bitcoinwand.py — CLI for signing Bitcoin messages and sending
signed POST requests.

bitcoinwand.py runs argparse and all logic at module level. We patch
sys.argv and all external dependencies before importing via importlib,
following the same pattern as test_spellbook.py.
"""
import importlib.util
import os
import sys

import mock
import pytest

_BITCOINWAND_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bitcoinwand.py')

VALID_ADDRESS = '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2'
PRIVATE_KEY = 'L4rK1yDtCWekvXuE6oXD9jCYZgns3P4LpMxWqBk5J9aY='


def _import_bitcoinwand(message='hello', valid_addr=True, find_wallet=(0, 0), isfile=False, message_hash=None):
    """Import bitcoinwand with mocked dependencies. Returns the module object."""
    if 'bitcoinwand' in sys.modules:
        del sys.modules['bitcoinwand']

    mock_response = mock.Mock()
    mock_response.text = 'OK'

    patches = [
        mock.patch('sys.argv', ['bitcoinwand.py', VALID_ADDRESS, message, 'http://example.com']),
        mock.patch('validators.validators.valid_address', return_value=valid_addr),
        mock.patch('helpers.hotwallethelpers.find_address_in_wallet', return_value=find_wallet),
        mock.patch('helpers.hotwallethelpers.get_private_key_from_wallet',
                   return_value={VALID_ADDRESS: PRIVATE_KEY}),
        mock.patch('os.path.isfile', return_value=isfile),
        mock.patch('helpers.messagehelpers.sign_message', return_value='signature'),
        mock.patch('requests.post', return_value=mock_response),
    ]

    if message_hash is not None:
        patches.append(mock.patch('helpers.ipfshelpers.add_json', return_value=message_hash))

    for p in patches:
        p.start()

    try:
        spec = importlib.util.spec_from_file_location('bitcoinwand', _BITCOINWAND_PATH)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sys.modules['bitcoinwand'] = mod
        return mod
    finally:
        for p in patches:
            p.stop()


class TestBitcoinwandImport:

    def test_import_with_short_message(self):
        mod = _import_bitcoinwand(message='hello')
        assert mod.args.address == VALID_ADDRESS
        assert mod.args.message == 'hello'
        assert mod.args.url == 'http://example.com'

    def test_data_contains_address(self):
        mod = _import_bitcoinwand(message='hello')
        assert mod.data['address'] == VALID_ADDRESS

    def test_data_contains_message(self):
        mod = _import_bitcoinwand(message='hello')
        assert mod.data['message'] == 'hello'

    def test_data_contains_signature(self):
        mod = _import_bitcoinwand(message='hello')
        assert mod.data['signature'] == 'signature'

    def test_parser_has_address_argument(self):
        mod = _import_bitcoinwand(message='hello')
        actions = {a.dest for a in mod.parser._actions}
        assert 'address' in actions

    def test_parser_has_message_argument(self):
        mod = _import_bitcoinwand(message='hello')
        actions = {a.dest for a in mod.parser._actions}
        assert 'message' in actions

    def test_parser_has_url_argument(self):
        mod = _import_bitcoinwand(message='hello')
        actions = {a.dest for a in mod.parser._actions}
        assert 'url' in actions


class TestBitcoinwandInvalidAddress:

    def test_invalid_address_exits(self):
        with pytest.raises(SystemExit):
            _import_bitcoinwand(message='hello', valid_addr=False)


class TestBitcoinwandAddressNotFound:

    def test_address_not_found_exits(self):
        with pytest.raises(SystemExit):
            _import_bitcoinwand(message='hello', find_wallet=(None, None))


class TestBitcoinwandLongMessage:

    def test_long_message_uses_ipfs(self):
        long_message = 'A' * 300
        mod = _import_bitcoinwand(message=long_message, message_hash='QmHash123')
        assert mod.data['message'] == '/ipfs/QmHash123'

    def test_long_message_signature_still_set(self):
        long_message = 'A' * 300
        mod = _import_bitcoinwand(message=long_message, message_hash='QmHash123')
        assert mod.data['signature'] == 'signature'


class TestBitcoinwandFileMessage:

    def test_message_from_file(self):
        file_content = 'message from file'
        with mock.patch('builtins.open', new_callable=mock.mock_open, read_data=file_content):
            mod = _import_bitcoinwand(message='somefile.txt', isfile=True)
        assert mod.data['message'] == 'message from file'
