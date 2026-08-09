
"""AES encryption/decryption cipher for the Valyrian Spellbook."""

import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher(object):
    """AES encryption/decryption cipher for the Valyrian Spellbook."""
    def __init__(self, key):
        """  init   method."""
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        """Encrypt a plaintext string using AES-CBC with PKCS7 padding."""
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        """Decrypt a ciphertext string using AES-CBC with PKCS7 unpadding."""
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        """Apply PKCS7 padding to the data to match the AES block size."""
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs).encode('ascii')

    @staticmethod
    def _unpad(s):
        """Remove PKCS7 padding from the decrypted data."""
        return s[:-ord(s[len(s) - 1:])]

