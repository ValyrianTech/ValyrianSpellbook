#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from helpers.publickeyhelpers import (
    get_pubkey_format, encode_pubkey, decode_pubkey,
    add_pubkeys, compress, pubkey_to_address, bin_hash160
)
from helpers.py3specials import from_int_to_byte


class TestGetPubkeyFormat(object):
    """Tests for get_pubkey_format function"""

    def test_get_pubkey_format_decimal(self):
        pub = (123, 456)
        result = get_pubkey_format(pub)
        assert result == 'decimal'

    def test_get_pubkey_format_decimal_list(self):
        pub = [123, 456]
        result = get_pubkey_format(pub)
        assert result == 'decimal'

    def test_get_pubkey_format_bin(self):
        # 65 bytes starting with 0x04
        pub = b'\x04' + b'\x00' * 64
        result = get_pubkey_format(pub)
        assert result == 'bin'

    def test_get_pubkey_format_hex(self):
        # 130 chars starting with '04'
        pub = '04' + '00' * 64
        result = get_pubkey_format(pub)
        assert result == 'hex'

    def test_get_pubkey_format_bin_compressed(self):
        # 33 bytes starting with 0x02 or 0x03
        pub = b'\x02' + b'\x00' * 32
        result = get_pubkey_format(pub)
        assert result == 'bin_compressed'

    def test_get_pubkey_format_bin_compressed_03(self):
        pub = b'\x03' + b'\x00' * 32
        result = get_pubkey_format(pub)
        assert result == 'bin_compressed'

    def test_get_pubkey_format_hex_compressed(self):
        # 66 chars starting with '02' or '03'
        pub = '02' + '00' * 32
        result = get_pubkey_format(pub)
        assert result == 'hex_compressed'

    def test_get_pubkey_format_hex_compressed_03(self):
        pub = '03' + '00' * 32
        result = get_pubkey_format(pub)
        assert result == 'hex_compressed'

    def test_get_pubkey_format_bin_electrum(self):
        # 64 bytes (no prefix)
        pub = b'\x00' * 64
        result = get_pubkey_format(pub)
        assert result == 'bin_electrum'

    def test_get_pubkey_format_hex_electrum(self):
        # 128 chars (no prefix)
        pub = '00' * 64
        result = get_pubkey_format(pub)
        assert result == 'hex_electrum'

    def test_get_pubkey_format_invalid(self):
        pub = 'invalid'
        with pytest.raises(Exception):
            get_pubkey_format(pub)


class TestEncodePubkey(object):
    """Tests for encode_pubkey function"""

    def test_encode_pubkey_decimal(self):
        pub = (123, 456)
        result = encode_pubkey(pub, 'decimal')
        assert result == (123, 456)

    def test_encode_pubkey_bin(self):
        pub = (123, 456)
        result = encode_pubkey(pub, 'bin')
        assert isinstance(result, bytes)
        assert len(result) == 65
        assert result[0] == 4

    def test_encode_pubkey_bin_compressed(self):
        pub = (123, 456)  # 456 is even
        result = encode_pubkey(pub, 'bin_compressed')
        assert isinstance(result, bytes)
        assert len(result) == 33
        assert result[0] == 2  # Even y

    def test_encode_pubkey_bin_compressed_odd(self):
        pub = (123, 457)  # 457 is odd
        result = encode_pubkey(pub, 'bin_compressed')
        assert result[0] == 3  # Odd y

    def test_encode_pubkey_hex(self):
        pub = (123, 456)
        result = encode_pubkey(pub, 'hex')
        assert isinstance(result, str)
        assert len(result) == 130
        assert result.startswith('04')

    def test_encode_pubkey_hex_compressed(self):
        pub = (123, 456)
        result = encode_pubkey(pub, 'hex_compressed')
        assert isinstance(result, str)
        assert len(result) == 66
        assert result.startswith('02')

    def test_encode_pubkey_bin_electrum(self):
        pub = (123, 456)
        result = encode_pubkey(pub, 'bin_electrum')
        assert isinstance(result, bytes)
        assert len(result) == 64

    def test_encode_pubkey_hex_electrum(self):
        pub = (123, 456)
        result = encode_pubkey(pub, 'hex_electrum')
        assert isinstance(result, str)
        assert len(result) == 128

    def test_encode_pubkey_invalid_format(self):
        pub = (123, 456)
        with pytest.raises(Exception):
            encode_pubkey(pub, 'invalid')

    def test_encode_pubkey_from_non_tuple(self):
        # Test with hex input that needs decoding first
        pub_hex = '04' + '00' * 64
        result = encode_pubkey(pub_hex, 'decimal')
        assert isinstance(result, tuple)


