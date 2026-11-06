"""Authenticated AES encryption/decryption cipher for the Valyrian Spellbook.

This module provides the :class:`AESCipher` class used to protect the hot wallet
and other secrets at rest.

The current (v2) format uses AES-GCM for authenticated encryption and a slow,
salted ``scrypt`` key-derivation function, which together provide:

- **Confidentiality** — the plaintext cannot be read without the password.
- **Integrity/authenticity** — any tampering with the ciphertext, tag, salt,
  version byte or magic prefix causes decryption to fail with a
  :class:`ValueError`.
- **Brute-force resistance** — ``scrypt`` (rather than a single SHA-256 round)
  makes offline password guessing expensive.

Ciphertext layout (v2, after base64 decoding)::

    <magic (2, b'SB')> | <version byte (1)> | <salt (16)> | <nonce (16)> | <tag (16)> | <ciphertext>

The magic prefix makes the v2 format unambiguous: a v2 payload can never be
confused with a legacy (v1) AES-CBC ciphertext whose random IV happens to begin
with the version byte. The magic, version byte and salt are all fed into the
GCM authenticator (AAD) so an attacker cannot swap any of them without
invalidating the tag.

For backward compatibility, the class can still *read* two older formats, but
only through explicit opt-in:

- Old v2 payloads (single ``VERSION`` byte, no magic) written by earlier
  releases are still decrypted transparently, and are authenticated exactly as
  they were before. Authentication failure raises :class:`ValueError`; there is
  no fallback.
- Legacy (v1) AES-CBC ciphertexts (with PKCS7 padding and a single SHA-256 key
  round) are no longer read by :meth:`decrypt` by default. They can be read by
  constructing the cipher with ``allow_legacy=True`` or by calling
  :meth:`decrypt_legacy`, both of which log a warning. The intended migration
  is to call :meth:`decrypt_legacy` once and then re-:meth:`encrypt` the
  plaintext into the authenticated v2 format.

There is no GCM->CBC downgrade: a payload that authenticates as v2 is never
retried as unauthenticated legacy, so tampered v2 data cannot be silently
decrypted and no padding/UTF-8 oracle is exposed.
"""

import base64
import binascii
import hashlib
import logging

from Crypto.Cipher import AES  # nosec B413 # pycryptodome, not the deprecated pyCrypto
from Crypto.Protocol.KDF import scrypt  # nosec B413 # pycryptodome, not the deprecated pyCrypto
from Crypto.Random import get_random_bytes  # nosec B413 # pycryptodome, not the deprecated pyCrypto

