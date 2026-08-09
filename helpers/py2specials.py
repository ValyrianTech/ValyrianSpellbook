"""Python 2 compatibility helpers copied from Vitalik Buterin's pybitcointools."""
# Code copied from Vitalik Buterin's pybitcointools (library is no longer maintained)

import sys
import re
import binascii
import os
import hashlib


if sys.version_info.major == 2:
    string_types = (str, unicode)  # type: ignore[name-defined]  # noqa: F821
    string_or_bytes_types = string_types
    int_types = (int, float, long)  # type: ignore[name-defined]  # noqa: F821

    # Base switching
    code_strings = {
        2: '01',
        10: '0123456789',
        16: '0123456789abcdef',
        32: 'abcdefghijklmnopqrstuvwxyz234567',
        58: '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz',
        256: ''.join([chr(x) for x in range(256)])
    }

    # used in publickeyhelpers
    two = '\x02'
    three = '\x03'
    four = '\x04'

    def bin_dbl_sha256(s):
        """Double SHA-256 hash of the input bytes."""
        bytes_to_hash = from_string_to_bytes(s)
        return hashlib.sha256(hashlib.sha256(bytes_to_hash).digest()).digest()

    def lpad(msg, symbol, length):
        """Left-pad msg with symbol to reach the given length."""
        if len(msg) >= length:
            return msg
        return symbol * (length - len(msg)) + msg

    def get_code_string(base):
        """Return the character set for the given base encoding."""
        if base in code_strings:
            return code_strings[base]
        else:
            raise ValueError("Invalid base!")

    def changebase(string, frm, to, minlen=0):
        """Convert a string from one base encoding to another."""
        if frm == to:
            return lpad(string, get_code_string(frm)[0], minlen)
        return encode(decode(string, frm), to, minlen)

    def bin_to_b58check(inp, magicbyte=0):
        """Convert bytes to a Base58Check-encoded string with optional magic byte prefix."""
        if magicbyte == 0:
            inp = '\x00' + inp
        while magicbyte > 0:
            inp = chr(int(magicbyte % 256)) + inp
            magicbyte //= 256
        leadingzbytes = len(re.match('^\x00*', inp).group(0))
        checksum = bin_dbl_sha256(inp)[:4]
        return '1' * leadingzbytes + changebase(inp+checksum, 256, 58)

    def bytes_to_hex_string(b):
        """Convert bytes to a hex string."""
        return b.encode('hex')

    def safe_from_hex(s):
        """Decode a hex string to bytes."""
        return s.decode('hex')

    def from_int_representation_to_bytes(a):
        """Convert an integer to its string representation."""
        return str(a)

    def from_int_to_byte(a):
        """Convert an integer (0-255) to a single byte character."""
        return chr(a)

    def from_byte_to_int(a):
        """Convert a single byte character to its integer value."""
        return ord(a)

    def from_bytes_to_string(s):
        """Convert bytes to a string (no-op in Python 2)."""
        return s

    def from_string_to_bytes(a):
        """Convert a string to bytes (no-op in Python 2)."""
        return a

    def safe_hexlify(a):
        """Hex-encode the input and return a safe hex string."""
        return binascii.hexlify(a)

    def encode(val, base, minlen=0):
        """Encode an integer to a string in the given base with optional minimum length."""
        base, minlen = int(base), int(minlen)
        code_string = get_code_string(base)
        result = ""
        while val > 0:
            result = code_string[val % base] + result
            val //= base
        return code_string[0] * max(minlen - len(result), 0) + result

    def decode(string, base):
        """Decode a string in the given base to an integer."""
        base = int(base)
        code_string = get_code_string(base)
        result = 0
        if base == 16:
            string = string.lower()
        while len(string) > 0:
            result *= base
            result += code_string.find(string[0])
            string = string[1:]
        return result

    def random_string(x):
        """Return x random bytes."""
        return os.urandom(x)

    def print_to_stderr(message):
        """Print a message to stderr."""
        print >> sys.stderr, message  # noqa: F633
