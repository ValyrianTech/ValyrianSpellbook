#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import binascii

from .BIP32_test_vectors import bip32_test_vectors
from .BIP39_test_vectors import BIP39_test_vectors, BIP39_test_vectors_japanese

from bips.BIP32 import (
    parse_derivation_path,
    get_xpriv,
    get_xpub,
    get_xpub_child,
    set_chain_mode,
    bip32_master_key,
    bip32_ckd,
    bip32_serialize,
    bip32_deserialize,
    raw_bip32_ckd,
    hash_to_int,
    bip32_privtopub,
    bip32_extract_key,
    HARDENED,
    MAINNET_PRIVATE,
    TESTNET_PRIVATE,
)
from helpers.configurationhelpers import get_use_testnet

# Test vectors from BIP39 and BIP32 specifications
testvectors = [[testvector[2], testvector[3]] for testvector in BIP39_test_vectors['english']]
testvectors_japanese = [[testvector['seed'], testvector['bip32_xprv']] for testvector in BIP39_test_vectors_japanese]
xpriv_testvectors = [[vector['seed'], vector['derivation_path'], vector['xpriv']] for vector in bip32_test_vectors]
xpub_testvectors = [[vector['seed'], vector['derivation_path'], vector['xpub']] for vector in bip32_test_vectors]


def setup_module(module):
    """Setup: ensure mainnet mode for consistent test results"""
    set_chain_mode(mainnet=True)


def teardown_module(module):
    """Teardown: restore chain mode based on configuration"""
    set_chain_mode(mainnet=(get_use_testnet() is False))


class TestBIP32(object):
    """Tests for BIP32 using official test vectors"""

    @pytest.mark.parametrize('seed, xpriv', [testvector for testvector in testvectors])
    def test_get_master_key(self, seed, xpriv):
        print('\nseed (hex): %s' % seed)
        print('seed (bin): %s' % binascii.unhexlify(seed))
        print('expected xpriv: %s' % xpriv)

        assert bip32_master_key(seed=binascii.unhexlify(seed), vbytes=b'\x04\x88\xAD\xE4') == xpriv

    @pytest.mark.parametrize('derivation_path, expected', [
        ["m", []],
        ["m/0", [0]],
        ["m/0'", [(2 ** 31)]],
        ["m/44'/0", [44 + (2 ** 31), 0]],
        ["m/44'/0'", [44 + (2 ** 31), (2 ** 31)]],
        ["m/44'/1", [44 + (2 ** 31), 1]],
        ["m/44'/1'", [44 + (2 ** 31), 1+(2 ** 31)]],
        ["m/44'/0/0", [44 + (2 ** 31), 0, 0]],
        ["m/44'/0'/0", [44 + (2 ** 31), (2 ** 31), 0]],
        ["m/44'/0/1", [44 + (2 ** 31), 0, 1]],
        ["m/44'/0'/1", [44 + (2 ** 31), (2 ** 31), 1]],
        ["m/44'/0/0'", [44 + (2 ** 31), 0, (2 ** 31)]],
        ["m/44'/0'/0'", [44 + (2 ** 31), (2 ** 31), (2 ** 31)]],
        ["m/44'/0/1'", [44 + (2 ** 31), 0, 1+(2 ** 31)]],
        ["m/44'/0'/1'", [44 + (2 ** 31), (2 ** 31), 1+(2 ** 31)]],
        ["m/44'/1", [44 + (2 ** 31), 1]],
        ["m/44'/1'", [44 + (2 ** 31), 1 + (2 ** 31)]],
    ])
    def test_parse_derivation_path(self, derivation_path, expected):
        print('\nderivation path: %s' % derivation_path)
        print('expected: %s' % expected)

        assert parse_derivation_path(derivation_path=derivation_path) == expected

    @pytest.mark.parametrize('seed, derivation_path, xpriv', [testvector for testvector in xpriv_testvectors])
    def test_get_xpriv(self, seed, derivation_path, xpriv):
        print('\nseed: %s' % seed)
        print('derivation path: %s' % derivation_path)
        print('expected xpriv: %s' % xpriv)

        assert get_xpriv(seed=binascii.unhexlify(seed), derivation_path=derivation_path) == xpriv

    @pytest.mark.parametrize('seed, derivation_path, xpub', [testvector for testvector in xpub_testvectors])
    def test_get_xpub(self, seed, derivation_path, xpub):
        print('\nseed: %s' % seed)
        print('derivation path: %s' % derivation_path)
        print('expected xpub: %s' % xpub)

        assert get_xpub(seed=binascii.unhexlify(seed), derivation_path=derivation_path) == xpub

    def test_get_xpub_child(self):
        # Test if a xpub derived from another xpub is the same as if it would be derived from a seed
        seed = '000102030405060708090a0b0c0d0e0f'
        derivation_path = 'm/0'
        xpub = get_xpub(seed=binascii.unhexlify(seed), derivation_path=derivation_path)

        child_derivation_path = 'm/0/0'
        assert get_xpub_child(xpub=xpub, child_index=0) == get_xpub(seed=binascii.unhexlify(seed), derivation_path=child_derivation_path)


