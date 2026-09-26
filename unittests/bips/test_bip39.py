#!/usr/bin/env python
import binascii

import pytest

from bips.bip39 import get_seed

from .bip39_test_vectors import BIP39_test_vectors, BIP39_test_vectors_japanese

testvectors = [[testvector[1], 'TREZOR', testvector[2]] for testvector in BIP39_test_vectors['english']]
testvectors_japanese = [[testvector['mnemonic'], testvector['passphrase'], testvector['seed']] for testvector in BIP39_test_vectors_japanese]


class TestBIP39:
    def test_pytest(self):
        print('testing pytest...',)
        assert True

    @pytest.mark.parametrize('mnemonic, passphrase, seed', [testvector for testvector in testvectors])
    def test_mnemonic_to_seed(self, mnemonic, passphrase, seed):
        print(f'\nMnemonic: {mnemonic}')
        print(f'Passphrase: {passphrase}')
        print(f'expected seed (hex): {seed}')
        print(f'expected seed (bin): {binascii.unhexlify(seed)}')

        assert get_seed(mnemonic=mnemonic, passphrase=passphrase) == binascii.unhexlify(seed)

    @pytest.mark.parametrize('mnemonic, passphrase, seed', [testvector for testvector in testvectors_japanese])
    def test_mnemonic_to_seed_japanese(self, mnemonic, passphrase, seed):
        print(f'\nMnemonic: {mnemonic}')
        print(f'Passphrase: {passphrase}')
        print(f'expected seed (hex): {seed}')
        print(f'expected seed (bin): {binascii.unhexlify(seed)}')

        assert get_seed(mnemonic=mnemonic, passphrase=passphrase, language='japanese') == binascii.unhexlify(seed)
