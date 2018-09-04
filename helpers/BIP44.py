#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bips.BIP32 import bip32_ckd, bip32_privtopub, bip32_master_key, bip32_extract_key, MAINNET_PRIVATE, TESTNET_PRIVATE
from bips.BIP39 import get_seed
from bips.BIP44 import get_addresses_from_xpub, get_change_addresses_from_xpub, get_xpriv_keys, get_xpub_keys
from helpers.publickeyhelpers import pubkey_to_address
from helpers.privatekeyhelpers import privkey_to_address, privkey_to_pubkey, encode_privkey

from binascii import hexlify, unhexlify
import json
import urllib2  # todo replace with requests
from pprint import pprint
import time

HARDENED = 2**31
MAGICBYTE = 0
VBYTES = MAINNET_PRIVATE
COIN_TYPE = 0


class BIP44Wallet(object):
    def __init__(self, mnemonic, passphrase="", account=0, n=100):
        self.mnemonic = mnemonic
        self.passphrase = passphrase
        self.account = account
        self.xpub_keys = get_xpub_keys(self.mnemonic, self.passphrase, account+1)
        self.xpriv_keys = get_xpriv_keys(self.mnemonic, self.passphrase, account+1)

        self.n = n
        self.addresses = get_addresses_from_xpub(self.xpub_keys[account], self.n)
        self.change_addresses = get_change_addresses_from_xpub(self.xpub_keys[account], self.n)

    def scan(self):
        unspent_outputs = {}
        chunk_size = 200
        k = 0
        for addressList in [self.addresses, self.change_addresses]:
            i = 0
            while i < self.n:
                chunk = addressList[i:i+chunk_size]

                url = 'https://blockchain.info/multiaddr?active={0}'.format('|'.join(chunk))
                ret = urllib2.urlopen(urllib2.Request(url))
                data = json.loads(ret.read())

                for j in range(0, len(data['addresses'])):
                    if data['addresses'][j]['final_balance'] > 0:
                        key_index = addressList.index(data['addresses'][j]['address'])
                        private_key = get_private_key(self.xpriv_keys[self.account], key_index, k)
                        unspent_outputs[data['addresses'][j]['address']] = {'value': data['addresses'][j]['final_balance'],
                                                                            'i': key_index,
                                                                            'private_key': private_key[data['addresses'][j]['address']],
                                                                            'change': k,
                                                                            "account": self.account}

                i += chunk_size
                time.sleep(1)

            k += 1

        pprint(unspent_outputs)

        total_value = 0
        for address in unspent_outputs:
            total_value += unspent_outputs[address]['value']

        print 'Total value:', total_value/1e8, 'BTC'

        return unspent_outputs

    def sweep(self, to_address):
        pass


def set_testnet(testnet=False):
    """
    Set the global variable MAGICBYTE for encoding the address:
    Bitcoin mainnet uses 0, Bitcoin testnet uses 111

    Set the global variable VBYTES for deriving the master key from a seed:
    MAINNET_PRIVATE = b'\x04\x88\xAD\xE4'
    TESTNET_PRIVATE = b'\x04\x35\x83\x94'

    Set the global variable COIN_TYPE for deriving the BIP32 path:
    Bitcoin mainnet uses 0, Bitcoin testnet uses 1

    :param testnet: Set to True for testnet (default=False -> mainnet)
    """
    global MAGICBYTE, VBYTES, COIN_TYPE
    MAGICBYTE, VBYTES, COIN_TYPE = (111, TESTNET_PRIVATE, 1) if testnet is True else (0, MAINNET_PRIVATE, 0)











def get_private_key(xpriv, i, k=0):
    private_keys = {}
    priv0 = bip32_ckd(xpriv, k)

    private_key = bip32_ckd(priv0, i)
    wif_key = encode_privkey(bip32_extract_key(private_key), 'wif_compressed', vbyte=MAGICBYTE)
    address_from_private_key = privkey_to_address(wif_key, magicbyte=MAGICBYTE)
    private_keys[address_from_private_key] = wif_key

    return private_keys








def show_details(mnemonic, passphrase="", n_accounts=1):
    seed = hexlify(get_seed(mnemonic=mnemonic, passphrase=passphrase))
    print 'Seed:\t\t\t\t', seed

    priv = bip32_master_key(unhexlify(seed), vbytes=VBYTES)
    print 'Xpriv:\t\t\t\t', priv

    key = encode_privkey(bip32_extract_key(priv), 'wif_compressed', vbyte=MAGICBYTE)
    print 'Key:\t\t\t\t', key

    pub = bip32_privtopub(priv)
    print 'Derived public key:\t', pub
    pub_hex = bip32_extract_key(pub)
    print 'public key (hex):\t', pub_hex
    print 'Master Key address:\t', pubkey_to_address(pub_hex, magicbyte=MAGICBYTE)

    print ""
    print "TREZOR Keys:"

    account = 0
    derived_private_key = bip32_ckd(bip32_ckd(bip32_ckd(priv, 44+HARDENED), HARDENED), HARDENED+account)
    print 'Derived private key:', derived_private_key

    private_key = encode_privkey(bip32_extract_key(derived_private_key), 'wif_compressed', vbyte=MAGICBYTE)
    print 'private key (wif):\t', private_key

    derived_public_key = bip32_privtopub(derived_private_key)
    print 'Derived public key:', derived_public_key

    public_key_hex = privkey_to_pubkey(private_key)
    print 'public key (hex):\t', public_key_hex

    address = pubkey_to_address(public_key_hex, magicbyte=MAGICBYTE)
    print 'address:\t\t\t', address

    print ""
    print "Account public keys (XPUB)"
    xpubs = []
    for i in range(0, n_accounts):
        derived_private_key = bip32_ckd(bip32_ckd(bip32_ckd(priv, 44+HARDENED), HARDENED+COIN_TYPE), HARDENED+i)
        xpub = bip32_privtopub(derived_private_key)
        print 'Account', i, 'xpub:', xpub
        xpubs.append(xpub)

    return xpubs