class TestBIP32Additional(object):
    """Additional tests for BIP32 to cover remaining lines"""

    def test_parse_derivation_path_invalid(self):
        """Test that invalid derivation paths raise an exception"""
        with pytest.raises(Exception) as excinfo:
            parse_derivation_path("invalid/path")
        assert 'Derivation path is invalid' in str(excinfo.value)

    def test_get_xpub_child_hardened_raises(self):
        """Test that hardened child derivation from xpub raises an exception"""
        seed = '000102030405060708090a0b0c0d0e0f'
        xpub = get_xpub(seed=binascii.unhexlify(seed), derivation_path='m')
        
        with pytest.raises(Exception) as excinfo:
            get_xpub_child(xpub=xpub, child_index=HARDENED)
        assert "non-hardened" in str(excinfo.value).lower()

    def test_bip32_deserialize_invalid_checksum(self):
        """Test that invalid checksum raises an exception"""
        # Create a valid key first
        seed = '000102030405060708090a0b0c0d0e0f'
        xpriv = get_xpriv(seed=binascii.unhexlify(seed), derivation_path='m')
        
        # Modify the last character to invalidate checksum
        if isinstance(xpriv, bytes):
            invalid_xpriv = xpriv[:-1] + b'X'
        else:
            invalid_xpriv = xpriv[:-1] + 'X'
        
        with pytest.raises(Exception) as excinfo:
            bip32_deserialize(invalid_xpriv)
        assert 'checksum' in str(excinfo.value).lower()

    def test_raw_bip32_ckd_public_hardened_raises(self):
        """Test that hardened derivation from public key raises an exception"""
        seed = '000102030405060708090a0b0c0d0e0f'
        xpub = get_xpub(seed=binascii.unhexlify(seed), derivation_path='m')
        
        # Try to do hardened derivation on public key
        with pytest.raises(Exception) as excinfo:
            bip32_ckd(xpub, HARDENED)
        assert "private derivation" in str(excinfo.value).lower()

    def test_hash_to_int_hex_40(self):
        """Test hash_to_int with 40-character hex string"""
        hex_40 = '0' * 40
        result = hash_to_int(hex_40)
        assert result == 0

    def test_hash_to_int_hex_64(self):
        """Test hash_to_int with 64-character hex string"""
        hex_64 = '0' * 64
        result = hash_to_int(hex_64)
        assert result == 0

    def test_hash_to_int_binary(self):
        """Test hash_to_int with binary data"""
        binary_data = b'\x00' * 32
        result = hash_to_int(binary_data)
        assert result == 0

    def test_set_chain_mode_mainnet(self):
        """Test setting chain mode to mainnet"""
        set_chain_mode(mainnet=True)
        # After setting mainnet, VERSION_BYTES should be MAINNET_PRIVATE
        from bips.BIP32 import VERSION_BYTES, MAGICBYTE
        assert VERSION_BYTES == MAINNET_PRIVATE
        assert MAGICBYTE == 0

    def test_set_chain_mode_testnet(self):
        """Test setting chain mode to testnet"""
        set_chain_mode(mainnet=False)
        from bips.BIP32 import VERSION_BYTES, MAGICBYTE
        assert VERSION_BYTES == TESTNET_PRIVATE
        assert MAGICBYTE == 111
        # Restore mainnet
        set_chain_mode(mainnet=True)

    def test_bip32_extract_key(self):
        """Test extracting key from serialized data"""
        seed = '000102030405060708090a0b0c0d0e0f'
        xpriv = get_xpriv(seed=binascii.unhexlify(seed), derivation_path='m')
        key = bip32_extract_key(xpriv)
        assert key is not None
        assert len(key) > 0

    def test_bip32_privtopub(self):
        """Test converting private key to public key"""
        seed = '000102030405060708090a0b0c0d0e0f'
        xpriv = get_xpriv(seed=binascii.unhexlify(seed), derivation_path='m')
        xpub = bip32_privtopub(xpriv)
        
        # xpub should start with 'xpub'
        if isinstance(xpub, bytes):
            assert xpub.startswith(b'xpub')
        else:
            assert xpub.startswith('xpub')
