"""Python 3 compatibility helpers copied from Vitalik Buterin's pybitcointools."""
# Code copied from Vitalik Buterin's pybitcointools (library is no longer maintained)

import binascii
import hashlib
import os
import re
import sys
from functools import reduce  # noqa: F401 - re-exported for backward compatibility

string_types = (str)
string_or_bytes_types = (str, bytes)
int_types = (int, float)
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
two = 2
three = 3
four = 4

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
        inp = from_int_to_byte(0) + inp
    while magicbyte > 0:
        inp = from_int_to_byte(magicbyte % 256) + inp
        magicbyte //= 256

    leadingzbytes = 0
    for x in inp:
        if x != 0:
            break
        leadingzbytes += 1

    checksum = bin_dbl_sha256(inp)[:4]
    return '1' * leadingzbytes + changebase(inp+checksum, 256, 58)

def bytes_to_hex_string(b):
    """Convert bytes to a hex string."""
    if isinstance(b, str):
        return b

    return ''.join(f'{y:02x}' for y in b)

def safe_from_hex(s):
    """Decode a hex string to bytes."""
    return bytes.fromhex(s)

def from_int_representation_to_bytes(a):
    """Convert an integer to its UTF-8 bytes representation."""
    return bytes(str(a), 'utf-8')

def from_int_to_byte(a):
    """Convert an integer (0-255) to a single byte."""
    return bytes([a])

def from_byte_to_int(a):
    """Convert a single byte to its integer value."""
    return a

def from_string_to_bytes(a):
    """Convert a string to bytes, encoding as UTF-8 if necessary."""
    return a if isinstance(a, bytes) else bytes(a, 'utf-8')

def safe_hexlify(a):
    """Hex-encode the input and return a safe UTF-8 hex string."""
    return str(binascii.hexlify(a), 'utf-8')

def encode(val, base, minlen=0):
    """Encode an integer to a string in the given base with optional minimum length."""
    base, minlen = int(base), int(minlen)
    code_string = get_code_string(base)
    result_bytes = b''
    while val > 0:
        curcode = code_string[val % base]
        result_bytes = bytes([ord(curcode)]) + result_bytes
        val //= base

    pad_size = minlen - len(result_bytes)

    padding_element = b'\x00' if base == 256 else b'1' \
            if base == 58 else b'0'
    if (pad_size > 0):
        result_bytes = padding_element*pad_size + result_bytes

    result_string = ''.join([chr(y) for y in result_bytes])
    result = result_bytes if base == 256 else result_string

    return result

def decode(string, base):
    """Decode a string in the given base to an integer."""
    if base == 256 and isinstance(string, str):
        string = bytes(bytearray.fromhex(string))
    base = int(base)
    code_string = get_code_string(base)
    result = 0
    if base == 256:
        def extract(d, cs):
            """Return the byte value directly for base-256 decoding."""
            return d
    else:
        def extract(d, cs):
            """Find the position of a character in the code string for decoding."""
            return cs.find(d if isinstance(d, str) else chr(d))

    if base == 16:
        string = string.lower()
    while len(string) > 0:
        result *= base
        result += extract(string[0], code_string)
        string = string[1:]
    return result

def random_string(x):
    """Return x random bytes as a string."""
    return str(os.urandom(x))

def print_to_stderr(message):
    """Print a message to stderr."""
    print(message, file=sys.stderr)


def b58check_to_bin(s):
    """Convert a Base58Check-encoded string to raw bytes, validating the checksum.

    Strips the version byte prefix (first byte) and the 4-byte checksum.
    Raises TypeError if `s` is not a str, ValueError if it is too short or has an
    invalid checksum. This validation is done explicitly (not via assert) so that
    it is NOT removed when Python runs with -O / PYTHONOPTIMIZE=1.
    """
    if not isinstance(s, str):
        raise TypeError(f'Base58Check string must be a str, got {type(s).__name__}')
    leadingzbytes = len(re.match('^1*', s).group(0))
    data = b'\x00' * leadingzbytes + changebase(s, 58, 256)
    if len(data) < 5:
        raise ValueError(f'Address too short to contain a checksum: {s!r}')
    if bin_dbl_sha256(data[:-4])[:4] != data[-4:]:
        raise ValueError(f'Invalid Base58Check checksum for address {s!r}')
    return data[1:-4]
