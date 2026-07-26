#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from helpers.privatekeyhelpers import (
    PrivateKey, encode_privkey, decode_privkey, get_privkey_format,
    b58check_to_bin, privkey_to_pubkey, add_privkeys, privkey_to_address,
    wif_compressed_regex, wif_uncompressed_regex, hexadecimal_regex
)
from helpers.jacobianhelpers import N


class TestPrivateKeyClass(object):
    """Tests for PrivateKey class"""

    def test_privatekey_from_decimal(self):
        pk = PrivateKey(12345)
        assert pk.decimal == 12345
        assert pk.hex is not None
        assert pk.wif is not None
        assert pk.wifc is not None

    def test_privatekey_from_hex(self):
        hex_key = '0000000000000000000000000000000000000000000000000000000000003039'
        pk = PrivateKey(hex_key)
        assert pk.decimal == 12345
        assert pk.hex == hex_key.upper()

    def test_privatekey_from_wif(self):
        # Test creating from WIF format
        wif = encode_privkey(12345, 'wif')
        pk = PrivateKey(wif)
        assert pk.decimal == 12345


class TestGetPrivkeyFormat(object):
    """Tests for get_privkey_format function"""

    def test_get_privkey_format_decimal(self):
        result = get_privkey_format(12345)
        assert result == 'decimal'

    def test_get_privkey_format_decimal_float(self):
        result = get_privkey_format(12345.0)
        assert result == 'decimal'

    def test_get_privkey_format_bin(self):
        # 32 bytes
        key = b'\x00' * 32
        result = get_privkey_format(key)
        assert result == 'bin'

    def test_get_privkey_format_bin_compressed(self):
        # 33 bytes
        key = b'\x00' * 32 + b'\x01'
        result = get_privkey_format(key)
        assert result == 'bin_compressed'

    def test_get_privkey_format_hex(self):
        # 64 chars
        key = '00' * 32
        result = get_privkey_format(key)
        assert result == 'hex'

    def test_get_privkey_format_hex_compressed(self):
        # 66 chars
        key = '00' * 32 + '01'
        result = get_privkey_format(key)
        assert result == 'hex_compressed'

    def test_get_privkey_format_wif(self):
        # Generate a WIF key
        wif = encode_privkey(12345, 'wif')
        result = get_privkey_format(wif)
        assert result == 'wif'

    def test_get_privkey_format_wif_compressed(self):
        wifc = encode_privkey(12345, 'wif_compressed')
        result = get_privkey_format(wifc)
        assert result == 'wif_compressed'

    def test_get_privkey_format_invalid(self):
        with pytest.raises(Exception):
            get_privkey_format('invalid')


class TestEncodePrivkey(object):
    """Tests for encode_privkey function"""

    def test_encode_privkey_decimal(self):
        result = encode_privkey(12345, 'decimal')
        assert result == 12345

    def test_encode_privkey_bin(self):
        result = encode_privkey(12345, 'bin')
        assert isinstance(result, bytes)
        assert len(result) == 32

    def test_encode_privkey_bin_compressed(self):
        result = encode_privkey(12345, 'bin_compressed')
        assert isinstance(result, bytes)
        assert len(result) == 33
        assert result[-1] == 1

    def test_encode_privkey_hex(self):
        result = encode_privkey(12345, 'hex')
        assert isinstance(result, str)
        assert len(result) == 64

    def test_encode_privkey_hex_compressed(self):
        result = encode_privkey(12345, 'hex_compressed')
        assert isinstance(result, str)
        assert len(result) == 66
        assert result.endswith('01')

    def test_encode_privkey_wif(self):
        result = encode_privkey(12345, 'wif')
        assert isinstance(result, str)
        assert result.startswith('5')

    def test_encode_privkey_wif_compressed(self):
        result = encode_privkey(12345, 'wif_compressed')
        assert isinstance(result, str)
        assert result[0] in ['K', 'L']

    def test_encode_privkey_invalid_format(self):
        with pytest.raises(Exception):
            encode_privkey(12345, 'invalid')

    def test_encode_privkey_from_non_int(self):
        # Test with hex input
        hex_key = '00' * 32
        result = encode_privkey(hex_key, 'decimal')
        assert isinstance(result, int)

    def test_encode_privkey_with_vbyte(self):
        result = encode_privkey(12345, 'wif', vbyte=111)
        assert isinstance(result, str)


