#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from bips.BIP32 import set_chain_mode
from helpers.hotwallethelpers import get_address_from_wallet, get_private_key_from_wallet
from helpers.messagehelpers import verify_message, sign_message
from helpers.configurationhelpers import get_use_testnet


# Note if this test fails, check if openssl and ripemd160 are installed
# see: https://stackoverflow.com/questions/72409563/unsupported-hash-type-ripemd160-with-hashlib-in-python
# To quickly enable it, find the directory that holds your OpenSSL config file or a symlink to it, by running the below command:
#
# openssl version -d
# You can now go to the directory and edit the config file (it may be necessary to use sudo):
#
# nano openssl.cnf
# Make sure that the config file contains following lines (you might need to add the legacy bits):
#
# openssl_conf = openssl_init
#
# [openssl_init]
# providers = provider_sect
#
# [provider_sect]
# default = default_sect
# legacy = legacy_sect
#
# [default_sect]
# activate = 1
#
# [legacy_sect]
# activate = 1


class TestSignMessage(object):
    # For some reason there are multiple possible valid signatures, testing both the signatures found on the
    # https://github.com/stequald/bitcoin-sign-message readme as the ones that are actually calculated
    def test_verify_message_with_compressed_address_with_given_signature(self):
        address = '14dD6ygPi5WXdwwBTt1FBZK3aD8uDem1FY'
        message = 'test message'
        signature = 'IPn9bbEdNUp6+bneZqE2YJbq9Hv5aNILq9E5eZoMSF3/fBX4zjeIN6fpXfGSGPrZyKfHQ/c/kTSP+NIwmyTzMfk='
        assert verify_message(address=address, message=message, signature=signature)

    def test_verify_message_with_compressed_address_with_calculated_signature(self):
        address = '14dD6ygPi5WXdwwBTt1FBZK3aD8uDem1FY'
        message = 'test message'
        signature = 'ILiJ/1XP+t+RzA5P9opUjcS1Qu2FQ+YS2bATMes/BEphEmLfEXT3aOTrHateB68tUNvUFy3Nx/53tIOD74jCpy4='
        assert verify_message(address=address, message=message, signature=signature)

    def test_verify_message_with_compressed_address_with_another_calculated_signature(self):
        address = '14dD6ygPi5WXdwwBTt1FBZK3aD8uDem1FY'
        message = 'test message'
        signature = 'IHQfwue444Q4QaavxMKYsYv5kSTprtmoIf7g7eXuVNULbHBPSdjQ48mC/d05NZsjJO9Tpl+dWYqzmdbEpcKOvoQ='
        assert verify_message(address=address, message=message, signature=signature)

    def test_sign_message_with_compressed_address(self):
        address = '14dD6ygPi5WXdwwBTt1FBZK3aD8uDem1FY'
        private_key = 'L41XHGJA5QX43QRG3FEwPbqD5BYvy6WxUxqAMM9oQdHJ5FcRHcGk'
        message = 'test message'

        print('Address:', address)
        print('Message:', message)

        # signature keeps changing, sign_input_message both signs and verifies
        signature = sign_message(message, private_key)
        print('Signature:', signature)

        assert verify_message(address=address, message=message, signature=signature)

    def test_verify_message_with_uncompressed_address_with_given_signature(self):
        address = '1HUBHMij46Hae75JPdWjeZ5Q7KaL7EFRSD'
        message = 'test message'
        signature = 'G0k+Nt1u5boTTUfLyj6x1T5flg1v9rUKGlhs/jPApaTWLHf3GVdAIOIHip6sVwXEuzQGPWIlS0VT+yryXiDaavw='
        assert verify_message(address=address, message=message, signature=signature)

    def test_verify_message_with_uncompressed_address_with_calculated_signature(self):
        address = '1HUBHMij46Hae75JPdWjeZ5Q7KaL7EFRSD'
        message = 'test message'
        signature = 'HKhuLiH76s+z1CXhbvXxYyBNp/NNfGdivPku6RVvc22fV2rRxNcuKN+8H4fjvl7JR1fq4mw6GY8ayVpz/QGNxcE='
        assert verify_message(address=address, message=message, signature=signature)

    def test_sign_message_with_uncompressed_address(self):
        address = '1HUBHMij46Hae75JPdWjeZ5Q7KaL7EFRSD'
        private_key = '5KMWWy2d3Mjc8LojNoj8Lcz9B1aWu8bRofUgGwQk959Dw5h2iyw'
        message = 'test message'

        print('Address:', address)
        print('Message:', message)

        # signature keeps changing, sign_input_message both signs and verifies
        signature = sign_message(message, private_key)
        print('Signature:', signature)

        assert verify_message(address=address, message=message, signature=signature)

    def test_verify_message_with_address_and_sig_found_on_bitcointalk(self):
        address = '1BzFQocxr7QABTpwGz6o9Dsb6tPpBqbWZ8'
        message = 'This is harizen from bitcointalk.org. Today is February 1,2016.'
        signature = 'HyEuQEIIi5KS0dqyCaIWh6a5A3wIMFqkSEehuNa7jOUZTSyLa08czuASi5RUcj78hPI5PMNec0w6XhzflMbFNcM='
        assert verify_message(address=address, message=message, signature=signature)

    @pytest.mark.parametrize('index', range(1))
    def test_sign_message_with_addresses_from_hot_wallet(self, index):
        account = 0
        address = get_address_from_wallet(account=account, index=index)
        private_key = get_private_key_from_wallet(account=account, index=index)[address]
        message = 'This is a test message'

        print('Address:', address)
        print('Message:', message)

        signature = sign_message(message, private_key)
        print('Signature:', signature)

        assert verify_message(address=address, message=message, signature=signature)

    def test_verify_message_with_wrong_message(self):
        address = '14dD6ygPi5WXdwwBTt1FBZK3aD8uDem1FY'
        message = 'wrong message'
        signature = 'IPn9bbEdNUp6+bneZqE2YJbq9Hv5aNILq9E5eZoMSF3/fBX4zjeIN6fpXfGSGPrZyKfHQ/c/kTSP+NIwmyTzMfk='
        assert not verify_message(address=address, message=message, signature=signature)

    def test_verify_message_with_wrong_signature(self):
        address = '14dD6ygPi5WXdwwBTt1FBZK3aD8uDem1FY'
        message = 'test message'
        signature = 'G0k+Nt1u5boTTUfLyj6x1T5flg1v9rUKGlhs/jPApaTWLHf3GVdAIOIHip6sVwXEuzQGPWIlS0VT+yryXiDaavw='
        assert not verify_message(address=address, message=message, signature=signature)

    def test_verify_message_with_wrong_address(self):
        address = '1HUBHMij46Hae75JPdWjeZ5Q7KaL7EFRSD'
        message = 'test message'
        signature = 'IPn9bbEdNUp6+bneZqE2YJbq9Hv5aNILq9E5eZoMSF3/fBX4zjeIN6fpXfGSGPrZyKfHQ/c/kTSP+NIwmyTzMfk='
        assert not verify_message(address=address, message=message, signature=signature)

    def test_verify_message_with_testnet_address(self):
        if get_use_testnet() is False:
            print('Change configuration to use testnet to test this!!')
            return

        address = 'n2xqSGhqeQqiC6rp34NmPF8xmjQrcxLc6K'
        message = 'This is a test message for verification of n2xq'
        signature = 'H4NTp6Z3RWVndpmapw3sJ/CZd0jDS0evgQxasAN+hn3KGhoMLNvzs1Ms3nvPAqdf04XG3O6A4QmmIi70y14Lh18='
        assert verify_message(address=address, message=message, signature=signature)

    @pytest.mark.parametrize('index', range(1))
    def test_sign_message_with_addresses_from_hot_wallet_in_testnet_mode(self, index):
        set_chain_mode(mainnet=False)
        account = 0
        address = get_address_from_wallet(account=account, index=index)
        private_key = get_private_key_from_wallet(account=account, index=index)[address]
        message = 'This is a test message'

        print('Address:', address)
        print('Message:', message)

        signature = sign_message(message, private_key)
        print('Signature:', signature)

        assert verify_message(address=address, message=message, signature=signature)

    def test_sign_message_with_a_message_of_256_chars(self):
        address = get_address_from_wallet(account=0, index=0)
        message = ''.join(['a' for _ in range(255)])
        private_key = get_private_key_from_wallet(account=0, index=0)[address]

        signature = sign_message(message, private_key)
        print('Signature:', signature)

        assert verify_message(address=address, message=message, signature=signature)
