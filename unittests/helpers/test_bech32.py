#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from helpers.bech32 import (
    bech32_polymod, bech32_hrp_expand, bech32_verify_checksum,
    bech32_create_checksum, bech32_encode, bech32_decode,
    convertbits, decode, encode, CHARSET
)


class TestBech32Polymod(object):
    """Tests for bech32_polymod function"""

    def test_bech32_polymod_empty(self):
        result = bech32_polymod([])
        assert result == 1

    def test_bech32_polymod_single_value(self):
        result = bech32_polymod([0])
        assert isinstance(result, int)

    def test_bech32_polymod_multiple_values(self):
        result = bech32_polymod([1, 2, 3, 4, 5])
        assert isinstance(result, int)


class TestBech32HrpExpand(object):
    """Tests for bech32_hrp_expand function"""

    def test_bech32_hrp_expand_bc(self):
        result = bech32_hrp_expand('bc')
        assert isinstance(result, list)
        assert len(result) == 5  # 2 high bits + separator + 2 low bits

    def test_bech32_hrp_expand_tb(self):
        result = bech32_hrp_expand('tb')
        assert isinstance(result, list)


class TestBech32VerifyChecksum(object):
    """Tests for bech32_verify_checksum function"""

    def test_bech32_verify_checksum_valid(self):
        # Create a valid checksum and verify it
        hrp = 'bc'
        data = [0, 14, 20, 15, 7, 13, 26, 0, 25, 18, 6, 11, 13, 8, 21, 4, 20, 3, 17, 2, 29, 3, 12, 29, 3, 4, 15, 24, 20, 6, 14, 30, 22]
        # This should be a valid bech32 string data
        result = bech32_verify_checksum(hrp, data)
        assert isinstance(result, bool)


class TestBech32CreateChecksum(object):
    """Tests for bech32_create_checksum function"""

    def test_bech32_create_checksum(self):
        hrp = 'bc'
        data = [0, 14, 20, 15, 7, 13, 26, 0]
        result = bech32_create_checksum(hrp, data)
        assert isinstance(result, list)
        assert len(result) == 6


class TestBech32Encode(object):
    """Tests for bech32_encode function"""

    def test_bech32_encode(self):
        hrp = 'bc'
        data = [0, 14, 20, 15, 7, 13, 26, 0]
        result = bech32_encode(hrp, data)
        assert result.startswith('bc1')
        assert '1' in result


class TestBech32Decode(object):
    """Tests for bech32_decode function"""

    def test_bech32_decode_valid(self):
        # Valid bech32 string
        bech = 'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4'
        hrp, data = bech32_decode(bech)
        assert hrp == 'bc'
        assert data is not None

    def test_bech32_decode_invalid_char(self):
        # Contains invalid character (char < 33 or > 126)
        bech = 'bc1' + chr(32) + 'test'
        hrp, data = bech32_decode(bech)
        assert hrp is None
        assert data is None

    def test_bech32_decode_mixed_case(self):
        # Mixed case is invalid
        bech = 'BC1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4'
        hrp, data = bech32_decode(bech)
        assert hrp is None
        assert data is None

    def test_bech32_decode_no_separator(self):
        # No '1' separator
        bech = 'bcqw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4'
        hrp, data = bech32_decode(bech)
        assert hrp is None
        assert data is None

    def test_bech32_decode_separator_at_start(self):
        # '1' at position 0
        bech = '1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4'
        hrp, data = bech32_decode(bech)
        assert hrp is None
        assert data is None

    def test_bech32_decode_too_long(self):
        # String longer than 90 characters
        bech = 'bc1' + 'q' * 100
        hrp, data = bech32_decode(bech)
        assert hrp is None
        assert data is None

    def test_bech32_decode_invalid_data_char(self):
        # Contains character not in CHARSET after separator
        bech = 'bc1bw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4'  # 'b' is not in charset
        hrp, data = bech32_decode(bech)
        assert hrp is None
        assert data is None

    def test_bech32_decode_invalid_checksum(self):
        # Valid format but wrong checksum
        bech = 'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t5'  # Changed last char
        hrp, data = bech32_decode(bech)
        assert hrp is None
        assert data is None

    def test_bech32_decode_short_after_separator(self):
        # Less than 6 chars after separator
        bech = 'bc1qw508'
        hrp, data = bech32_decode(bech)
        assert hrp is None
        assert data is None


