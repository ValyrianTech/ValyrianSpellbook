#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .py3specials import *

from .jacobianhelpers import fast_add, A, B, P
from py_ripemd160 import ripemd160


def get_pubkey_format(pub):
    if isinstance(pub, (tuple, list)):
        return 'decimal'
    elif len(pub) == 65 and pub[0] == four:
        return 'bin'
    elif len(pub) == 130 and pub[0:2] == '04':
        return 'hex'
    elif len(pub) == 33 and pub[0] in [two, three]:
        return 'bin_compressed'
    elif len(pub) == 66 and pub[0:2] in ['02', '03']:
        return 'hex_compressed'
    elif len(pub) == 64:
        return 'bin_electrum'
    elif len(pub) == 128:
        return 'hex_electrum'
    else:
        raise Exception("Pubkey not in recognized format")


def encode_pubkey(pub, formt):
    if not isinstance(pub, (tuple, list)):
        pub = decode_pubkey(pub)
    if formt == 'decimal':
        return pub
    elif formt == 'bin':
        return b'\x04' + encode(pub[0], 256, 32) + encode(pub[1], 256, 32)
    elif formt == 'bin_compressed':
        return from_int_to_byte(2+(pub[1] % 2)) + encode(pub[0], 256, 32)
    elif formt == 'hex':
        return '04' + encode(pub[0], 16, 64) + encode(pub[1], 16, 64)
    elif formt == 'hex_compressed':
        return '0'+str(2+(pub[1] % 2)) + encode(pub[0], 16, 64)
    elif formt == 'bin_electrum':
        return encode(pub[0], 256, 32) + encode(pub[1], 256, 32)
    elif formt == 'hex_electrum':
        return encode(pub[0], 16, 64) + encode(pub[1], 16, 64)
    else:
        raise Exception("Invalid format!")


def decode_pubkey(pub, formt=None):
    if not formt:
        formt = get_pubkey_format(pub)

    if formt == 'decimal':
        return pub
    elif formt == 'bin':
        return decode(pub[1:33], 256), decode(pub[33:65], 256)
    elif formt == 'bin_compressed':
        x = decode(pub[1:33], 256)
        beta = pow(int(x*x*x+A*x+B), int((P+1)//4), int(P))
        y = (P-beta) if ((beta + from_byte_to_int(pub[0])) % 2) else beta
        return x, y
    elif formt == 'hex':
        return decode(pub[2:66], 16), decode(pub[66:130], 16)
    elif formt == 'hex_compressed':
        return decode_pubkey(safe_from_hex(pub), 'bin_compressed')
    elif formt == 'bin_electrum':
        return decode(pub[:32], 256), decode(pub[32:64], 256)
    elif formt == 'hex_electrum':
        return decode(pub[:64], 16), decode(pub[64:128], 16)
    else:
        raise Exception("Invalid format!")


def add_pubkeys(p1, p2):
    f1, f2 = get_pubkey_format(p1), get_pubkey_format(p2)
    return encode_pubkey(fast_add(decode_pubkey(p1, f1), decode_pubkey(p2, f2)), f1)


def compress(pubkey):
    f = get_pubkey_format(pubkey)
    if 'compressed' in f:
        return pubkey
    elif f == 'bin':
        return encode_pubkey(decode_pubkey(pubkey, f), 'bin_compressed')
    elif f == 'hex' or f == 'decimal':
        return encode_pubkey(decode_pubkey(pubkey, f), 'hex_compressed')


def pubkey_to_address(pubkey, magicbyte=0):
    """
    Convert a public key to an address

    :param pubkey: A public key
    :param magicbyte: 0=mainnet, 111=testnet
    :return: A Bitcoin address
    """
    if isinstance(pubkey, (list, tuple)):
        pubkey = encode_pubkey(pubkey, 'bin')

    if len(pubkey) in [66, 130]:
        return bin_to_b58check(bin_hash160(binascii.unhexlify(pubkey)), magicbyte)

    return bin_to_b58check(bin_hash160(pubkey), magicbyte)


def bin_hash160(string):
    intermed = hashlib.sha256(string).digest()
    try:
        digest = ripemd160(hashlib.sha256(intermed).digest())
    except Exception as ex:
        raise Exception('Unable to get ripemd160 digest: %s' % ex)
    return digest