class TestDecodePrivkey(object):
    """Tests for decode_privkey function"""

    def test_decode_privkey_decimal(self):
        result = decode_privkey(12345, 'decimal')
        assert result == 12345

    def test_decode_privkey_bin(self):
        bin_key = encode_privkey(12345, 'bin')
        result = decode_privkey(bin_key, 'bin')
        assert result == 12345

    def test_decode_privkey_bin_compressed(self):
        bin_c = encode_privkey(12345, 'bin_compressed')
        result = decode_privkey(bin_c, 'bin_compressed')
        assert result == 12345

    def test_decode_privkey_hex(self):
        hex_key = encode_privkey(12345, 'hex')
        result = decode_privkey(hex_key, 'hex')
        assert result == 12345

    def test_decode_privkey_hex_compressed(self):
        hex_c = encode_privkey(12345, 'hex_compressed')
        result = decode_privkey(hex_c, 'hex_compressed')
        assert result == 12345

    def test_decode_privkey_wif(self):
        wif = encode_privkey(12345, 'wif')
        result = decode_privkey(wif, 'wif')
        assert result == 12345

    def test_decode_privkey_wif_compressed(self):
        wifc = encode_privkey(12345, 'wif_compressed')
        result = decode_privkey(wifc, 'wif_compressed')
        assert result == 12345

    def test_decode_privkey_auto_detect(self):
        wif = encode_privkey(12345, 'wif')
        result = decode_privkey(wif)  # No format specified
        assert result == 12345

    def test_decode_privkey_invalid_format(self):
        with pytest.raises(Exception):
            decode_privkey('test', 'invalid')


class TestB58checkToBin(object):
    """Tests for b58check_to_bin function"""

    def test_b58check_to_bin(self):
        wif = encode_privkey(12345, 'wif')
        result = b58check_to_bin(wif)
        assert isinstance(result, bytes)

    def test_b58check_to_bin_leading_ones(self):
        # WIF with leading zeros in the key
        wif = encode_privkey(1, 'wif')
        result = b58check_to_bin(wif)
        assert isinstance(result, bytes)


class TestPrivkeyToPubkey(object):
    """Tests for privkey_to_pubkey function"""

    def test_privkey_to_pubkey_decimal(self):
        result = privkey_to_pubkey(12345)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_privkey_to_pubkey_hex(self):
        hex_key = encode_privkey(12345, 'hex')
        result = privkey_to_pubkey(hex_key)
        assert isinstance(result, str)
        assert result.startswith('04')

    def test_privkey_to_pubkey_hex_compressed(self):
        hex_c = encode_privkey(12345, 'hex_compressed')
        result = privkey_to_pubkey(hex_c)
        assert isinstance(result, str)
        assert result[0:2] in ['02', '03']

    def test_privkey_to_pubkey_wif(self):
        wif = encode_privkey(12345, 'wif')
        result = privkey_to_pubkey(wif)
        assert isinstance(result, str)

    def test_privkey_to_pubkey_wif_compressed(self):
        wifc = encode_privkey(12345, 'wif_compressed')
        result = privkey_to_pubkey(wifc)
        assert isinstance(result, str)

    def test_privkey_to_pubkey_invalid(self):
        # Private key >= N is invalid
        with pytest.raises(Exception):
            privkey_to_pubkey(N)


class TestAddPrivkeys(object):
    """Tests for add_privkeys function"""

    def test_add_privkeys_decimal(self):
        result = add_privkeys(100, 200)
        assert result == 300

    def test_add_privkeys_hex(self):
        p1 = encode_privkey(100, 'hex')
        p2 = encode_privkey(200, 'hex')
        result = add_privkeys(p1, p2)
        # Result should be in same format as first key
        assert isinstance(result, str)
        assert len(result) == 64

    def test_add_privkeys_wrap_around(self):
        # Test modular arithmetic
        result = add_privkeys(N - 1, 2)
        assert result == 1


