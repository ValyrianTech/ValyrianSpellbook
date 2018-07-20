#!/usr/bin/env python
# -*- coding: utf-8 -*-

from helpers.configurationhelpers import get_use_testnet
from pybitcointools import bip32_ckd, bip32_master_key, bip32_privtopub


HARDENED = 2**31

MAINNET_PRIVATE = b'\x04\x88\xAD\xE4'
MAINNET_PUBLIC = b'\x04\x88\xB2\x1E'
TESTNET_PRIVATE = b'\x04\x35\x83\x94'
TESTNET_PUBLIC = b'\x04\x35\x87\xCF'

VERSION_BYTES = TESTNET_PRIVATE if get_use_testnet() is True else MAINNET_PRIVATE


def set_chain_mode(mainnet=True):
    """
    Override the configuration to switch between mainnet and testnet mode

    :param mainnet: True or False
    """
    global VERSION_BYTES
    VERSION_BYTES = MAINNET_PRIVATE if mainnet is True else TESTNET_PRIVATE


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
    parts = derivation_path.split('/')

    if parts[0] != 'm':
        raise Exception('Derivation path should start with "m", got %s' % derivation_path)

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
