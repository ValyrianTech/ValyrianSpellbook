#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock

from bips.BIP44 import (
    get_address_from_xpub,
    get_addresses_from_xpub,
    get_change_addresses_from_xpub,
    get_xpriv_key,
    get_xpriv_keys,
    get_xpub_key,
    get_xpub_keys,
    get_private_key,
)
from bips.BIP32 import set_chain_mode
from helpers.configurationhelpers import get_use_testnet


# Test mnemonic (12 words) - this is a well-known test vector
TEST_MNEMONIC = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"


def setup_module(module):
    """Setup: ensure mainnet mode for consistent test results"""
    set_chain_mode(mainnet=True)


def teardown_module(module):
    """Teardown: restore chain mode based on configuration"""
    set_chain_mode(mainnet=(get_use_testnet() is False))


class TestBIP44(object):
    """Tests for BIP44 functions"""

    def test_get_xpriv_key(self):
        """Test getting an xpriv key from a mnemonic"""
        xpriv = get_xpriv_key(mnemonic=TEST_MNEMONIC, passphrase="", account=0)
        assert xpriv is not None
        assert isinstance(xpriv, (str, bytes))
        # xpriv keys start with 'xprv' on mainnet
        if isinstance(xpriv, bytes):
            assert xpriv.startswith(b'xprv')
        else:
            assert xpriv.startswith('xprv')

    def test_get_xpriv_key_with_passphrase(self):
        """Test getting an xpriv key with a passphrase"""
        xpriv_no_pass = get_xpriv_key(mnemonic=TEST_MNEMONIC, passphrase="", account=0)
        xpriv_with_pass = get_xpriv_key(mnemonic=TEST_MNEMONIC, passphrase="test", account=0)
        # Different passphrases should produce different keys
        assert xpriv_no_pass != xpriv_with_pass

    def test_get_xpriv_key_different_accounts(self):
        """Test getting xpriv keys for different accounts"""
        xpriv_0 = get_xpriv_key(mnemonic=TEST_MNEMONIC, passphrase="", account=0)
        xpriv_1 = get_xpriv_key(mnemonic=TEST_MNEMONIC, passphrase="", account=1)
        # Different accounts should produce different keys
        assert xpriv_0 != xpriv_1

    def test_get_xpriv_keys(self):
        """Test getting multiple xpriv keys"""
        xprivs = get_xpriv_keys(mnemonic=TEST_MNEMONIC, passphrase="", i=3)
        assert len(xprivs) == 3
        # All keys should be different
        assert len(set(xprivs)) == 3

    def test_get_xpub_key(self):
        """Test getting an xpub key from a mnemonic"""
        xpub = get_xpub_key(mnemonic=TEST_MNEMONIC, passphrase="", account=0)
        assert xpub is not None
        # xpub keys start with 'xpub' on mainnet
        if isinstance(xpub, bytes):
            assert xpub.startswith(b'xpub')
        else:
            assert xpub.startswith('xpub')

    def test_get_xpub_keys(self):
        """Test getting multiple xpub keys"""
        xpubs = get_xpub_keys(mnemonic=TEST_MNEMONIC, passphrase="", i=3)
        assert len(xpubs) == 3
        # All keys should be different
        assert len(set(xpubs)) == 3

    def test_get_address_from_xpub(self):
        """Test getting an address from an xpub key"""
        xpub = get_xpub_key(mnemonic=TEST_MNEMONIC, passphrase="", account=0)
        address = get_address_from_xpub(xpub=xpub, i=0)
        assert address is not None
        assert isinstance(address, str)
        # Bitcoin mainnet addresses start with 1 or 3
        assert address[0] in ['1', '3']

    def test_get_addresses_from_xpub(self):
        """Test getting multiple addresses from an xpub key"""
        xpub = get_xpub_key(mnemonic=TEST_MNEMONIC, passphrase="", account=0)
        addresses = get_addresses_from_xpub(xpub=xpub, i=5)
        assert len(addresses) == 5
        # All addresses should be different
        assert len(set(addresses)) == 5
        # All should be valid Bitcoin addresses
        for addr in addresses:
            assert addr[0] in ['1', '3']

    def test_get_change_addresses_from_xpub(self):
        """Test getting change addresses from an xpub key"""
        xpub = get_xpub_key(mnemonic=TEST_MNEMONIC, passphrase="", account=0)
        change_addresses = get_change_addresses_from_xpub(xpub=xpub, i=5)
        assert len(change_addresses) == 5
        # All addresses should be different
        assert len(set(change_addresses)) == 5
        # Change addresses should be different from regular addresses
        regular_addresses = get_addresses_from_xpub(xpub=xpub, i=5)
        for addr in change_addresses:
            assert addr not in regular_addresses

    def test_get_private_key(self):
        """Test getting a private key from an xpriv key"""
        xpriv = get_xpriv_key(mnemonic=TEST_MNEMONIC, passphrase="", account=0)
        private_keys = get_private_key(xpriv=xpriv, i=0, k=0)
        assert isinstance(private_keys, dict)
        assert len(private_keys) == 1
        # The key should be an address, the value should be a WIF key
        for address, wif in private_keys.items():
            assert address[0] in ['1', '3']
            # WIF keys start with 5, K, or L on mainnet
            assert wif[0] in ['5', 'K', 'L']

    def test_get_private_key_change(self):
        """Test getting a change private key from an xpriv key"""
        xpriv = get_xpriv_key(mnemonic=TEST_MNEMONIC, passphrase="", account=0)
        private_keys_normal = get_private_key(xpriv=xpriv, i=0, k=0)
        private_keys_change = get_private_key(xpriv=xpriv, i=0, k=1)
        # Change and normal keys should be different
        assert list(private_keys_normal.keys())[0] != list(private_keys_change.keys())[0]
