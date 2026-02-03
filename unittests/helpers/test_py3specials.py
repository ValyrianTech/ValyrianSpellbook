#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from helpers.py3specials import (
    bin_dbl_sha256, lpad, get_code_string, changebase,
    bin_to_b58check, bytes_to_hex_string, safe_from_hex,
    from_int_representation_to_bytes, from_int_to_byte,
    from_byte_to_int, from_string_to_bytes, safe_hexlify,
    encode, decode, random_string, print_to_stderr,
    string_types, string_or_bytes_types, int_types,
    code_strings, two, three, four
)


class TestConstants(object):
    """Tests for module constants"""

    def test_string_types(self):
        assert string_types == str

    def test_string_or_bytes_types(self):
        assert string_or_bytes_types == (str, bytes)

    def test_int_types(self):
        assert int_types == (int, float)

    def test_numeric_constants(self):
        assert two == 2
        assert three == 3
        assert four == 4

    def test_code_strings(self):
        assert 2 in code_strings
        assert 10 in code_strings
        assert 16 in code_strings
        assert 32 in code_strings
        assert 58 in code_strings
        assert 256 in code_strings


class TestBinDblSha256(object):
    """Tests for bin_dbl_sha256 function"""

    def test_bin_dbl_sha256_bytes(self):
        result = bin_dbl_sha256(b'hello')
        assert isinstance(result, bytes)
        assert len(result) == 32

    def test_bin_dbl_sha256_string(self):
        result = bin_dbl_sha256('hello')
        assert isinstance(result, bytes)
        assert len(result) == 32


class TestLpad(object):
    """Tests for lpad function"""

    def test_lpad_shorter(self):
        result = lpad('abc', '0', 5)
        assert result == '00abc'
        assert len(result) == 5

    def test_lpad_equal(self):
        result = lpad('abcde', '0', 5)
        assert result == 'abcde'

    def test_lpad_longer(self):
        result = lpad('abcdefg', '0', 5)
        assert result == 'abcdefg'


class TestGetCodeString(object):
    """Tests for get_code_string function"""

    def test_get_code_string_binary(self):
        result = get_code_string(2)
        assert result == '01'

    def test_get_code_string_decimal(self):
        result = get_code_string(10)
        assert result == '0123456789'

    def test_get_code_string_hex(self):
        result = get_code_string(16)
        assert result == '0123456789abcdef'

    def test_get_code_string_base58(self):
        result = get_code_string(58)
        assert '0' not in result  # Base58 excludes 0, O, I, l
        assert 'O' not in result
        assert 'I' not in result
        assert 'l' not in result

    def test_get_code_string_invalid(self):
        with pytest.raises(ValueError):
            get_code_string(7)


class TestChangebase(object):
    """Tests for changebase function"""

    def test_changebase_same_base(self):
        result = changebase('abc', 16, 16)
        assert result == 'abc'

    def test_changebase_same_base_with_padding(self):
        result = changebase('abc', 16, 16, minlen=5)
        assert result == '00abc'

    def test_changebase_hex_to_decimal(self):
        result = changebase('ff', 16, 10)
        assert result == '255'

    def test_changebase_decimal_to_hex(self):
        result = changebase('255', 10, 16)
        assert result == 'ff'


class TestBinToB58check(object):
    """Tests for bin_to_b58check function"""

    def test_bin_to_b58check_zero_magicbyte(self):
        inp = bytes([0] * 20)
        result = bin_to_b58check(inp, magicbyte=0)
        assert isinstance(result, str)
        assert result.startswith('1')

    def test_bin_to_b58check_nonzero_magicbyte(self):
        inp = bytes([0] * 20)
        result = bin_to_b58check(inp, magicbyte=5)
        assert isinstance(result, str)

    def test_bin_to_b58check_large_magicbyte(self):
        inp = bytes([0] * 20)
        result = bin_to_b58check(inp, magicbyte=256)
        assert isinstance(result, str)

    def test_bin_to_b58check_leading_zeros(self):
        inp = bytes([0, 0, 0, 1, 2, 3])
        result = bin_to_b58check(inp, magicbyte=0)
        # Should have leading 1s for leading zero bytes
        assert result.startswith('1')


