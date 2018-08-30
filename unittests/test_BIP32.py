#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import binascii

from BIP32_test_vectors import bip32_test_vectors
from BIP39_test_vectors import BIP39_test_vectors, BIP39_test_vectors_japanese

from bips.BIP32 import parse_derivation_path, get_xpriv, get_xpub, get_xpub_child, set_chain_mode

from pybitcointools import bip32_master_key

testvectors = [[testvector[2], testvector[3]] for testvector in BIP39_test_vectors['english']]
testvectors_japanese = [[testvector['seed'], testvector['bip32_xprv']] for testvector in BIP39_test_vectors_japanese]

xpriv_testvectors = [[vector['seed'], vector['derivation_path'], vector['xpriv']] for vector in bip32_test_vectors]
xpub_testvectors = [[vector['seed'], vector['derivation_path'], vector['xpub']] for vector in bip32_test_vectors]

# Set chain mode to mainnet (just in case the current configuration is set to use testnet)
set_chain_mode(mainnet=True)


class TestBIP32(object):
    @pytest.mark.parametrize('seed, xpriv', [testvector for testvector in testvectors])
    def test_get_master_key(self, seed, xpriv):
        print '\nseed (hex): %s' % seed
        print 'seed (bin): %s' % binascii.unhexlify(seed)
        print 'expected xpriv: %s' % xpriv

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
        print '\nderivation path: %s' % derivation_path
        print 'expected: %s' % expected

        assert parse_derivation_path(derivation_path=derivation_path) == expected

    @pytest.mark.parametrize('seed, derivation_path, xpriv', [testvector for testvector in xpriv_testvectors])
    def test_get_xpriv(self, seed, derivation_path, xpriv):
        print '\nseed: %s' % seed
        print 'derivation path: %s' % derivation_path
        print 'expected xpriv: %s' % xpriv

        assert get_xpriv(seed=binascii.unhexlify(seed), derivation_path=derivation_path) == xpriv

    @pytest.mark.parametrize('seed, derivation_path, xpub', [testvector for testvector in xpub_testvectors])
    def test_get_xpub(self, seed, derivation_path, xpub):
        print '\nseed: %s' % seed
        print 'derivation path: %s' % derivation_path
        print 'expected xpub: %s' % xpub

        assert get_xpub(seed=binascii.unhexlify(seed), derivation_path=derivation_path) == xpub

    def test_get_xpub_child(self):
        # Test if a xpub derived from another xpub is the same as if it would be derived from a seed
        seed = '000102030405060708090a0b0c0d0e0f'
        derivation_path = 'm/0'
        xpub = get_xpub(seed=binascii.unhexlify(seed), derivation_path=derivation_path)

        child_derivation_path = 'm/0/0'
        assert get_xpub_child(xpub=xpub, child_index=0) == get_xpub(seed=binascii.unhexlify(seed), derivation_path=child_derivation_path)
