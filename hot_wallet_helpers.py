#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import getpass
import simplejson
from AESCipher import AESCipher
from configurationhelpers import get_wallet_dir, get_default_wallet
from BIP44.BIP44 import get_xpub_key, get_address_from_xpub

HOT_WALLET_PASSWORD = None


def get_hot_wallet():
    global HOT_WALLET_PASSWORD

    if HOT_WALLET_PASSWORD is None:
        prompt_decryption_password()

    wallet_dir, wallet_id = get_wallet_dir(), get_default_wallet()

    try:
        cipher = AESCipher(key=HOT_WALLET_PASSWORD)
        with open(os.path.join(wallet_dir, '%s.enc' % wallet_id), 'r') as input_file:
            encrypted_data = input_file.read()
            return simplejson.loads(cipher.decrypt(encrypted_data))

    except Exception:
        raise Exception('Invalid password to decrypt hot wallet!')


def prompt_decryption_password():
    global HOT_WALLET_PASSWORD
    # if this is running in pycharm console, make sure 'Emulate terminal in output console' is checked in the configuration
    # HOT_WALLET_PASSWORD = getpass.getpass('Enter the password to decrypt the hot wallet: ')
    HOT_WALLET_PASSWORD = ''  # Todo enable password prompt again after development is done


def get_address_from_wallet(account, index):
    xpub_key = get_xpub_key_from_wallet(account)
    return get_address_from_xpub(xpub=xpub_key, i=index)


def get_xpub_key_from_wallet(account):
    hot_wallet = get_hot_wallet()
    xpub_key = get_xpub_key(mnemonic=' '.join(hot_wallet['mnemonic']),
                            passphrase=hot_wallet['passphrase'],
                            account=account)

    # Explicitly delete the local variable hot wallet from memory as soon as possible for security reasons
    del hot_wallet

    return xpub_key