class TestConvertbits(object):
    """Tests for convertbits function"""

    def test_convertbits_8_to_5(self):
        data = [0, 1, 2, 3]
        result = convertbits(data, 8, 5)
        assert result is not None
        assert isinstance(result, list)

    def test_convertbits_5_to_8(self):
        data = [0, 0, 0, 0, 0, 0, 1, 0]
        result = convertbits(data, 5, 8, pad=False)
        assert result is not None

    def test_convertbits_negative_value(self):
        data = [-1, 0, 1]
        result = convertbits(data, 8, 5)
        assert result is None

    def test_convertbits_value_too_large(self):
        data = [256, 0, 1]  # 256 is too large for 8 bits
        result = convertbits(data, 8, 5)
        assert result is None

    def test_convertbits_no_pad(self):
        data = [0, 1]
        result = convertbits(data, 8, 5, pad=False)
        # May return None if bits don't align properly
        assert result is None or isinstance(result, list)

    def test_convertbits_with_padding(self):
        data = [0, 1]
        result = convertbits(data, 8, 5, pad=True)
        assert result is not None


class TestDecode(object):
    """Tests for decode function (segwit address decoding)"""

    def test_decode_valid_p2wpkh(self):
        # Valid P2WPKH address
        addr = 'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4'
        witver, witprog = decode('bc', addr)
        assert witver == 0
        assert witprog is not None
        assert len(witprog) == 20

    def test_decode_valid_p2wsh(self):
        # Valid P2WSH address (32 bytes)
        addr = 'bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3'
        witver, witprog = decode('bc', addr)
        assert witver == 0
        assert witprog is not None
        assert len(witprog) == 32

    def test_decode_wrong_hrp(self):
        addr = 'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4'
        witver, witprog = decode('tb', addr)  # Wrong HRP
        assert witver is None
        assert witprog is None

    def test_decode_invalid_witness_version(self):
        # Witness version > 16 is invalid - create address with version 17
        # We need to craft a bech32 string with witness version > 16
        # Version is first data byte, 17 = 'h' in charset
        hrp = 'bc'
        # Create data with version 17 (invalid) and some program
        data = [17] + [0] * 20
        bech = bech32_encode(hrp, data)
        witver, witprog = decode('bc', bech)
        assert witver is None
        assert witprog is None

    def test_decode_invalid_v0_length(self):
        # For v0, program must be 20 or 32 bytes
        # Create v0 address with 25 bytes (invalid for v0)
        hrp = 'bc'
        witprog = [0] * 25
        # Manually encode to bypass validation in encode()
        data = [0] + convertbits(witprog, 8, 5)
        bech = bech32_encode(hrp, data)
        witver, result = decode('bc', bech)
        assert witver is None
        assert result is None


class TestEncode(object):
    """Tests for encode function (segwit address encoding)"""

    def test_encode_p2wpkh(self):
        # 20-byte witness program (P2WPKH)
        witprog = [0] * 20
        result = encode('bc', 0, witprog)
        assert result is not None
        assert result.startswith('bc1q')

    def test_encode_invalid_returns_none(self):
        # Test that encode returns None for invalid data
        # Create a program that would fail decode validation
        # A 1-byte program is too short (< 2 bytes)
        witprog = [0]
        result = encode('bc', 0, witprog)
        assert result is None

    def test_encode_p2wsh(self):
        # 32-byte witness program (P2WSH)
        witprog = [0] * 32
        result = encode('bc', 0, witprog)
        assert result is not None
        assert result.startswith('bc1q')

    def test_encode_testnet(self):
        witprog = [0] * 20
        result = encode('tb', 0, witprog)
        assert result is not None
        assert result.startswith('tb1q')

    def test_encode_witness_v1(self):
        # Witness version 1 (taproot)
        witprog = [0] * 32
        result = encode('bc', 1, witprog)
        assert result is not None
        assert result.startswith('bc1p')


class TestCharset(object):
    """Tests for CHARSET constant"""

    def test_charset_length(self):
        assert len(CHARSET) == 32

    def test_charset_no_duplicates(self):
        assert len(set(CHARSET)) == 32
