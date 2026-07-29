#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import binascii
import hashlib
from random import choice, randint

from transactionfactory import (
    p2pkh_script, p2sh_script, p2wpkh_script, p2wsh_script, address_to_script,
    op_return_script, num_to_op_push, add_op_return, serialize, deserialize,
    access, multiaccess, mktx, sign, is_inp, json_is_base, json_changebase,
    num_to_var_int, signature_form, serialize_script, serialize_script_unit,
    der_encode_sig, ecdsa_tx_sign, ecdsa_raw_sign, hash_to_int,
    deterministic_generate_k, bin_txhash, txhash, double_sha256,
    make_custom_tx, SIGHASH_ALL, SIGHASH_NONE, SIGHASH_SINGLE, SIGHASH_ANYONECANPAY,
)
from transactionfactory import is_python2
from helpers.privatekeyhelpers import privkey_to_pubkey, encode_privkey
from helpers.publickeyhelpers import pubkey_to_address
from helpers.py3specials import encode, safe_hexlify
from data.transaction import TX


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

    def test_num_to_op_push_zero(self):
        result = binascii.hexlify(num_to_op_push(0))
        assert result == b'00'

    def test_num_to_op_push_75(self):
        result = binascii.hexlify(num_to_op_push(75))
        assert result == b'4b'

    def test_num_to_op_push_76(self):
        result = binascii.hexlify(num_to_op_push(76))
        assert result == b'4c4c'

    def test_num_to_op_push_255(self):
        # 255 is not < 0xff (255), so it falls through to the 0xffff branch
        result = binascii.hexlify(num_to_op_push(255))
        assert result == b'4dff00'

    def test_num_to_op_push_256(self):
        result = binascii.hexlify(num_to_op_push(256))
        assert result == b'4d0001'

    def test_num_to_op_push_65535(self):
        # 65535 is not < 0xffff, so it falls through to the 0xffffffff branch
        result = binascii.hexlify(num_to_op_push(65535))
        assert result == b'4effff0000'

    def test_num_to_op_push_65536(self):
        result = binascii.hexlify(num_to_op_push(65536))
        assert result == b'4e00000100'

    def test_num_to_op_push_too_large(self):
        with pytest.raises(ValueError):
            num_to_op_push(0xffffffff)

    def test_op_return_script_non_string_raises(self):
        with pytest.raises(Exception, match='must be a string'):
            op_return_script(hex_data=123)

    def test_op_return_script_non_hex_raises(self):
        with pytest.raises(Exception, match='must be in hex format'):
            op_return_script(hex_data='xyz')

    def test_op_return_script_odd_length_raises(self):
        with pytest.raises(Exception, match='must be in hex format'):
            op_return_script(hex_data='abc')

    def test_add_op_return_no_tx(self):
        msg = 'hello'
        result = add_op_return(msg)
        expected = op_return_script(hex_data=binascii.hexlify(msg.encode()).decode())
        assert result == expected

    def test_add_op_return_with_hex_tx(self):
        msg = 'test'
        # Build a simple tx with mktx
        tx_hex = mktx({'output': 'a' * 64 + ':0'}, {'address': 'n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa', 'value': 50000})
        result = add_op_return(msg, tx_hex)
        # Verify the OP_RETURN was added by deserializing
        txo = deserialize(result)
        assert len(txo['outs']) == 2
        assert txo['outs'][-1]['script'][:2] == '6a'
        assert txo['outs'][-1]['value'] == 0

    def test_add_op_return_with_bytes_tx(self):
        # Bug in production code: re.match with string pattern on bytes raises TypeError
        msg = 'test'
        tx_hex = mktx({'output': 'a' * 64 + ':0'}, {'address': 'n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa', 'value': 50000})
        tx_bytes = binascii.unhexlify(tx_hex)
        with pytest.raises(TypeError):
            add_op_return(msg, tx_bytes)

    def test_add_op_return_with_dict_tx(self):
        # Bug in production code: re.match with string pattern on dict raises TypeError
        msg = 'test'
        tx_hex = mktx({'output': 'a' * 64 + ':0'}, {'address': 'n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa', 'value': 50000})
        txo = deserialize(tx_hex)
        with pytest.raises(TypeError):
            add_op_return(msg, txo)

    def test_add_op_return_existing_op_return_raises(self):
        msg = 'test'
        tx_hex = mktx({'output': 'a' * 64 + ':0'}, {'address': 'n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa', 'value': 50000})
        tx_with_op_return = add_op_return(msg, tx_hex)
        with pytest.raises(AssertionError):
            add_op_return('again', tx_with_op_return)

    def test_serialize_and_deserialize_roundtrip(self):
        tx_hex = mktx({'output': 'a' * 64 + ':0'}, {'address': 'n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa', 'value': 50000})
        txo = deserialize(tx_hex)
        reserialized = serialize(txo)
        assert reserialized == tx_hex

    def test_deserialize_hex_string(self):
        tx_hex = mktx({'output': 'a' * 64 + ':0'}, {'address': 'n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa', 'value': 50000})
        txo = deserialize(tx_hex)
        assert txo['version'] == 1
        assert len(txo['ins']) == 1
        assert len(txo['outs']) == 1
        assert txo['locktime'] == 0

    def test_deserialize_bytes(self):
        tx_hex = mktx({'output': 'a' * 64 + ':0'}, {'address': 'n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa', 'value': 50000})
        tx_bytes = binascii.unhexlify(tx_hex)
        txo = deserialize(tx_bytes)
        assert txo['version'] == 1
        assert len(txo['ins']) == 1
        assert len(txo['outs']) == 1

    def test_access_dict_direct(self):
        d = {'value': 100, 'script': 'abc'}
        assert access(d, 'value') == 100

    def test_access_dict_float_key(self):
        d = {1.0: 'float_val', 0: 'zero'}
        assert access(d, '1.0') == 'float_val'

    def test_access_dict_int_key(self):
        d = {0: 'zero', 1: 'one'}
        assert access(d, '1') == 'one'

    def test_access_list(self):
        lst = ['a', 'b', 'c']
        assert access(lst, '1') == 'b'

    def test_multiaccess(self):
        objs = [{'value': 10}, {'value': 20}, {'value': 30}]
        assert multiaccess(objs, 'value') == [10, 20, 30]

    def test_is_inp_long_string(self):
        assert is_inp('a' * 65) is True

    def test_is_inp_with_output_key(self):
        assert is_inp({'output': 'abc:0'}) is True

    def test_is_inp_with_outpoint_key(self):
        assert is_inp({'outpoint': {'hash': 'abc', 'index': 0}}) is True

    def test_is_inp_not_an_input(self):
        assert is_inp('short') is False

    def test_json_is_base_string_valid(self):
        assert json_is_base('abcdef', 16) is True

    def test_json_is_base_string_invalid_char(self):
        assert json_is_base('xyz', 16) is False

    def test_json_is_base_int(self):
        assert json_is_base(42, 16) is True

    def test_json_is_base_none(self):
        assert json_is_base(None, 16) is True

    def test_json_is_base_bytes(self):
        if not is_python2:
            assert json_is_base(b'hello', 16) is False

    def test_json_is_base_list_valid(self):
        assert json_is_base(['abc', '123'], 16) is True

    def test_json_is_base_list_invalid(self):
        assert json_is_base(['abc', 'xyz'], 16) is False

    def test_json_is_base_dict_valid(self):
        assert json_is_base({'key': 'abc', 'val': '123'}, 16) is True

    def test_json_is_base_dict_invalid(self):
        assert json_is_base({'key': 'xyz'}, 16) is False

    def test_json_changebase_string(self):
        result = json_changebase('48656c6c6f', lambda x: binascii.unhexlify(x))
        assert result == b'Hello'

    def test_json_changebase_int(self):
        assert json_changebase(42, lambda x: x) == 42

    def test_json_changebase_none(self):
        assert json_changebase(None, lambda x: x) is None

    def test_json_changebase_list(self):
        result = json_changebase(['48', '65'], lambda x: binascii.unhexlify(x))
        assert result == [b'H', b'e']

    def test_json_changebase_dict(self):
        result = json_changebase({'a': '48'}, lambda x: binascii.unhexlify(x))
        assert result == {'a': b'H'}

    def test_num_to_var_int_small(self):
        assert binascii.hexlify(num_to_var_int(100)) == b'64'

    def test_num_to_var_int_253(self):
        assert binascii.hexlify(num_to_var_int(253)) == b'fdfd00'

    def test_num_to_var_int_65536(self):
        assert binascii.hexlify(num_to_var_int(65536)) == b'fe00000100'

    def test_num_to_var_int_large(self):
        assert binascii.hexlify(num_to_var_int(4294967296)) == b'ff0000000001000000'


