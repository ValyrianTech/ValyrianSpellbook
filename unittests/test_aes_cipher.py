#!/usr/bin/env python
"""Tests for AESCipher.py — authenticated AES-GCM encryption for the hot wallet."""

import base64
import hashlib

import pytest

from Crypto.Cipher import AES

from AESCipher import AESCipher

# Legacy v1 (CBC) format carries no version byte. Use a fixed IV whose first
# byte is not the v2 marker (0x02) so the new decrypt reliably detects legacy.
_LEGACY_IV = b'0123456789abcdef'
_LEGACY_BLOCK_SIZE = 32


def _legacy_encrypt(password, plaintext):
    """Produce a legacy (v1) CBC ciphertext using the original algorithm."""
    key = hashlib.sha256(password.encode()).digest()
    pad_len = _LEGACY_BLOCK_SIZE - (len(plaintext) % _LEGACY_BLOCK_SIZE)
    padded = plaintext + bytes([pad_len]) * pad_len
    cipher = AES.new(key, AES.MODE_CBC, _LEGACY_IV)
    return base64.b64encode(_LEGACY_IV + cipher.encrypt(padded))


class TestAESCipher:

    def test_init_sets_block_size(self):
        cipher = AESCipher(key='test_password')
        assert cipher.bs == 32

    def test_encrypt_decrypt_round_trip(self):
        cipher = AESCipher(key='test_password')
        encrypted = cipher.encrypt(b'secret data')
        assert isinstance(encrypted, bytes)
        assert cipher.decrypt(encrypted) == 'secret data'

    def test_encrypt_decrypt_empty_password_and_plaintext(self):
        cipher = AESCipher(key='')
        encrypted = cipher.encrypt(b'')
        assert cipher.decrypt(encrypted) == ''

    def test_decrypt_accepts_str_payload(self):
        cipher = AESCipher(key='test_password')
        encrypted = cipher.encrypt(b'secret data')
        assert cipher.decrypt(encrypted.decode('utf-8')) == 'secret data'

    def test_tampered_ciphertext_raises(self):
        cipher = AESCipher(key='test_password')
        encrypted = cipher.encrypt(b'secret data')
        data = bytearray(base64.b64decode(encrypted))
        data[-1] ^= 0x01
        with pytest.raises(ValueError):
            cipher.decrypt(base64.b64encode(bytes(data)))

    def test_wrong_password_raises(self):
        encrypted = AESCipher(key='correct').encrypt(b'secret data')
        with pytest.raises(ValueError):
            AESCipher(key='wrong').decrypt(encrypted)

    def test_legacy_cbc_decryption(self):
        legacy = _legacy_encrypt('old_password', b'legacy secret')
        cipher = AESCipher(key='old_password')
        assert cipher.decrypt(legacy) == 'legacy secret'

    def test_legacy_cbc_decryption_empty(self):
        legacy = _legacy_encrypt('old_password', b'')
        cipher = AESCipher(key='old_password')
        assert cipher.decrypt(legacy) == ''

    def test_encrypt_deterministic_with_injected_salt_and_nonce(self):
        salt = b's' * 16
        nonce = b'n' * 16
        first = AESCipher(key='pw', salt=salt, nonce=nonce).encrypt(b'data')
        second = AESCipher(key='pw', salt=salt, nonce=nonce).encrypt(b'data')
        assert first == second

    def test_encrypt_rejects_str_input(self):
        cipher = AESCipher(key='test_password')
        with pytest.raises(TypeError):
            cipher.encrypt('secret data')

    def test_pad_adds_pkcs7_padding(self):
        cipher = AESCipher(key='test_password')
        padded = cipher._pad(b'abc')
        assert len(padded) == 32
        assert padded == b'abc' + b'\x1d' * 29

    def test_pad_rejects_non_bytes(self):
        cipher = AESCipher(key='test_password')
        with pytest.raises(TypeError):
            cipher._pad('abc')

    def test_unpad_removes_pkcs7_padding(self):
        padded = b'abc' + b'\x1d' * 29
        assert AESCipher._unpad(padded) == b'abc'

    def test_unpad_rejects_non_bytes(self):
        with pytest.raises(TypeError):
            AESCipher._unpad('abc')

    def test_unpad_rejects_empty_data(self):
        with pytest.raises(ValueError):
            AESCipher._unpad(b'')

    def test_unpad_rejects_zero_padding(self):
        with pytest.raises(ValueError):
            AESCipher._unpad(b'abc\x00')

    def test_unpad_rejects_padding_longer_than_data(self):
        with pytest.raises(ValueError):
            AESCipher._unpad(b'abc\x05')

    def test_unpad_rejects_padding_longer_than_block(self):
        with pytest.raises(ValueError):
            AESCipher._unpad(b'a' * 32 + b'\x21')

    def test_unpad_rejects_inconsistent_padding(self):
        with pytest.raises(ValueError):
            AESCipher._unpad(b'hello\x03\x03\x02')
