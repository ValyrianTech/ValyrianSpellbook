#!/usr/bin/env python
"""Helper functions for encoding, decoding, and manipulating Bitcoin private keys."""
import re

from .jacobianhelpers import G, N, fast_multiply
from .publickeyhelpers import encode_pubkey, pubkey_to_address
from .py3specials import bin_dbl_sha256, bin_to_b58check, changebase, decode, encode

# Regular expressions for private key formats
wif_compressed_regex = '^[LK][1-9A-Za-z][^OIl]{50}$'
wif_uncompressed_regex = '^5[HJK][1-9A-Za-z][^OIl]{48}$'
hexadecimal_regex = '^[0-9a-fA-F]{64}$'
base64_regex = '^[-A-Za-z0-9+=]{1,50}|=[^=]|={3,}$'


class PrivateKey:
    """
    Represents a Bitcoin private key in multiple formats (WIF, hex, decimal, binary).

    Initializes the private key from any supported format, deriving all representations.
    """
    def __init__(self, private_key, testnet=False):
        vbyte = 0 if testnet is False else 111

        self.decimal = encode_privkey(private_key=private_key, formt='decimal', vbyte=vbyte)
        self.bin = encode_privkey(private_key=private_key, formt='bin', vbyte=vbyte)
        self.binc = encode_privkey(private_key=private_key, formt='bin_compressed', vbyte=vbyte)
        self.hex = encode_privkey(private_key=private_key, formt='hex', vbyte=vbyte).upper()
        self.hexc = encode_privkey(private_key=private_key, formt='hex_compressed', vbyte=vbyte).upper()
        self.wif = encode_privkey(private_key=private_key, formt='wif', vbyte=vbyte)
        self.wifc = encode_privkey(private_key=private_key, formt='wif_compressed', vbyte=vbyte)

        if self.wifc is not None:
            if re.match(wif_compressed_regex, self.wifc) is None:
                raise ValueError(f'Invalid WIF compressed key: {self.wifc}')

        elif self.wif is not None:  # pragma: no cover
            if re.match(wif_uncompressed_regex, self.wif) is None:
                raise ValueError(f'Invalid WIF uncompressed key: {self.wif}')

        elif self.hex is not None and re.match(hexadecimal_regex, self.hex) is None:  # pragma: no cover
            raise ValueError(f'Invalid HEX key: {self.hex}')


def encode_privkey(private_key, formt, vbyte=0):
    """Encode a private key integer into the requested format (decimal, bin, hex, wif, etc.)."""
    if not isinstance(private_key, (int, float)):
        return encode_privkey(decode_privkey(private_key), formt, vbyte)

    if formt == 'decimal':
        return private_key
    elif formt == 'bin':
        return encode(private_key, 256, 32)
    elif formt == 'bin_compressed':
        return encode(private_key, 256, 32) + b'\x01'
    elif formt == 'hex':
        return encode(private_key, 16, 64)
    elif formt == 'hex_compressed':
        return encode(private_key, 16, 64) + '01'
    elif formt == 'wif':
        return bin_to_b58check(encode(private_key, 256, 32), 128 + int(vbyte))
    elif formt == 'wif_compressed':
        return bin_to_b58check(encode(private_key, 256, 32) + b'\x01', 128 + int(vbyte))
    else:
        raise ValueError("Invalid format!")


def decode_privkey(private_key, formt=None):
    """Decode a private key from any supported format to a decimal integer."""
    if not formt:
        formt = get_privkey_format(private_key)

    if formt == 'decimal':
        return private_key
    elif formt == 'bin':
        return decode(private_key, 256)
    elif formt == 'bin_compressed':
        return decode(private_key[:32], 256)
    elif formt == 'hex':
        return decode(private_key, 16)
    elif formt == 'hex_compressed':
        return decode(private_key[:64], 16)
    elif formt == 'wif':
        return decode(b58check_to_bin(private_key), 256)
    elif formt == 'wif_compressed':
        return decode(b58check_to_bin(private_key)[:32], 256)
    else:
        raise ValueError("WIF does not represent privkey")


def get_privkey_format(private_key):
    """Detect the format of a private key (decimal, bin, hex, wif, etc.)."""
    if isinstance(private_key, (int, float)):
        return 'decimal'
    elif len(private_key) == 32:
        return 'bin'
    elif len(private_key) == 33:
        return 'bin_compressed'
    elif len(private_key) == 64:
        return 'hex'
    elif len(private_key) == 66:
        return 'hex_compressed'
    else:
        bin_p = b58check_to_bin(private_key)
        if len(bin_p) == 32:
            return 'wif'
        elif len(bin_p) == 33:
            return 'wif_compressed'
        else:
            raise ValueError("WIF does not represent privkey")


def b58check_to_bin(private_key):
    """Convert a Base58Check-encoded private key to raw bytes (stripping prefix and checksum)."""
    leadingzbytes = len(re.match('^1*', private_key).group(0))
    data = b'\x00' * leadingzbytes + changebase(private_key, 58, 256)
    assert bin_dbl_sha256(data[:-4])[:4] == data[-4:]
    return data[1:-4]


def privkey_to_pubkey(privkey):
    """Derive the public key from a private key by scalar multiplication of the generator point."""
    f = get_privkey_format(privkey)
    privkey = decode_privkey(privkey, f)
    if privkey >= N:
        raise ValueError("Invalid privkey")
    if f in ['bin', 'bin_compressed', 'hex', 'hex_compressed', 'decimal']:
        return encode_pubkey(fast_multiply(G, privkey), f)
    else:
        return encode_pubkey(fast_multiply(G, privkey), f.replace('wif', 'hex'))


def add_privkeys(p1, p2):
    """Add two private keys together modulo the curve order N."""
    f1, f2 = get_privkey_format(p1), get_privkey_format(p2)
    return encode_privkey((decode_privkey(p1, f1) + decode_privkey(p2, f2)) % N, f1)


def privkey_to_address(priv, magicbyte=0):
    """Derive a Bitcoin address from a private key."""
    return pubkey_to_address(privkey_to_pubkey(priv), magicbyte)