class TestAddressToScriptErrors:
    def test_invalid_bech32_length(self):
        with pytest.raises(Exception, match='Invalid version 0 bech32 address'):
            address_to_script('bc1qnda5w4t7zp00hz79tylsa4kwhmda68puv82yavx')


class TestSignatureForm:
    def setup_method(self):
        self.tx_hex = mktx({'output': 'a' * 64 + ':0'}, {'address': 'n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa', 'value': 50000})
        self.script = p2pkh_script('n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa')

    def test_signature_form_string_input(self):
        result = signature_form(self.tx_hex, 0, self.script, SIGHASH_ALL)
        assert isinstance(result, str)

    def test_signature_form_sighash_all(self):
        txo = deserialize(self.tx_hex)
        result = signature_form(txo, 0, self.script, SIGHASH_ALL)
        assert len(result['outs']) == 1
        assert result['ins'][0]['script'] == self.script

    def test_signature_form_sighash_none(self):
        txo = deserialize(self.tx_hex)
        result = signature_form(txo, 0, self.script, SIGHASH_NONE)
        assert result['outs'] == []

    def test_signature_form_sighash_single(self):
        txo = deserialize(self.tx_hex)
        result = signature_form(txo, 0, self.script, SIGHASH_SINGLE)
        assert len(result['outs']) == 1

    def test_signature_form_sighash_anyonecanpay(self):
        txo = deserialize(self.tx_hex)
        result = signature_form(txo, 0, self.script, SIGHASH_ANYONECANPAY)
        assert len(result['ins']) == 1
        assert result['ins'][0]['script'] == self.script


