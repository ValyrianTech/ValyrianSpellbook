#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import base64
from binascii import unhexlify, b2a_base64
import hashlib

from py2specials import *
from py3specials import *

# Regular expressions for private key formats
wif_compressed_regex = '^[LK][1-9A-Za-z][^OIl]{50}$'
wif_uncompressed_regex = '^5[HJK][1-9A-Za-z][^OIl]{48}$'
hexadecimal_regex = '^[0-9a-fA-F]{64}$'
base64_regex = '^[-A-Za-z0-9+=]{1,50}|=[^=]|={3,}$'


class PrivateKey(object):
    def __init__(self, private_key, testnet=False):
        vbyte = 0 if testnet is False else 111

        self.decimal = encode_privkey(private_key=private_key, formt='decimal', vbyte=vbyte)
        self.bin = encode_privkey(private_key=private_key, formt='bin', vbyte=vbyte)
        self.binc = encode_privkey(private_key=private_key, formt='bin_compressed', vbyte=vbyte)
        self.hex = encode_privkey(private_key=private_key, formt='hex', vbyte=vbyte).upper()
        self.hexc = encode_privkey(private_key=private_key, formt='hex_compressed', vbyte=vbyte).upper()
        self.wif = encode_privkey(private_key=private_key, formt='wif', vbyte=vbyte)
        self.wifc = encode_privkey(private_key=private_key, formt='wif_compressed', vbyte=vbyte)

        print ""
        print self.decimal
        print self.bin
        print self.binc
        print self.hex
        print self.hexc
        print self.wif
        print self.wifc

        self.base64 = None

        # # count how many parameters were given, must be exactly 1
        # n_args = sum([arg is not None for arg in [self.wifc, self.wif, self.hex, self.base64]])
        # if n_args != 1:
        #     raise Exception('You must provide a private key in one of the following formats: WIF compressed, WIF uncompressed, hexadecimal or base64')

        if self.wifc is not None:
            if re.match(wif_compressed_regex, self.wifc) is None:
                raise Exception('Invalid WIF compressed key: %s' % self.wifc)

        elif self.wif is not None:
            if re.match(wif_uncompressed_regex, self.wif) is None:
                raise Exception('Invalid WIF uncompressed key: %s' % self.wif)

        elif self.hex is not None:
            if re.match(hexadecimal_regex, self.hex) is None:
                raise Exception('Invalid HEX key: %s' % self.hex)

        # elif self.base64 is not None:
        #     if re.match(base64_regex, self.base64) is None or len(self.base64) != 44:
        #         raise Exception('Invalid base64 key: %s' % self.base64)
        #


def encode_privkey(private_key, formt, vbyte=0):
    if not isinstance(private_key, int_types):
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
        raise Exception("Invalid format!")


def decode_privkey(private_key, formt=None):
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
        raise Exception("WIF does not represent privkey")


def get_privkey_format(private_key):
    if isinstance(private_key, int_types):
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
            raise Exception("WIF does not represent privkey")


def b58check_to_bin(private_key):
    leadingzbytes = len(re.match('^1*', private_key).group(0))
    data = b'\x00' * leadingzbytes + changebase(private_key, 58, 256)
    assert bin_dbl_sha256(data[:-4])[:4] == data[-4:]
    return data[1:-4]