class TestPrivkeyToAddress(object):
    """Tests for privkey_to_address function"""

    def test_privkey_to_address(self):
        result = privkey_to_address(12345)
        assert isinstance(result, str)
        assert result.startswith('1')

    def test_privkey_to_address_testnet(self):
        result = privkey_to_address(12345, magicbyte=111)
        assert isinstance(result, str)
        assert result[0] in ['m', 'n']


class TestRegexPatterns(object):
    """Tests for regex patterns"""

    def test_wif_compressed_regex(self):
        import re
        wifc = encode_privkey(12345, 'wif_compressed')
        assert re.match(wif_compressed_regex, wifc) is not None

    def test_wif_uncompressed_regex(self):
        import re
        wif = encode_privkey(12345, 'wif')
        assert re.match(wif_uncompressed_regex, wif) is not None

    def test_hexadecimal_regex(self):
        import re
        hex_key = encode_privkey(12345, 'hex')
        assert re.match(hexadecimal_regex, hex_key) is not None


class TestPrivateKeyTestnet(object):
    """Tests for PrivateKey with testnet - covering additional paths"""

    def test_privatekey_mainnet(self):
        """Test PrivateKey creation with mainnet (default)"""
        pk = PrivateKey(12345, testnet=False)
        assert pk.decimal == 12345
        assert pk.wif is not None
        # Mainnet WIF starts with '5'
        assert pk.wif.startswith('5')


class TestDecodePrivkeyEdgeCases(object):
    """Tests for decode_privkey edge cases"""

    def test_decode_privkey_invalid_format_raises(self):
        """Test that invalid format raises exception"""
        with pytest.raises(Exception) as excinfo:
            decode_privkey('test', 'invalid_format')
        assert 'WIF does not represent privkey' in str(excinfo.value)


class TestPrivateKeyTestnetWIF(object):
    """Tests for PrivateKey with testnet WIF format"""

    def test_privatekey_testnet_raises_on_wifc_validation(self):
        """Test PrivateKey testnet raises exception because WIF compressed regex doesn't match testnet keys"""
        with pytest.raises(Exception) as excinfo:
            PrivateKey(12345, testnet=True)
        assert 'Invalid WIF compressed key' in str(excinfo.value)

    def test_privatekey_from_wif_compressed(self):
        """Test creating PrivateKey from WIF compressed format"""
        wifc = encode_privkey(12345, 'wif_compressed')
        pk = PrivateKey(wifc)
        assert pk.decimal == 12345

    def test_privatekey_from_hex_string(self):
        """Test creating PrivateKey from hex string"""
        hex_key = '0000000000000000000000000000000000000000000000000000000000003039'
        pk = PrivateKey(hex_key)
        assert pk.decimal == 12345
        assert pk.hex == hex_key.upper()


class TestGetPrivkeyFormatEdgeCases(object):
    """Tests for get_privkey_format edge cases"""

    def test_get_privkey_format_invalid_bin_length(self):
        """Test get_privkey_format with invalid binary length raises exception"""
        with pytest.raises(Exception):
            get_privkey_format(b'\x00' * 31)  # Not 32 or 33 bytes

    def test_get_privkey_format_empty_string(self):
        """Test get_privkey_format with empty string raises exception"""
        with pytest.raises(Exception):
            get_privkey_format('')

    def test_get_privkey_format_invalid_wif_length(self):
        """Test get_privkey_format with WIF that decodes to invalid length (line 103)"""
        from unittest.mock import patch
        # A string that doesn't match any length checks (not 58, 64, 66, etc.)
        # but will fall through to the b58check_to_bin path
        with patch('helpers.privatekeyhelpers.b58check_to_bin', return_value=b'\x00' * 20):
            with pytest.raises(Exception) as excinfo:
                get_privkey_format('LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL')
            assert 'WIF does not represent privkey' in str(excinfo.value)
