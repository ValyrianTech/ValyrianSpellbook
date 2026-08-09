#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helper functions for managing the encrypted hot wallet (keys, addresses, seeds)."""

import os
import getpass
import simplejson

from AESCipher import AESCipher
from bips.BIP44 import get_address_from_xpub, get_addresses_from_xpub, get_xpriv_key, get_xpub_key, get_private_key
from helpers.configurationhelpers import get_wallet_dir, get_default_wallet
from bips.BIP39 import get_seed

HOT_WALLET_PASSWORD = None


def get_hot_wallet():
    """Decrypt and return the hot wallet data, prompting for password if needed."""
    global HOT_WALLET_PASSWORD
    wallet_dir, wallet_id = get_wallet_dir(), get_default_wallet()

    if HOT_WALLET_PASSWORD is None:
        # Try empty password first (Reminder: in production there should always be a decryption password for the hot wallet)
        try:
            cipher = AESCipher(key='')
            with open(os.path.join(wallet_dir, '%s.enc' % wallet_id), 'r') as input_file:
                encrypted_data = input_file.read()
                return simplejson.loads(cipher.decrypt(encrypted_data))

        except Exception:
            prompt_decryption_password()

    try:
        cipher = AESCipher(key=HOT_WALLET_PASSWORD)
        with open(os.path.join(wallet_dir, '%s.enc' % wallet_id), 'r') as input_file:
            encrypted_data = input_file.read()
            return simplejson.loads(cipher.decrypt(encrypted_data))

    except Exception:
        raise Exception('Invalid password to decrypt hot wallet!')


def prompt_decryption_password():
    """Prompt the user for the hot wallet decryption password."""
    global HOT_WALLET_PASSWORD
    # if this is running in pycharm console, make sure 'Emulate terminal in output console' is checked in the configuration
    HOT_WALLET_PASSWORD = getpass.getpass('Enter the password to decrypt the hot wallet: ')


def get_address_from_wallet(account, index):
    """Derive a Bitcoin address from the hot wallet for the given account and index."""
    xpub_key = get_xpub_key_from_wallet(account)
    return get_address_from_xpub(xpub=xpub_key, i=index)


def get_xpub_key_from_wallet(account):
    """Derive the xpub key for the given account from the hot wallet."""
    hot_wallet = get_hot_wallet()
    xpub_key = get_xpub_key(mnemonic=' '.join(hot_wallet['mnemonic']),
                            passphrase=hot_wallet['passphrase'],
                            account=account)

    # Explicitly delete the local variable hot wallet from memory as soon as possible for security reasons
    del hot_wallet

    return xpub_key


def get_xpriv_key_from_wallet(account):
    """Derive the xpriv key for the given account from the hot wallet."""
    hot_wallet = get_hot_wallet()
    xpriv_key = get_xpriv_key(mnemonic=' '.join(hot_wallet['mnemonic']),
                              passphrase=hot_wallet['passphrase'],
                              account=account)

    # Explicitly delete the local variable hot wallet from memory as soon as possible for security reasons
    del hot_wallet

    return xpriv_key


def get_private_key_from_wallet(account, index):
    """Derive the private key for the given account and index from the hot wallet."""
    xpriv_key = get_xpriv_key_from_wallet(account=account)
    return get_private_key(xpriv=xpriv_key, i=index)


def get_single_address_private_key(address):
    """Retrieve the private key for a single address stored directly in the hot wallet."""
    hot_wallet = get_hot_wallet()

    if address in hot_wallet:
        return {address: hot_wallet[address]}


def find_address_in_wallet(address, accounts=1, indexes=20):
    """Search the hot wallet for the given address across accounts and indexes."""
    hot_wallet = get_hot_wallet()

    for account in range(accounts):
        xpub_key = get_xpub_key(mnemonic=' '.join(hot_wallet['mnemonic']),
                                passphrase=hot_wallet['passphrase'],
                                account=account)

        addresses = get_addresses_from_xpub(xpub=xpub_key, i=indexes)

        if address in addresses:
            return account, addresses.index(address)

    return None, None


def find_single_address_in_wallet(address):
    """Check if a single address exists directly in the hot wallet."""
    hot_wallet = get_hot_wallet()

    return hot_wallet[address] if address in hot_wallet else None


def hot_wallet_seed():
    """Derive the seed from the hot wallet mnemonic and passphrase."""
    hot_wallet = get_hot_wallet()
    return get_seed(mnemonic=' '.join(hot_wallet['mnemonic']), passphrase=hot_wallet['passphrase'])


def find_account_by_xpub(xpub, n=20):
    """Find the account index that matches the given xpub by scanning up to n accounts."""
    hot_wallet = get_hot_wallet()

    for i in range(n):
        account_xpub = get_xpub_key(mnemonic=' '.join(hot_wallet['mnemonic']),
                                    passphrase=hot_wallet['passphrase'],
                                    account=i)
        if xpub == account_xpub:
            return i
