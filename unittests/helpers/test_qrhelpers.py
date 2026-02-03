#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock

from helpers.qrhelpers import generate_qr


class TestQRHelpers(unittest.TestCase):
    """Test cases for helpers/qrhelpers.py"""

    def test_generate_qr_basic(self):
        """Test basic QR code generation"""
        result = generate_qr("test message")
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)

    def test_generate_qr_with_border(self):
        """Test QR code generation with custom border"""
        result = generate_qr("test message", border=2)
        self.assertIsInstance(result, bytes)

    def test_generate_qr_with_box_size(self):
        """Test QR code generation with custom box size"""
        result = generate_qr("test message", box_size=32)
        self.assertIsInstance(result, bytes)

    def test_generate_qr_error_correction_l(self):
        """Test QR code generation with error correction L"""
        result = generate_qr("test message", error='L')
        self.assertIsInstance(result, bytes)

    def test_generate_qr_error_correction_m(self):
        """Test QR code generation with error correction M"""
        result = generate_qr("test message", error='M')
        self.assertIsInstance(result, bytes)

    def test_generate_qr_error_correction_q(self):
        """Test QR code generation with error correction Q"""
        result = generate_qr("test message", error='Q')
        self.assertIsInstance(result, bytes)

    def test_generate_qr_error_correction_h(self):
        """Test QR code generation with error correction H"""
        result = generate_qr("test message", error='H')
        self.assertIsInstance(result, bytes)

    def test_generate_qr_invalid_error_correction(self):
        """Test QR code generation with invalid error correction raises ValueError"""
        # The code has a bug where it sets error_correction to string 'M' instead of constant
        with self.assertRaises(ValueError):
            generate_qr("test message", error='X')

    def test_generate_qr_with_version(self):
        """Test QR code generation with specific version"""
        result = generate_qr("test message", version=5)
        self.assertIsInstance(result, bytes)

    def test_generate_qr_long_message(self):
        """Test QR code generation with longer message"""
        long_message = "bitcoin:1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa?amount=0.001"
        result = generate_qr(long_message)
        self.assertIsInstance(result, bytes)


if __name__ == '__main__':
    unittest.main()