class TestSerializeScript:
    def test_serialize_script_with_hex_input(self):
        # When script is hex strings, json_is_base returns True and it gets converted
        script = ['48656c6c6f']
        result = serialize_script(script)
        # Should return hex string
        assert isinstance(result, str)

    def test_serialize_script_with_bytes(self):
        script = [b'Hello']
        result = serialize_script(script)
        assert isinstance(result, bytes)

    def test_serialize_script_unit_int_small(self):
        result = serialize_script_unit(5)
        assert result == bytes([5 + 80])

    def test_serialize_script_unit_int_large(self):
        result = serialize_script_unit(20)
        assert result == bytes([20])

    def test_serialize_script_unit_none(self):
        result = serialize_script_unit(None)
        assert result == b'\x00'

    def test_serialize_script_unit_short_bytes(self):
        data = b'\x01' * 10
        result = serialize_script_unit(data)
        assert result == bytes([10]) + data

    def test_serialize_script_unit_medium_bytes(self):
        data = b'\x01' * 100
        result = serialize_script_unit(data)
        assert result == bytes([76]) + bytes([100]) + data

    def test_serialize_script_unit_long_bytes(self):
        data = b'\x01' * 300
        result = serialize_script_unit(data)
        assert result == bytes([77]) + encode(len(data), 256, 2)[::-1] + data

    def test_serialize_script_unit_very_long_bytes(self):
        data = b'\x01' * 70000
        result = serialize_script_unit(data)
        assert result == bytes([78]) + encode(len(data), 256, 4)[::-1] + data


