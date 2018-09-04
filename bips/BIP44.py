#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BIP32 import bip32_ckd, bip32_extract_key, MAGICBYTE
from helpers.publickeyhelpers import encode_pubkey, pubkey_to_address


def get_address_from_xpub(xpub, i):
    """
    Get a Bitcoin address from an xpub key

    :param xpub: The xpub key
    :param i: The index of the address
    :return: A Bitcoin Address
    """
    pub0 = bip32_ckd(xpub, 0)
    public_key = bip32_ckd(pub0, i)
    hex_key = encode_pubkey(bip32_extract_key(public_key), 'hex_compressed')
    address = pubkey_to_address(hex_key, magicbyte=MAGICBYTE)

    return address


def get_addresses_from_xpub(xpub, i=100):
    """
    Get a list of addresses derived from an xpub key

    :param xpub: The xpub key
    :param i: The number of addresses to derive
    :return: A list of Bitcoin addresses
    """
    address_list = []
    pub0 = bip32_ckd(xpub, 0)

    for i in range(0, i):
        public_key = bip32_ckd(pub0, i)
        hex_key = encode_pubkey(bip32_extract_key(public_key), 'hex_compressed')
        address_from_public_key = pubkey_to_address(hex_key, magicbyte=MAGICBYTE)
        address_list.append(address_from_public_key)

    return address_list


def get_change_addresses_from_xpub(xpub, i=100):
    """
    Get a list of change addresses derived from an xpub key

    :param xpub: The xpub key
    :param i: The number of addresses to derive
    :return: A list of Bitcoin addresses
    """
    address_list = []
    pub0 = bip32_ckd(xpub, 1)

    for i in range(0, i):
        public_key = bip32_ckd(pub0, i)
        hex_key = encode_pubkey(bip32_extract_key(public_key), 'hex_compressed')
        address_from_public_key = pubkey_to_address(hex_key, magicbyte=MAGICBYTE)
        address_list.append(address_from_public_key)

    return address_list
