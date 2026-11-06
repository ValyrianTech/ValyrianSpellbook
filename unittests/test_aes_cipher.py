#!/usr/bin/env python
"""Tests for AESCipher.py — authenticated AES-GCM encryption for the hot wallet."""

import base64
import binascii
import hashlib
from unittest import mock

import pytest
from Crypto.Cipher import AES  # nosec B413 # pycryptodome, not the deprecated pyCrypto
from Crypto.Protocol.KDF import scrypt  # nosec B413 # pycryptodome, not the deprecated pyCrypto
from Crypto.Random import get_random_bytes  # nosec B413 # pycryptodome, not the deprecated pyCrypto

from AESCipher import (
    KEY_SIZE,
    NONCE_SIZE,
    SALT_SIZE,
    SCRYPT_N,
    SCRYPT_P,
    SCRYPT_R,
    VERSION,
    AESCipher,
)

# Legacy v1 (CBC) format carries no version byte. Use a fixed IV whose first
# byte is not the v2 marker (0x02) so the new decrypt reliably detects legacy.
_LEGACY_IV = b'0123456789abcdef'
_LEGACY_BLOCK_SIZE = 32


def _legacy_encrypt(password, plaintext, iv=_LEGACY_IV):
    """Produce a legacy (v1) CBC ciphertext using the original algorithm."""
    key = hashlib.sha256(password.encode()).digest()
    pad_len = _LEGACY_BLOCK_SIZE - (len(plaintext) % _LEGACY_BLOCK_SIZE)
    padded = plaintext + bytes([pad_len]) * pad_len
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(padded))