# v2 format constants.
MAGIC = b'SB'  # Unambiguous magic prefix so v2 can never be confused with a legacy IV.
VERSION = b'\x02'  # Version marker identifying the authenticated (GCM) format.
V2_PREFIX = MAGIC + VERSION
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
    """AES-GCM cipher with scrypt key derivation and opt-in legacy CBC decryption."""

    LOG = logging.getLogger('Spellbook')

    def __init__(self, key, salt=None, nonce=None, *, allow_legacy=False):
        """Initialise the cipher with a password.

        :param key: The password/secret used to derive the encryption key.
        :param salt: Optional fixed salt for deterministic testing. When
            omitted, a fresh random salt is generated for every encryption.
        :param nonce: Optional fixed nonce for deterministic testing. When
            omitted, a fresh random nonce is generated for every encryption.
        :param allow_legacy: When ``True``, :meth:`decrypt` may fall back to the
            unauthenticated legacy AES-CBC format for payloads that are not
            v2-prefixed. Defaults to ``False``; legacy wallets should be read
            via :meth:`decrypt_legacy` and re-encrypted instead.
        """
        self._password = key
        self._salt = salt
        self._nonce = nonce
        self._allow_legacy = allow_legacy
        self.bs = LEGACY_BLOCK_SIZE

    def encrypt(self, raw):
        """Encrypt ``raw`` bytes and return a base64-encoded ``bytes`` payload.

        Produces the v2 wire format ``MAGIC + VERSION + salt + nonce + tag +
        ciphertext`` (after base64 decoding), with ``MAGIC``, ``VERSION`` and
        the salt fed into the GCM AAD so a magic/version/salt swap invalidates
        the tag.

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
        cipher.update(MAGIC)
        cipher.update(VERSION)
        cipher.update(salt)
        ciphertext, tag = cipher.encrypt_and_digest(raw)

        return base64.b64encode(MAGIC + VERSION + salt + nonce + tag + ciphertext)

    def decrypt(self, enc):
        """Decrypt a base64 payload and return the plaintext as a ``str``.

        Payloads whose first decoded bytes are ``V2_PREFIX`` (magic + version)
        are decrypted as v2 only. Payloads whose first decoded byte is the old
        v2 ``VERSION`` marker (no magic) are decrypted as the old v2 layout
        only. In both cases GCM authentication failure raises
        :class:`ValueError`; there is no legacy fallback.

        A payload that is not v2-prefixed is only read as legacy AES-CBC when
        the cipher was constructed with ``allow_legacy=True`` (which logs a
        warning); otherwise :class:`ValueError` is raised explaining that
        legacy wallets must be migrated via :meth:`decrypt_legacy` /
        ``allow_legacy=True`` and re-encrypted.

        :param enc: The base64-encoded ciphertext (``bytes`` or ``str``).
        :returns: The decrypted plaintext as a ``str``.
        :raises ValueError: If the payload is malformed, tampered with, the
            password is wrong, or it is a legacy payload and legacy decryption
            is not enabled.
        """
        data = self._decode(enc)

        if data.startswith(V2_PREFIX):
            return self._decrypt_v2(data)

        if data[:1] == VERSION:
            return self._decrypt_v2(data)

        if self._allow_legacy:
            self.LOG.warning('Decrypting a legacy (unauthenticated AES-CBC) payload; '
                             'this fallback is deprecated and the wallet should be re-encrypted to v2')
            return self._decrypt_legacy(data)

        raise ValueError(
            'Unsupported ciphertext format: the payload is not a v2 (authenticated) '
            'ciphertext. Legacy (AES-CBC) wallets must be migrated before they can '
            'be read with the default cipher: construct AESCipher(key=..., '
            'allow_legacy=True) or call decrypt_legacy() to read it, then re-encrypt '
            'with encrypt().'
        )

    def decrypt_legacy(self, enc):
        """Decrypt a legacy (v1) AES-CBC payload and return the plaintext as a ``str``.

        This always uses the unauthenticated legacy path and logs a warning. It
        is intended for a one-time migration of known-legacy wallets: decrypt
        the payload here, then re-:meth:`encrypt` the plaintext into the
        authenticated v2 format.

        :param enc: The base64-encoded legacy ciphertext (``bytes`` or ``str``).
        :returns: The decrypted plaintext as a ``str``.
        :raises ValueError: If the payload is malformed, tampered with, or the
            password is wrong.
        """
        self.LOG.warning('Decrypting a legacy (unauthenticated AES-CBC) payload via '
                         'the explicit legacy path; re-encrypt with encrypt() to migrate to v2')
        return self._decrypt_legacy(self._decode(enc))

    @staticmethod
    def _decode(enc):
        """Validate and base64-decode ``enc`` (``bytes`` or ``str``) to raw bytes.

        :raises ValueError: If the payload is not strict base64.
        """
        if isinstance(enc, str):
            enc = enc.encode('utf-8')

        enc = enc.strip()

        try:
            return base64.b64decode(enc, validate=True)
        except binascii.Error as ex:
            raise ValueError(f'malformed base64 payload: {ex}') from ex

    def _decrypt_v2(self, data):
        """Decrypt an authenticated (v2) payload and return the UTF-8 string.

        Parses both the new magic-prefixed layout (``MAGIC + VERSION + salt +
        nonce + tag + ciphertext``) and the old v2 layout (``VERSION + salt +
        nonce + tag + ciphertext``). GCM authentication failures propagate as
        :class:`ValueError`, and a plaintext that is not valid UTF-8 is also
        converted to :class:`ValueError`.
        """
        if data.startswith(V2_PREFIX):
            offset = len(V2_PREFIX)
            aad_parts = (MAGIC, VERSION)
        else:
            offset = len(VERSION)
            aad_parts = (VERSION,)

        salt = data[offset:offset + SALT_SIZE]
        nonce = data[offset + SALT_SIZE:offset + SALT_SIZE + NONCE_SIZE]
        tag = data[offset + SALT_SIZE + NONCE_SIZE:offset + SALT_SIZE + NONCE_SIZE + TAG_SIZE]
        ciphertext = data[offset + SALT_SIZE + NONCE_SIZE + TAG_SIZE:]

        key = scrypt(self._password.encode('utf-8'), salt, KEY_SIZE,
                     N=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P)

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        for part in aad_parts:
            cipher.update(part)
        cipher.update(salt)

        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        try:
            return plaintext.decode('utf-8')
        except UnicodeDecodeError as ex:
            raise ValueError('decrypted plaintext is not valid UTF-8') from ex

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
