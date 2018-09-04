#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import hmac

from helpers.py2specials import *
from helpers.py3specials import *
from helpers.privatekeyhelpers import privkey_to_pubkey, add_privkeys
from helpers.publickeyhelpers import add_pubkeys, compress, bin_hash160, encode_pubkey, pubkey_to_address

from helpers.configurationhelpers import get_use_testnet

BIP32_DERIVATION_PATH_REGEX = "^m(\/\d+'?)*"
HARDENED = 2**31

MAINNET_PRIVATE = b'\x04\x88\xAD\xE4'
MAINNET_PUBLIC = b'\x04\x88\xB2\x1E'
TESTNET_PRIVATE = b'\x04\x35\x83\x94'
TESTNET_PUBLIC = b'\x04\x35\x87\xCF'
PRIVATE = [MAINNET_PRIVATE, TESTNET_PRIVATE]
PUBLIC = [MAINNET_PUBLIC, TESTNET_PUBLIC]

VERSION_BYTES = TESTNET_PRIVATE if get_use_testnet() is True else MAINNET_PRIVATE
MAGICBYTE = 111 if get_use_testnet() is True else 0


def set_chain_mode(mainnet=True):
    """
    Override the configuration to switch between mainnet and testnet mode

    :param mainnet: True or False
    """
    global VERSION_BYTES, MAGICBYTE
    VERSION_BYTES = MAINNET_PRIVATE if mainnet is True else TESTNET_PRIVATE
    MAGICBYTE = 0 if mainnet is True else 111

# Set the chain mode based on the current configuration
set_chain_mode(mainnet=(get_use_testnet() is False))


def parse_derivation_path(derivation_path):
    """
    Parse a derivation path

    BIP32 paths: m / purpose' / coin_type' / account' / change / address_index
    ' means a hardened path is used: 2**31 is added to the number
    example path for bitcoin mainnet is m/44'/0'/0'/0/0
    example path for bitcoin testnet is m/44'/1'/0'/0/0

    :param derivation_path: A string
    :return: a list containing the child index for each depth in the derivation path
    """
    if re.match(BIP32_DERIVATION_PATH_REGEX, derivation_path) is None:
        raise Exception('Derivation path is invalid: %s' % derivation_path)

    parts = derivation_path.split('/')

    child_indexes = []
    if len(parts) > 1:
        for part in parts[1:]:
            child_indexes.append(int(part[:-1]) + HARDENED if part.endswith("'") else int(part))

    return child_indexes


def get_xpriv(seed, derivation_path):
    """
    Get the extended private key

    :param seed: The seed as a binary number
    :param derivation_path: The derivation path (example: m/44'/0'/0'/1/2 , a ' indicates a hardened child)
    :return: A xpriv key
    """
    # First derive the master key
    child_key = bip32_master_key(seed, vbytes=VERSION_BYTES)

    # For each depth in the derivation path, derive the child key recursively
    for child_index in parse_derivation_path(derivation_path=derivation_path):
        child_key = bip32_ckd(data=child_key, i=child_index)

    return child_key


def get_xpub(seed, derivation_path):
    """
    Get the extended public key

    :param seed: The seed as a binary number
    :param derivation_path: The derivation path (example: m/44'/0'/0'/1/2 , a ' indicates a hardened child)
    :return: A xpub key
    """
    return bip32_privtopub(data=get_xpriv(seed=seed, derivation_path=derivation_path))


def get_xpub_child(xpub, child_index):
    """
    Derive an xpub key from a parent xpub key

    :param xpub: The parent xpub key
    :param child_index: The index of the child, note: must be non-hardened (smaller than 2**31)
    :return:
    """
    if child_index >= HARDENED:
        raise Exception('Only non-hardened child xpubs keys can be derived from an xpub key')

    return bip32_ckd(data=xpub, i=child_index)

# ----------------------------------------------------------------------------------------------------------------------


def bip32_ckd(data, i):
    return bip32_serialize(raw_bip32_ckd(bip32_deserialize(data), i))


def bip32_serialize(rawtuple):
    vbytes, depth, fingerprint, i, chaincode, key = rawtuple
    i = encode(i, 256, 4)
    chaincode = encode(hash_to_int(chaincode), 256, 32)
    keydata = b'\x00'+key[:-1] if vbytes in PRIVATE else key
    bindata = vbytes + from_int_to_byte(depth % 256) + fingerprint + i + chaincode + keydata
    return changebase(bindata+bin_dbl_sha256(bindata)[:4], 256, 58)


def bip32_deserialize(data):
    dbin = changebase(data, 58, 256)
    if bin_dbl_sha256(dbin[:-4])[:4] != dbin[-4:]:
        raise Exception("Invalid checksum")
    vbytes = dbin[0:4]
    depth = from_byte_to_int(dbin[4])
    fingerprint = dbin[5:9]
    i = decode(dbin[9:13], 256)
    chaincode = dbin[13:45]
    key = dbin[46:78]+b'\x01' if vbytes in PRIVATE else dbin[45:78]
    return vbytes, depth, fingerprint, i, chaincode, key


def raw_bip32_ckd(rawtuple, i):
    vbytes, depth, fingerprint, oldi, chaincode, key = rawtuple
    i = int(i)

    if vbytes in PRIVATE:
        priv = key
        pub = privkey_to_pubkey(key)
    else:
        pub = key

    if i >= 2**31:
        if vbytes in PUBLIC:
            raise Exception("Can't do private derivation on public key!")
        I = hmac.new(chaincode, b'\x00'+priv[:32]+encode(i, 256, 4), hashlib.sha512).digest()
    else:
        I = hmac.new(chaincode, pub+encode(i, 256, 4), hashlib.sha512).digest()

    if vbytes in PRIVATE:
        newkey = add_privkeys(I[:32]+B'\x01', priv)
        fingerprint = bin_hash160(privkey_to_pubkey(key))[:4]
    if vbytes in PUBLIC:
        newkey = add_pubkeys(compress(privkey_to_pubkey(I[:32])), key)
        fingerprint = bin_hash160(key)[:4]

    return vbytes, depth + 1, fingerprint, i, I[32:], newkey


def hash_to_int(x):
    if len(x) in [40, 64]:
        return decode(x, 16)
    return decode(x, 256)


# ----------------------------------------------------------------------------------------------------------------------


def bip32_master_key(seed, vbytes=MAINNET_PRIVATE):
    I = hmac.new(
            from_string_to_bytes("Bitcoin seed"),
            from_string_to_bytes(seed),
            hashlib.sha512
        ).digest()
    return bip32_serialize((vbytes, 0, b'\x00'*4, 0, I[32:], I[:32]+b'\x01'))

# ----------------------------------------------------------------------------------------------------------------------


def raw_bip32_privtopub(rawtuple):
    vbytes, depth, fingerprint, i, chaincode, key = rawtuple
    newvbytes = MAINNET_PUBLIC if vbytes == MAINNET_PRIVATE else TESTNET_PUBLIC
    return newvbytes, depth, fingerprint, i, chaincode, privkey_to_pubkey(key)


def bip32_privtopub(data):
    return bip32_serialize(raw_bip32_privtopub(bip32_deserialize(data)))


def bip32_extract_key(data):
    return safe_hexlify(bip32_deserialize(data)[-1])
