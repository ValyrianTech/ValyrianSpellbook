"""Authenticated AES encryption/decryption cipher for the Valyrian Spellbook.

This module provides the :class:`AESCipher` class used to protect the hot wallet
and other secrets at rest.

The current (v2) format uses AES-GCM for authenticated encryption and a slow,
salted ``scrypt`` key-derivation function, which together provide:

- **Confidentiality** — the plaintext cannot be read without the password.
- **Integrity/authenticity** — any tampering with the ciphertext, tag, salt or
  version byte causes decryption to fail with a :class:`ValueError`.
- **Brute-force resistance** — ``scrypt`` (rather than a single SHA-256 round)
  makes offline password guessing expensive.

Ciphertext layout (v2, after base64 decoding)::

    <version byte (1)> | <salt (16)> | <nonce (16)> | <tag (16)> | <ciphertext>

The version byte and salt are fed into the GCM authenticator so an attacker
cannot swap them without invalidating the tag.

For backward compatibility, the class can still *read* legacy (v1) ciphertexts
produced by the old implementation (AES-CBC with PKCS7 padding and a single
SHA-256 key round). The legacy format carries no version byte, so any payload
whose first byte is not the v2 marker is treated as legacy. Because a legacy
IV may randomly begin with the v2 marker, a payload that starts with the v2
marker is tried as v2 first and, if authentication fails, retried as legacy —
this keeps the ~1/256 of legacy wallets whose IV starts with 0x02 decryptable.
The legacy retry is only attempted when the payload is structurally legacy-shaped
(its length is ``16 + 16*k`` bytes, i.e. an IV plus a positive multiple of
``AES.block_size`` ciphertext).
"""

import base64
import hashlib

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes

# v2 format constants.
VERSION = b'\x02'  # Version marker identifying the authenticated (GCM) format.
SALT_SIZE = 16
NONCE_SIZE = 16
TAG_SIZE = 16
KEY_SIZE = 32

# scrypt work factors (deliberately slow).
SCRYPT_N = 2 ** 14
SCRYPT_R = 8
SCRYPT_P = 1

# Block size used by the legacy (v1) PKCS7 padding implementation.
LEGACY_BLOCK_SIZE = 32


class AESCipher:
    """AES-GCM cipher with scrypt key derivation and legacy CBC decryption."""

    def __init__(self, key, salt=None, nonce=None):
        """Initialise the cipher with a password.

        :param key: The password/secret used to derive the encryption key.
        :param salt: Optional fixed salt for deterministic testing. When
            omitted, a fresh random salt is generated for every encryption.
        :param nonce: Optional fixed nonce for deterministic testing. When
            omitted, a fresh random nonce is generated for every encryption.
        """
        self._password = key
        self._salt = salt
        self._nonce = nonce
        self.bs = LEGACY_BLOCK_SIZE

    def encrypt(self, raw):
        """Encrypt ``raw`` bytes and return a base64-encoded ``bytes`` payload.

        :param raw: The plaintext to encrypt. Must be ``bytes``.
        :returns: The base64-encoded authenticated ciphertext as ``bytes``.
        :raises TypeError: If ``raw`` is not ``bytes``.
        """
        if not isinstance(raw, bytes):
            raise TypeError(f'encrypt() requires bytes, got {type(raw).__name__}')

        salt = self._salt if self._salt is not None else get_random_bytes(SALT_SIZE)
        nonce = self._nonce if self._nonce is not None else get_random_bytes(NONCE_SIZE)

        key = scrypt(self._password.encode('utf-8'), salt, KEY_SIZE,
                     N=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P)

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        cipher.update(VERSION)
        cipher.update(salt)
        ciphertext, tag = cipher.encrypt_and_digest(raw)

        return base64.b64encode(VERSION + salt + nonce + tag + ciphertext)

    def decrypt(self, enc):
        """Decrypt a base64 payload and return the plaintext as a ``str``.

        Accepts the payload either as ``bytes`` or as a ``str`` (UTF-8). Payloads
        whose first decoded byte is the v2 version marker are tried as AES-GCM
        first; if GCM authentication fails they are retried as legacy AES-CBC
        ciphertexts, but only when the payload is structurally legacy-shaped
        (length ``16 + 16*k`` bytes) because a legacy IV may coincidentally begin
        with the marker. All other payloads are treated as legacy AES-CBC
        ciphertexts.

        :param enc: The base64-encoded ciphertext (``bytes`` or ``str``).
        :returns: The decrypted plaintext as a ``str``.
        :raises ValueError: If the payload is malformed, tampered with, or the
            password is wrong.
        """
        if isinstance(enc, str):
            enc = enc.encode('utf-8')

        data = base64.b64decode(enc)

        if data[:1] == VERSION:
            try:
                return self._decrypt_v2(data)
            except ValueError as v2_error:
                if not self._looks_like_legacy(data):
                    raise
                try:
                    return self._decrypt_legacy(data)
                except Exception:
                    raise v2_error

        return self._decrypt_legacy(data)

    @staticmethod
    def _looks_like_legacy(data):
        """Return True if ``data`` is structurally a legacy CBC payload."""
        if not isinstance(data, bytes) or len(data) < 2 * AES.block_size:
            return False
        return (len(data) - AES.block_size) % AES.block_size == 0

    def _decrypt_v2(self, data):
        """Decrypt an authenticated (v2) payload and return the UTF-8 string."""
        version = data[:1]
        salt = data[1:1 + SALT_SIZE]
        nonce = data[1 + SALT_SIZE:1 + SALT_SIZE + NONCE_SIZE]
        tag = data[1 + SALT_SIZE + NONCE_SIZE:1 + SALT_SIZE + NONCE_SIZE + TAG_SIZE]
        ciphertext = data[1 + SALT_SIZE + NONCE_SIZE + TAG_SIZE:]

        key = scrypt(self._password.encode('utf-8'), salt, KEY_SIZE,
                     N=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P)

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        cipher.update(version)
        cipher.update(salt)

        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode('utf-8')

    def _decrypt_legacy(self, data):
        """Decrypt a legacy (v1) AES-CBC payload and return the UTF-8 string."""
        iv = data[:AES.block_size]
        key = hashlib.sha256(self._password.encode()).digest()

        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(data[AES.block_size:])

        return self._unpad(plaintext).decode('utf-8')

    def _pad(self, data):
        """Apply PKCS7 padding to ``data`` (``bytes``) to the legacy block size."""
        if not isinstance(data, bytes):
            raise TypeError(f'_pad() requires bytes, got {type(data).__name__}')

        pad_len = self.bs - (len(data) % self.bs)
        return data + bytes([pad_len]) * pad_len

    @staticmethod
    def _unpad(data):
        """Remove and validate PKCS7 padding from ``data`` (``bytes``).

        :raises TypeError: If ``data`` is not ``bytes``.
        :raises ValueError: If the padding is malformed or missing.
        """
        if not isinstance(data, bytes):
            raise TypeError(f'_unpad() requires bytes, got {type(data).__name__}')

        if not data:
            raise ValueError('cannot unpad empty data')

        pad_len = data[-1]

        if pad_len == 0 or pad_len > LEGACY_BLOCK_SIZE or pad_len > len(data):
            raise ValueError('invalid PKCS7 padding length')

        if data[-pad_len:] != bytes([pad_len]) * pad_len:
            raise ValueError('invalid PKCS7 padding')

        return data[:-pad_len]
