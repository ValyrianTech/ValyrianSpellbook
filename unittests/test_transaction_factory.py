#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import binascii
from random import choice, randint


from transactionfactory import p2pkh_script, p2sh_script, p2wpkh_script, p2wsh_script, address_to_script
from transactionfactory import op_return_script, num_to_op_push
from data.transaction import TX

from helpers.py2specials import *
from helpers.py3specials import *


class TestTransactionFactory(object):
    @pytest.mark.parametrize('address, expected', [
        ["n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa", "76a914fa2d740fa4d0e741827035d642979f8feca285c988ac"],
        ["n4mLqhrbyJBAwgzfNxF8VSPeHB9nZksEtN", "76a914ff0389655fbebc32d5900d68706196647d2fc49a88ac"],
        ["msXXejbBboyVg9RetjZ3CfJRtboBmQ5kPv", "76a91483bd5aa4370bfe97064085e669c2ecb0cdb763c088ac"],
        ["1PYmZMCgKFKVth5W9kaRpdYq9Lf8eLQ95E", "76a914f754db62e6c344d82b66e69966f407367144a4e688ac"]
    ])
    def test_p2pkh_script(self, address, expected):
        assert p2pkh_script(address=address) == expected

    @pytest.mark.parametrize('address, expected', [
        ["2N9Wh4L1ZTZqFsUE8vpphfdQF6dyyrvTEgB", "a914b26ed940ba2f946929d14043006a37144b5a3f9a87"],
        ["2N4fu1VKjcv5TEZyWm7DCRcdRNAbotCKbLc", "a9147d53f08a51dbcaf525396b3ae66b9ad36b966df087"],
        ["36qa5uhG8qE9JFEYKnJ1fKgyfEPJA8Fx9i", "a9143876cdbcba1f0d15f1efc9073cb8be908e5958cf87"],
    ])
    def test_p2sh_script(self, address, expected):
        assert p2sh_script(address=address) == expected

    @pytest.mark.parametrize('address, expected', [
        ["tb1q8t5xu7arr35jwncf2qv2z7jl9ugq4ln3jy264z", "00143ae86e7ba31c69274f095018a17a5f2f100afe71"],
        ["bc1qnda5w4t7zp00hz79tylsa4kwhmda68puv82yav", "00149b7b47557e105efb8bc5593f0ed6cebedbdd1c3c"],
    ])
    def test_p2wpkh_script(self, address, expected):
        assert p2wpkh_script(address=address) == expected

    @pytest.mark.parametrize('address, expected', [
        ["tb1qwm0ujp48fsemspkgtly33fu8wx4t8sl32kqr4950rpdfhq8k95dsmk0fx2", "002076dfc906a74c33b806c85fc918a78771aab3c3f155803a968f185a9b80f62d1b"],
        ["bc1qlcnha82hwtualy7ky25mr8y2mkkj8r3lgfg299s47yhsxday4lms9zqnq8", "0020fe277e9d5772f9df93d622a9b19c8addad238e3f4250a29615f12f0337a4aff7"],
    ])
    def test_p2wsh_script(self, address, expected):
        assert p2wsh_script(address=address) == expected

    @pytest.mark.parametrize('address, expected', [
        ["n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa", "76a914fa2d740fa4d0e741827035d642979f8feca285c988ac"],
        ["n4mLqhrbyJBAwgzfNxF8VSPeHB9nZksEtN", "76a914ff0389655fbebc32d5900d68706196647d2fc49a88ac"],
        ["msXXejbBboyVg9RetjZ3CfJRtboBmQ5kPv", "76a91483bd5aa4370bfe97064085e669c2ecb0cdb763c088ac"],
        ["2N9Wh4L1ZTZqFsUE8vpphfdQF6dyyrvTEgB", "a914b26ed940ba2f946929d14043006a37144b5a3f9a87"],
        ["2N4fu1VKjcv5TEZyWm7DCRcdRNAbotCKbLc", "a9147d53f08a51dbcaf525396b3ae66b9ad36b966df087"],
        ["tb1q8t5xu7arr35jwncf2qv2z7jl9ugq4ln3jy264z", "00143ae86e7ba31c69274f095018a17a5f2f100afe71"],
        ["tb1qwm0ujp48fsemspkgtly33fu8wx4t8sl32kqr4950rpdfhq8k95dsmk0fx2", "002076dfc906a74c33b806c85fc918a78771aab3c3f155803a968f185a9b80f62d1b"],
        ["1PYmZMCgKFKVth5W9kaRpdYq9Lf8eLQ95E", "76a914f754db62e6c344d82b66e69966f407367144a4e688ac"],
        ["36qa5uhG8qE9JFEYKnJ1fKgyfEPJA8Fx9i", "a9143876cdbcba1f0d15f1efc9073cb8be908e5958cf87"],
        ["bc1qnda5w4t7zp00hz79tylsa4kwhmda68puv82yav", "00149b7b47557e105efb8bc5593f0ed6cebedbdd1c3c"],
        ["bc1qlcnha82hwtualy7ky25mr8y2mkkj8r3lgfg299s47yhsxday4lms9zqnq8", "0020fe277e9d5772f9df93d622a9b19c8addad238e3f4250a29615f12f0337a4aff7"],
    ])
    def test_address_to_script(self, address, expected):
        assert address_to_script(address=address) == expected

    def test_num_to_op_push(self):
        for num in range(1, 1024):
            op_push = binascii.hexlify(num_to_op_push(num))
            print('%s -> %s' % (num, op_push))
            # Todo add check length, there seems to be a bug with data longer than 255 chars, not really a problem because we don't allow more than the standard 80 chars (40 bytes)

    def test_op_return_script_with_strings_of_various_lengths(self):

        for x in range(1, 81):
            message = 'a' * x

            script = op_return_script(hex_data=binascii.hexlify(message.encode()).decode())
            print(message)
            print(script)

            assert TX().decode_op_return(hex_data=script) == message

    def test_op_return_script_with_random_string(self):

        for x in range(10000):
            print('')
            random_length = randint(1, 81)
            random_string = "".join(choice('abcdefghijklmnopqrstuvwxyz') for i in range(random_length))

            script = op_return_script(hex_data=binascii.hexlify(random_string.encode()).decode())
            print(random_string)
            print(script)

            assert TX().decode_op_return(hex_data=script) == random_string