class TestDecodePubkey(object):
    """Tests for decode_pubkey function"""

    def test_decode_pubkey_decimal(self):
        pub = (123, 456)
        result = decode_pubkey(pub, 'decimal')
        assert result == (123, 456)

    def test_decode_pubkey_bin(self):
        # Create a valid bin pubkey
        from helpers.jacobianhelpers import G, fast_multiply
        point = fast_multiply(G, 12345)
        pub_bin = encode_pubkey(point, 'bin')
        result = decode_pubkey(pub_bin, 'bin')
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_decode_pubkey_hex(self):
        from helpers.jacobianhelpers import G, fast_multiply
        point = fast_multiply(G, 12345)
        pub_hex = encode_pubkey(point, 'hex')
        result = decode_pubkey(pub_hex, 'hex')
        assert isinstance(result, tuple)
        assert result == point

    def test_decode_pubkey_bin_compressed(self):
        from helpers.jacobianhelpers import G, fast_multiply
        point = fast_multiply(G, 12345)
        pub_bin_c = encode_pubkey(point, 'bin_compressed')
        result = decode_pubkey(pub_bin_c, 'bin_compressed')
        assert isinstance(result, tuple)
        # x coordinate should match
        assert result[0] == point[0]

    def test_decode_pubkey_hex_compressed(self):
        from helpers.jacobianhelpers import G, fast_multiply
        point = fast_multiply(G, 12345)
        pub_hex_c = encode_pubkey(point, 'hex_compressed')
        result = decode_pubkey(pub_hex_c, 'hex_compressed')
        assert isinstance(result, tuple)
        assert result[0] == point[0]

    def test_decode_pubkey_bin_electrum(self):
        from helpers.jacobianhelpers import G, fast_multiply
        point = fast_multiply(G, 12345)
        pub_electrum = encode_pubkey(point, 'bin_electrum')
        result = decode_pubkey(pub_electrum, 'bin_electrum')
        assert result == point

    def test_decode_pubkey_hex_electrum(self):
        from helpers.jacobianhelpers import G, fast_multiply
        point = fast_multiply(G, 12345)
        pub_electrum = encode_pubkey(point, 'hex_electrum')
        result = decode_pubkey(pub_electrum, 'hex_electrum')
        assert result == point

    def test_decode_pubkey_invalid_format(self):
        with pytest.raises(Exception):
            decode_pubkey('test', 'invalid')

    def test_decode_pubkey_auto_detect(self):
        from helpers.jacobianhelpers import G, fast_multiply
        point = fast_multiply(G, 12345)
        pub_hex = encode_pubkey(point, 'hex')
        result = decode_pubkey(pub_hex)  # No format specified
        assert result == point


class TestAddPubkeys(object):
    """Tests for add_pubkeys function"""

    def test_add_pubkeys(self):
        from helpers.jacobianhelpers import G, fast_multiply, fast_add
        p1 = fast_multiply(G, 12345)
        p2 = fast_multiply(G, 67890)
        
        p1_hex = encode_pubkey(p1, 'hex')
        p2_hex = encode_pubkey(p2, 'hex')
        
        result = add_pubkeys(p1_hex, p2_hex)
        expected = fast_add(p1, p2)
        
        assert decode_pubkey(result) == expected


class TestCompress(object):
    """Tests for compress function"""

    def test_compress_already_compressed(self):
        pub = '02' + '00' * 32
        result = compress(pub)
        assert result == pub

    def test_compress_bin(self):
        from helpers.jacobianhelpers import G, fast_multiply
        point = fast_multiply(G, 12345)
        pub_bin = encode_pubkey(point, 'bin')
        result = compress(pub_bin)
        assert isinstance(result, bytes)
        assert len(result) == 33

    def test_compress_hex(self):
        from helpers.jacobianhelpers import G, fast_multiply
        point = fast_multiply(G, 12345)
        pub_hex = encode_pubkey(point, 'hex')
        result = compress(pub_hex)
        assert isinstance(result, str)
        assert len(result) == 66

    def test_compress_decimal(self):
        from helpers.jacobianhelpers import G, fast_multiply
        point = fast_multiply(G, 12345)
        result = compress(point)
        assert isinstance(result, str)
        assert len(result) == 66


class TestPubkeyToAddress(object):
    """Tests for pubkey_to_address function"""

    def test_pubkey_to_address_tuple(self):
        from helpers.jacobianhelpers import G, fast_multiply
        point = fast_multiply(G, 12345)
        result = pubkey_to_address(point)
        assert isinstance(result, str)
        assert result.startswith('1')

    def test_pubkey_to_address_hex(self):
        from helpers.jacobianhelpers import G, fast_multiply
        point = fast_multiply(G, 12345)
        pub_hex = encode_pubkey(point, 'hex')
        result = pubkey_to_address(pub_hex)
        assert isinstance(result, str)
        assert result.startswith('1')

    def test_pubkey_to_address_hex_compressed(self):
        from helpers.jacobianhelpers import G, fast_multiply
        point = fast_multiply(G, 12345)
        pub_hex_c = encode_pubkey(point, 'hex_compressed')
        result = pubkey_to_address(pub_hex_c)
        assert isinstance(result, str)
        assert result.startswith('1')

    def test_pubkey_to_address_bin(self):
        from helpers.jacobianhelpers import G, fast_multiply
        point = fast_multiply(G, 12345)
        pub_bin = encode_pubkey(point, 'bin')
        result = pubkey_to_address(pub_bin)
        assert isinstance(result, str)
        assert result.startswith('1')

    def test_pubkey_to_address_testnet(self):
        from helpers.jacobianhelpers import G, fast_multiply
        point = fast_multiply(G, 12345)
        result = pubkey_to_address(point, magicbyte=111)
        assert isinstance(result, str)
        # Testnet addresses start with 'm' or 'n'
        assert result[0] in ['m', 'n']


class TestBinHash160(object):
    """Tests for bin_hash160 function"""

    def test_bin_hash160(self):
        result = bin_hash160(b'hello')
        assert isinstance(result, bytes)
        assert len(result) == 20

    def test_bin_hash160_different_inputs(self):
        result1 = bin_hash160(b'hello')
        result2 = bin_hash160(b'world')
        assert result1 != result2
