#!/usr/bin/env python
"""Tests for AESCipher.py — AES encryption/decryption used by the hot wallet."""
from AESCipher import AESCipher


class TestAESCipher:

    def test_init_derives_32_byte_key(self):
        cipher = AESCipher(key='test_password')
        assert cipher.bs == 32
        assert len(cipher.key) == 32

    def test_encrypt_decrypt_round_trip(self):
        cipher = AESCipher(key='test_password')
        encrypted = cipher.encrypt(b'secret data')
        assert isinstance(encrypted, bytes)
        assert cipher.decrypt(encrypted) == 'secret data'

    def test_encrypt_decrypt_empty_password(self):
        cipher = AESCipher(key='')
        encrypted = cipher.encrypt(b'')
        assert cipher.decrypt(encrypted) == ''

    def test_pad_adds_pkcs7_padding(self):
        cipher = AESCipher(key='test_password')
        padded = cipher._pad(b'abc')
        assert len(padded) == 32
        assert padded == b'abc' + b'\x1d' * 29

    def test_unpad_removes_pkcs7_padding(self):
        padded = b'abc' + b'\x1d' * 29
        assert AESCipher._unpad(padded) == b'abc'