class TestEcdsaSign:
    PRIV = 12345

    def test_der_encode_sig(self):
        v, r, s = 27, 0x1, 0x2
        result = der_encode_sig(v, r, s)
        assert result.startswith('30')

    def test_der_encode_sig_with_leading_zero_r(self):
        v, r, s = 27, 0x89, 0x01
        result = der_encode_sig(v, r, s)
        # r starts with 89abcdef so should have 00 prepended
        assert '00' in result

    def test_der_encode_sig_with_leading_zero_s(self):
        v, r, s = 27, 0x01, 0x89
        result = der_encode_sig(v, r, s)
        assert '00' in result

    def test_ecdsa_raw_sign_uncompressed(self):
        priv = encode_privkey(self.PRIV, 'hex')
        msghash = hashlib.sha256(b'test message').digest()
        v, r, s = ecdsa_raw_sign(msghash, priv)
        assert 27 <= v <= 31
        assert r > 0
        assert s > 0

    def test_ecdsa_raw_sign_compressed(self):
        priv = encode_privkey(self.PRIV, 'hex_compressed')
        msghash = hashlib.sha256(b'test message').digest()
        v, r, s = ecdsa_raw_sign(msghash, priv)
        assert 31 <= v <= 35  # v + 4 for compressed

    def test_ecdsa_tx_sign(self):
        priv = encode_privkey(self.PRIV, 'hex')
        tx_hex = mktx({'output': 'a' * 64 + ':0'}, {'address': 'n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa', 'value': 50000})
        signing_tx = signature_form(tx_hex, 0, p2pkh_script('n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa'), SIGHASH_ALL)
        sig = ecdsa_tx_sign(signing_tx, priv, SIGHASH_ALL)
        assert isinstance(sig, str)
        assert sig.endswith('01')  # SIGHASH_ALL = 0x01


class TestHashFunctions:
    def test_hash_to_int_40_chars(self):
        h = 'a' * 40
        result = hash_to_int(h)
        assert isinstance(result, int)

    def test_hash_to_int_64_chars(self):
        h = 'a' * 64
        result = hash_to_int(h)
        assert isinstance(result, int)

    def test_hash_to_int_other_length(self):
        h = b'\x01' * 32
        result = hash_to_int(h)
        assert isinstance(result, int)

    def test_deterministic_generate_k(self):
        priv = encode_privkey(12345, 'hex')
        msghash = hashlib.sha256(b'test').digest()
        k = deterministic_generate_k(msghash, priv)
        assert isinstance(k, int)
        assert k > 0

    def test_bin_txhash(self):
        tx_hex = mktx({'output': 'a' * 64 + ':0'}, {'address': 'n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa', 'value': 50000})
        result = bin_txhash(tx_hex, SIGHASH_ALL)
        assert isinstance(result, bytes)
        assert len(result) == 32

    def test_txhash_without_hashcode(self):
        tx_hex = mktx({'output': 'a' * 64 + ':0'}, {'address': 'n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa', 'value': 50000})
        result = txhash(tx_hex)
        assert isinstance(result, str)
        assert len(result) == 64

    def test_txhash_with_hashcode(self):
        tx_hex = mktx({'output': 'a' * 64 + ':0'}, {'address': 'n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa', 'value': 50000})
        result = txhash(tx_hex, SIGHASH_ALL)
        assert isinstance(result, str)

    def test_txhash_bytes_input(self):
        tx_hex = mktx({'output': 'a' * 64 + ':0'}, {'address': 'n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa', 'value': 50000})
        tx_bytes = binascii.unhexlify(tx_hex)
        result = txhash(tx_bytes)
        assert isinstance(result, str)

    def test_double_sha256(self):
        result = double_sha256(b'hello')
        assert isinstance(result, str)
        assert len(result) == 64