class TestBytesToHexString(object):
    """Tests for bytes_to_hex_string function"""

    def test_bytes_to_hex_string_bytes(self):
        result = bytes_to_hex_string(b'\x00\x01\x02\xff')
        assert result == '000102ff'

    def test_bytes_to_hex_string_string(self):
        result = bytes_to_hex_string('already_string')
        assert result == 'already_string'


class TestSafeFromHex(object):
    """Tests for safe_from_hex function"""

    def test_safe_from_hex(self):
        result = safe_from_hex('000102ff')
        assert result == b'\x00\x01\x02\xff'

    def test_safe_from_hex_uppercase(self):
        result = safe_from_hex('AABBCC')
        assert result == b'\xaa\xbb\xcc'


class TestFromIntRepresentationToBytes(object):
    """Tests for from_int_representation_to_bytes function"""

    def test_from_int_representation_to_bytes(self):
        result = from_int_representation_to_bytes(123)
        assert result == b'123'

    def test_from_int_representation_to_bytes_zero(self):
        result = from_int_representation_to_bytes(0)
        assert result == b'0'


class TestFromIntToByte(object):
    """Tests for from_int_to_byte function"""

    def test_from_int_to_byte(self):
        result = from_int_to_byte(65)
        assert result == b'A'

    def test_from_int_to_byte_zero(self):
        result = from_int_to_byte(0)
        assert result == b'\x00'

    def test_from_int_to_byte_max(self):
        result = from_int_to_byte(255)
        assert result == b'\xff'


class TestFromByteToInt(object):
    """Tests for from_byte_to_int function"""

    def test_from_byte_to_int(self):
        result = from_byte_to_int(65)
        assert result == 65


class TestFromStringToBytes(object):
    """Tests for from_string_to_bytes function"""

    def test_from_string_to_bytes_string(self):
        result = from_string_to_bytes('hello')
        assert result == b'hello'

    def test_from_string_to_bytes_bytes(self):
        result = from_string_to_bytes(b'hello')
        assert result == b'hello'


class TestSafeHexlify(object):
    """Tests for safe_hexlify function"""

    def test_safe_hexlify(self):
        result = safe_hexlify(b'\x00\x01\x02\xff')
        assert result == '000102ff'
        assert isinstance(result, str)


class TestEncode(object):
    """Tests for encode function"""

    def test_encode_base10(self):
        result = encode(255, 10)
        assert result == '255'

    def test_encode_base16(self):
        result = encode(255, 16)
        assert result == 'ff'

    def test_encode_base58(self):
        result = encode(255, 58)
        assert isinstance(result, str)

    def test_encode_base256(self):
        result = encode(255, 256)
        assert isinstance(result, bytes)
        assert result == b'\xff'

    def test_encode_with_minlen(self):
        result = encode(1, 16, minlen=4)
        assert result == '0001'

    def test_encode_zero(self):
        result = encode(0, 16, minlen=2)
        assert result == '00'

    def test_encode_base256_with_padding(self):
        result = encode(1, 256, minlen=4)
        assert len(result) == 4
        assert result == b'\x00\x00\x00\x01'


class TestDecode(object):
    """Tests for decode function"""

    def test_decode_base10(self):
        result = decode('255', 10)
        assert result == 255

    def test_decode_base16(self):
        result = decode('ff', 16)
        assert result == 255

    def test_decode_base16_uppercase(self):
        result = decode('FF', 16)
        assert result == 255

    def test_decode_base58(self):
        result = decode('5Q', 58)
        assert isinstance(result, int)

    def test_decode_base256_bytes(self):
        result = decode(b'\xff', 256)
        assert result == 255

    def test_decode_base256_string(self):
        result = decode('ff', 256)
        assert result == 255


class TestRandomString(object):
    """Tests for random_string function"""

    def test_random_string(self):
        result = random_string(16)
        assert isinstance(result, str)

    def test_random_string_different_each_time(self):
        result1 = random_string(16)
        result2 = random_string(16)
        assert result1 != result2


class TestPrintToStderr(object):
    """Tests for print_to_stderr function"""

    def test_print_to_stderr(self, capsys):
        print_to_stderr('test message')
        captured = capsys.readouterr()
        assert 'test message' in captured.err
