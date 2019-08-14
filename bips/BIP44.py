#!/usr/bin/env python
# -*- coding: utf-8 -*-
from binascii import hexlify, unhexlify


from .BIP32 import bip32_ckd, bip32_extract_key, MAGICBYTE, bip32_master_key, VERSION_BYTES, bip32_privtopub
from .BIP39 import get_seed
from helpers.publickeyhelpers import encode_pubkey, pubkey_to_address
from helpers.privatekeyhelpers import encode_privkey, privkey_to_address
from helpers.configurationhelpers import get_use_testnet

HARDENED = 2**31
COIN_TYPE = 1 if get_use_testnet() is True else 0


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


def get_xpriv_key(mnemonic, passphrase="", account=0):
    # BIP32 paths: m / purpose' / coin_type' / account' / change / address_index
    # ' means a hardened path is used
    # path for bitcoin mainnet is m/44'/0'/0'/0/0
    # path for bitcoin testnet is m/44'/1'/0'/0/0

    seed = hexlify(get_seed(mnemonic=mnemonic, passphrase=passphrase))
    master_key = bip32_master_key(unhexlify(seed), vbytes=VERSION_BYTES)
    xpriv_key = bip32_ckd(bip32_ckd(bip32_ckd(master_key, 44+HARDENED), HARDENED+COIN_TYPE), HARDENED+account)

    return xpriv_key


def get_xpriv_keys(mnemonic, passphrase="", i=1):
    # BIP32 paths: m / purpose' / coin_type' / account' / change / address_index
    # ' means a hardened path is used
    # path for bitcoin mainnet is m/44'/0'/0'/0/0
    # path for bitcoin testnet is m/44'/1'/0'/0/0

    seed = hexlify(get_seed(mnemonic=mnemonic, passphrase=passphrase))
    private_key = bip32_master_key(unhexlify(seed), vbytes=VERSION_BYTES)
    xprivs = []
    for i in range(0, i):
        derived_private_key = bip32_ckd(bip32_ckd(bip32_ckd(private_key, 44+HARDENED), HARDENED+COIN_TYPE), HARDENED+i)
        xprivs.append(derived_private_key)

    return xprivs


def get_xpub_key(mnemonic, passphrase="", account=0):
    xpriv_key = get_xpriv_key(mnemonic=mnemonic, passphrase=passphrase, account=account)
    xpub_key = bip32_privtopub(xpriv_key)
    return xpub_key


def get_xpub_keys(mnemonic, passphrase="", i=1):
    # BIP32 paths: m / purpose' / coin_type' / account' / change / address_index
    # ' means a hardened path is used
    # path for bitcoin mainnet is m/44'/0'/0'/0/0
    # path for bitcoin testnet is m/44'/1'/0'/0/0

    seed = hexlify(get_seed(mnemonic=mnemonic, passphrase=passphrase))
    priv = bip32_master_key(unhexlify(seed), vbytes=VERSION_BYTES)
    xpubs = []
    for i in range(0, i):
        derived_private_key = bip32_ckd(bip32_ckd(bip32_ckd(priv, 44+HARDENED), HARDENED+COIN_TYPE), HARDENED+i)
        xpub = bip32_privtopub(derived_private_key)
        xpubs.append(xpub)

    return xpubs


def get_private_key(xpriv, i, k=0):
    """
    Get a private key derived from a xpriv key

    :param xpriv: The xpriv key
    :param i: The index of the address
    :param k: 0=normal addresses, 1=change addresses
    :return: A dict with the address as the key and the private key as the value
    """
    private_keys = {}
    priv0 = bip32_ckd(xpriv, k)

    private_key = bip32_ckd(priv0, i)
    wif_key = encode_privkey(bip32_extract_key(private_key), 'wif_compressed', vbyte=MAGICBYTE)
    address_from_private_key = privkey_to_address(wif_key, magicbyte=MAGICBYTE)
    private_keys[address_from_private_key] = wif_key

    return private_keys
