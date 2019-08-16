#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import binascii

from .BIP39_test_vectors import BIP39_test_vectors, BIP39_test_vectors_japanese
from bips.BIP39 import get_seed

testvectors = [[testvector[1], 'TREZOR', testvector[2]] for testvector in BIP39_test_vectors['english']]
testvectors_japanese = [[testvector['mnemonic'], testvector['passphrase'], testvector['seed']] for testvector in BIP39_test_vectors_japanese]


class TestBIP39(object):
    def test_pytest(self):
        print('testing pytest...',)
        assert True

    @pytest.mark.parametrize('mnemonic, passphrase, seed', [testvector for testvector in testvectors])
    def test_mnemonic_to_seed(self, mnemonic, passphrase, seed):
        print('\nMnemonic: %s' % mnemonic)
        print('Passphrase: %s' % passphrase)
        print('expected seed (hex): %s' % seed)
        print('expected seed (bin): %s' % binascii.unhexlify(seed))

        assert get_seed(mnemonic=mnemonic, passphrase=passphrase) == binascii.unhexlify(seed)

    @pytest.mark.parametrize('mnemonic, passphrase, seed', [testvector for testvector in testvectors_japanese])
    def test_mnemonic_to_seed_japanese(self, mnemonic, passphrase, seed):
        print('\nMnemonic: %s' % mnemonic)
        print('Passphrase: %s' % passphrase)
        print('expected seed (hex): %s' % seed)
        print('expected seed (bin): %s' % binascii.unhexlify(seed))

        assert get_seed(mnemonic=mnemonic, passphrase=passphrase, language='japanese') == binascii.unhexlify(seed)