class TestMktx:
    def test_mktx_with_list_args(self):
        ins = [{'output': 'a' * 64 + ':0'}]
        outs = [{'address': 'n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa', 'value': 50000}]
        tx_hex = mktx(ins, outs)
        assert isinstance(tx_hex, str)
        txo = deserialize(tx_hex)
        assert len(txo['ins']) == 1
        assert len(txo['outs']) == 1

    def test_mktx_with_individual_args(self):
        tx_hex = mktx({'output': 'a' * 64 + ':0'}, {'address': 'n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa', 'value': 50000})
        assert isinstance(tx_hex, str)

    def test_mktx_with_outpoint_dict(self):
        inp = {'outpoint': {'hash': 'a' * 64, 'index': 0}, 'script': '', 'sequence': 4294967295}
        tx_hex = mktx(inp, {'address': 'n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa', 'value': 50000})
        txo = deserialize(tx_hex)
        assert txo['ins'][0]['outpoint']['hash'] == 'a' * 64

    def test_mktx_with_string_output_address(self):
        tx_hex = mktx({'output': 'a' * 64 + ':0'}, 'n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa:50000')
        txo = deserialize(tx_hex)
        assert len(txo['outs']) == 1
        assert txo['outs'][0]['value'] == 50000

    def test_mktx_with_string_output_hex_script(self):
        tx_hex = mktx({'output': 'a' * 64 + ':0'}, '76a914' + 'b' * 40 + '88ac:50000')
        txo = deserialize(tx_hex)
        assert len(txo['outs']) == 1

    def test_mktx_with_script_output(self):
        tx_hex = mktx({'output': 'a' * 64 + ':0'}, {'script': '76a914' + 'b' * 40 + '88ac', 'value': 50000})
        txo = deserialize(tx_hex)
        assert len(txo['outs']) == 1

    def test_mktx_missing_address_and_script_raises(self):
        with pytest.raises(Exception, match="Could not find 'address' or 'script'"):
            mktx({'output': 'a' * 64 + ':0'}, {'value': 50000})


class TestSign:
    PRIV = 12345

    def setup_method(self):
        self.priv_hex = encode_privkey(self.PRIV, 'hex')
        self.pub = privkey_to_pubkey(self.priv_hex)
        self.address = pubkey_to_address(self.pub)
        self.tx_hex = mktx({'output': 'a' * 64 + ':0'}, {'address': self.address, 'value': 50000})

    def test_sign_hex_tx(self):
        result = sign(self.tx_hex, 0, self.priv_hex)
        assert isinstance(result, str)
        txo = deserialize(result)
        assert txo['ins'][0]['script'] != ''

    def test_sign_bytes_tx(self):
        # Bug in production code: isinstance(re, bytes) should be isinstance(tx, bytes)
        # re.match with string pattern on bytes raises TypeError
        tx_bytes = binascii.unhexlify(self.tx_hex)
        with pytest.raises(TypeError):
            sign(tx_bytes, 0, self.priv_hex)

    def test_sign_short_priv(self):
        priv_bin = encode_privkey(self.PRIV, 'bin')
        assert len(priv_bin) <= 33
        result = sign(self.tx_hex, 0, priv_bin)
        assert isinstance(result, str)