def _old_v2_encrypt(password, plaintext, salt=None, nonce=None):
    """Produce an old-v2 (no magic) GCM ciphertext using the original AAD."""
    salt = salt if salt is not None else get_random_bytes(SALT_SIZE)
    nonce = nonce if nonce is not None else get_random_bytes(NONCE_SIZE)
    key = scrypt(password.encode('utf-8'), salt, KEY_SIZE,
                 N=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    cipher.update(VERSION)
    cipher.update(salt)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return base64.b64encode(VERSION + salt + nonce + tag + ciphertext)


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

    def test_decrypt_tolerates_trailing_newline_bytes(self):
        cipher = AESCipher(key='test_password')
        encrypted = cipher.encrypt(b'secret data')
        assert cipher.decrypt(encrypted + b'\n') == 'secret data'

    def test_decrypt_tolerates_trailing_newline_str(self):
        cipher = AESCipher(key='test_password')
        encrypted = cipher.encrypt(b'secret data')
        assert cipher.decrypt(encrypted.decode('utf-8') + '\n') == 'secret data'

    def test_decrypt_tolerates_leading_and_trailing_whitespace(self):
        cipher = AESCipher(key='test_password')
        encrypted = cipher.encrypt(b'secret data')
        assert cipher.decrypt(b'  \n' + encrypted + b'\n\t ') == 'secret data'

    def test_decrypt_accepts_whitespace_padded_payload(self):
        cipher = AESCipher(key='test_password')
        encrypted = cipher.encrypt(b'secret data')
        padded = '  \n' + encrypted.decode('utf-8') + '\n\t '
        assert cipher.decrypt(padded) == 'secret data'

    def test_decrypt_rejects_malformed_base64(self):
        cipher = AESCipher(key='pw')
        with pytest.raises(ValueError) as exc_info:
            cipher.decrypt(b'not valid base64!!!')
        assert 'malformed base64 payload' in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, binascii.Error)

    def test_decrypt_rejects_malformed_base64_str_payload(self):
        cipher = AESCipher(key='pw')
        with pytest.raises(ValueError) as exc_info:
            cipher.decrypt('not valid base64!!!')
        assert 'malformed base64 payload' in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, binascii.Error)

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
        cipher = AESCipher(key='old_password', allow_legacy=True)
        assert cipher.decrypt(legacy) == 'legacy secret'

    def test_legacy_cbc_decryption_empty(self):
        legacy = _legacy_encrypt('old_password', b'')
        cipher = AESCipher(key='old_password', allow_legacy=True)
        assert cipher.decrypt(legacy) == ''

    def test_legacy_cbc_decryption_with_v2_marker_iv(self):
        iv = b'\x02' + b'\x00' * 15
        legacy = _legacy_encrypt('old_password', b'legacy secret', iv=iv)
        cipher = AESCipher(key='old_password')
        assert cipher.decrypt_legacy(legacy) == 'legacy secret'

    def test_decrypt_legacy_explicit(self):
        legacy = _legacy_encrypt('old_password', b'legacy secret')
        assert AESCipher(key='old_password').decrypt_legacy(legacy) == 'legacy secret'

    def test_decrypt_legacy_refuses_by_default(self):
        legacy = _legacy_encrypt('old_password', b'legacy secret')
        with pytest.raises(ValueError) as exc_info:
            AESCipher(key='old_password').decrypt(legacy)
        assert 'migrat' in str(exc_info.value)
        assert 'allow_legacy' in str(exc_info.value)
        assert 'decrypt_legacy' in str(exc_info.value)

    def test_decrypt_legacy_refuses_by_default_v2_marker_iv(self):
        iv = b'\x02' + b'\x00' * 15
        legacy = _legacy_encrypt('old_password', b'legacy secret', iv=iv)
        with pytest.raises(ValueError):
            AESCipher(key='old_password').decrypt(legacy)

    def test_decrypt_legacy_path_logs_warning(self):
        legacy = _legacy_encrypt('old_password', b'legacy secret')
        with mock.patch.object(AESCipher, 'LOG') as mock_log:
            AESCipher(key='old_password', allow_legacy=True).decrypt(legacy)
        mock_log.warning.assert_called_once()

    def test_decrypt_legacy_method_logs_warning(self):
        legacy = _legacy_encrypt('old_password', b'legacy secret')
        with mock.patch.object(AESCipher, 'LOG') as mock_log:
            AESCipher(key='old_password').decrypt_legacy(legacy)
        mock_log.warning.assert_called_once()

    def test_old_v2_layout_decrypts(self):
        payload = _old_v2_encrypt('old_password', b'old v2 secret')
        assert AESCipher(key='old_password').decrypt(payload) == 'old v2 secret'

    def test_old_v2_layout_wrong_password_raises(self):
        payload = _old_v2_encrypt('correct', b'old v2 secret')
        with pytest.raises(ValueError):
            AESCipher(key='wrong').decrypt(payload)

    def test_tampered_magic_rejected(self):
        cipher = AESCipher(key='test_password')
        encrypted = cipher.encrypt(b'secret data')
        data = bytearray(base64.b64decode(encrypted))
        data[0] ^= 0x01
        with pytest.raises(ValueError):
            cipher.decrypt(base64.b64encode(bytes(data)))

    def test_tampered_version_rejected(self):
        cipher = AESCipher(key='test_password')
        encrypted = cipher.encrypt(b'secret data')
        data = bytearray(base64.b64decode(encrypted))
        data[2] ^= 0x01
        with pytest.raises(ValueError):
            cipher.decrypt(base64.b64encode(bytes(data)))

    def test_tampered_salt_rejected(self):
        cipher = AESCipher(key='test_password')
        encrypted = cipher.encrypt(b'secret data')
        data = bytearray(base64.b64decode(encrypted))
        data[3] ^= 0x01
        with pytest.raises(ValueError):
            cipher.decrypt(base64.b64encode(bytes(data)))

    def test_non_utf8_plaintext_raises(self):
        cipher = AESCipher(key='test_password')
        encrypted = cipher.encrypt(b'\xff\xfe')
        with pytest.raises(ValueError):
            cipher.decrypt(encrypted)

    def test_v2_marker_legacy_shaped_but_legacy_fails_raises(self):
        payload = b'\x02' + b'\x00' * 47
        b64 = base64.b64encode(payload)
        with pytest.raises(ValueError):
            AESCipher(key='pw').decrypt(b64)

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
