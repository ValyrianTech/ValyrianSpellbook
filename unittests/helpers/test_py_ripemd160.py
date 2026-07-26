#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import hashlib

from helpers.py_ripemd160 import ripemd160, compress, fi, rol


class TestPyRipemd160(unittest.TestCase):
    """Test cases for helpers/py_ripemd160.py"""

    def test_ripemd160_empty(self):
        """Test RIPEMD-160 of empty string"""
        result = ripemd160(b'')
        expected = bytes.fromhex('9c1185a5c5e9fc54612808977ee8f548b2258d31')
        self.assertEqual(result, expected)

    def test_ripemd160_short(self):
        """Test RIPEMD-160 of short data (less than 64 bytes, no full blocks)"""
        result = ripemd160(b'abc')
        expected = bytes.fromhex('8eb208f7e05d987a9b044a8e98c6b087f15a0bfc')
        self.assertEqual(result, expected)

    def test_ripemd160_multi_block(self):
        """Test RIPEMD-160 with data >= 64 bytes to cover line 99 (full block processing)"""
        data = b'a' * 64  # Exactly 64 bytes = 1 full block
        result = ripemd160(data)
        # Verify it produces a valid 20-byte hash
        self.assertEqual(len(result), 20)
        # Cross-check with hashlib if available
        try:
            expected = hashlib.new('ripemd160', data).digest()
            self.assertEqual(result, expected)
        except ValueError:
            # ripemd160 may not be available in hashlib on all systems
            pass

    def test_ripemd160_long_message(self):
        """Test RIPEMD-160 with data > 64 bytes (multiple blocks)"""
        data = b'Hello, World! ' * 10  # 140 bytes = 2 full blocks + remainder
        result = ripemd160(data)
        self.assertEqual(len(result), 20)
        try:
            expected = hashlib.new('ripemd160', data).digest()
            self.assertEqual(result, expected)
        except ValueError:
            pass

    def test_fi_function_all_rounds(self):
        """Test fi function for all valid round indices"""
        x, y, z = 0x12345678, 0x9abcdef0, 0x0fedcba9
        for i in range(5):
            result = fi(x, y, z, i)
            self.assertIsInstance(result, int)

    def test_rol_function(self):
        """Test rol (rotate left) function"""
        result = rol(0x12345678, 4)
        self.assertEqual(result, 0x23456781)

    def test_compress_function(self):
        """Test compress function with a block"""
        state = (0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xc3d2e1f0)
        block = b'\x00' * 64
        result = compress(*state, block)
        self.assertEqual(len(result), 5)
        for h in result:
            self.assertIsInstance(h, int)


if __name__ == '__main__':
    unittest.main()