class TestMakeCustomTx:
    PRIV = 12345

    def setup_method(self):
        self.priv_hex = encode_privkey(self.PRIV, 'hex')
        self.pub = privkey_to_pubkey(self.priv_hex)
        self.address = pubkey_to_address(self.pub)
        self.tx_inputs = [{
            'address': self.address,
            'value': 60000,
            'output': 'a' * 64 + ':0',
            'confirmations': 1
        }]
        self.tx_outputs = [{
            'address': 'n4KmgAd3J7ubthHpe9vyLy2xyiVZpF7dPa',
            'value': 50000
        }]
        self.private_keys = {self.address: self.priv_hex}

    def test_make_custom_tx_valid(self):
        result = make_custom_tx(self.private_keys, self.tx_inputs, self.tx_outputs, tx_fee=10000)
        assert result is not None
        assert isinstance(result, str)

    def test_make_custom_tx_with_op_return(self):
        result = make_custom_tx(self.private_keys, self.tx_inputs, self.tx_outputs, tx_fee=10000, op_return_data='hello')
        assert result is not None
        txo = deserialize(result)
        # Should have 2 outputs: the payment + OP_RETURN
        assert len(txo['outs']) == 2

    def test_make_custom_tx_invalid_fee_type(self):
        # Bug in production code: %d format with string raises TypeError
        with pytest.raises(TypeError):
            make_custom_tx(self.private_keys, self.tx_inputs, self.tx_outputs, tx_fee='10000')

    def test_make_custom_tx_negative_fee(self):
        result = make_custom_tx(self.private_keys, self.tx_inputs, self.tx_outputs, tx_fee=-1)
        assert result is None

    def test_make_custom_tx_fee_mismatch(self):
        result = make_custom_tx(self.private_keys, self.tx_inputs, self.tx_outputs, tx_fee=9999)
        assert result is None

    def test_make_custom_tx_missing_key(self):
        result = make_custom_tx({}, self.tx_inputs, self.tx_outputs, tx_fee=10000)
        assert result is None

    def test_make_custom_tx_unconfirmed_no_zero_conf(self):
        inputs = [{
            'address': self.address,
            'value': 60000,
            'output': 'a' * 64 + ':0',
            'confirmations': 0
        }]
        result = make_custom_tx(self.private_keys, inputs, self.tx_outputs, tx_fee=10000)
        assert result is None

    def test_make_custom_tx_unconfirmed_with_zero_conf(self):
        inputs = [{
            'address': self.address,
            'value': 60000,
            'output': 'a' * 64 + ':0',
            'confirmations': 0
        }]
        result = make_custom_tx(self.private_keys, inputs, self.tx_outputs, tx_fee=10000, allow_zero_conf=True)
        assert result is not None

    def test_make_custom_tx_op_return_too_long(self):
        result = make_custom_tx(self.private_keys, self.tx_inputs, self.tx_outputs, tx_fee=10000, op_return_data='a' * 81)
        assert result is None


class TestDeserializeLargeVarInt:
    def test_deserialize_with_large_script_var_int(self):
        # Construct a tx with a script of 253 bytes to trigger var_int >= 253 path
        txobj = {
            "version": 1,
            "locktime": 0,
            "ins": [{
                "outpoint": {"hash": b'\x00' * 32, "index": 0},
                "script": b'\x00' * 253,
                "sequence": 4294967295
            }],
            "outs": [{
                "value": 0,
                "script": b'\x76\xa9\x14' + b'\x00' * 20 + b'\x88\xac'
            }]
        }
        tx_hex = safe_hexlify(serialize(txobj))
        txo = deserialize(tx_hex)
        assert len(txo['ins']) == 1
        assert len(txo['ins'][0]['script']) == 506  # 253 bytes hexlified = 506 chars


class TestSignatureFormSighashSingleMultiInput:
    def test_sighash_single_with_multiple_inputs(self):
        # With 2+ inputs, the SIGHASH_SINGLE branch iterates over outs[:ins-1]
        # and sets value/script to dummy values (lines 517-518)
        txobj = {
            "version": 1,
            "locktime": 0,
            "ins": [
                {"outpoint": {"hash": b'\x00' * 32, "index": 0}, "script": b'', "sequence": 4294967295},
                {"outpoint": {"hash": b'\x01' * 32, "index": 1}, "script": b'', "sequence": 4294967295},
            ],
            "outs": [
                {"value": 10000, "script": b'\x76\xa9\x14' + b'\x00' * 20 + b'\x88\xac'},
                {"value": 20000, "script": b'\x76\xa9\x14' + b'\x01' * 20 + b'\x88\xac'},
            ]
        }
        script = '76a914' + '00' * 20 + '88ac'
        result = signature_form(txobj, 0, script, SIGHASH_SINGLE)
        assert len(result['ins']) == 2
        # The first output should have been blanked out (value=2**64-1, script="")
        assert result['outs'][0]['value'] == 2**64 - 1
        assert result['outs'][0]['script'] == ""
