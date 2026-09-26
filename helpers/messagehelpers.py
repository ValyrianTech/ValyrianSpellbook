#!/usr/bin/env python
"""Helper functions for signing and verifying Bitcoin messages."""
import hashlib

import bitcoin
import simplejson
from bitcoin.signmessage import BitcoinMessage, SignMessage, VerifyMessage
from bitcoin.wallet import CBitcoinSecret

from helpers.configurationhelpers import get_use_testnet
from helpers.hotwallethelpers import (
    get_address_from_wallet,
    get_private_key_from_wallet,
)

bitcoin.SelectParams(name='testnet' if get_use_testnet() is True else 'mainnet')


def sign_message(message, private_key):
    """Sign a message with a private key and return the signature as a string."""
    key = CBitcoinSecret(private_key)
    return SignMessage(key=key, message=BitcoinMessage(message)).decode()


def verify_message(address, message, signature):
    """Verify that a signature was produced by the owner of the given address."""
    try:
        return VerifyMessage(address=address, message=BitcoinMessage(message), sig=signature)
    except (ValueError, KeyError, TypeError, OSError):
        return False


def sign_and_verify(private_key, message, address):
    """Sign a message and immediately verify it, returning the signature."""
    key = CBitcoinSecret(private_key)
    signature = SignMessage(key=key, message=BitcoinMessage(message))
    assert VerifyMessage(address=address, message=BitcoinMessage(message), sig=signature)
    return signature


def sign_data(message_data: dict, account: int, index: int):
    """Signs the data with the private key of the hot wallet at the specified account and index

    :param message_data: The data to sign
    :type message_data: dict
    :param account: The account of the wallet to use
    :type account: int
    :param index: The index of the wallet to use
    :type index: int

    :return: The signed data
    :rtype: dict

    :raises AssertionError: If the signature is not valid
    """

    address = get_address_from_wallet(account=account, index=index)
    private_key = get_private_key_from_wallet(account=account, index=index)[address]

    # calculate the sha256 hash of the ipfs_object
    sha256_hash = hashlib.sha256(simplejson.dumps(message_data, sort_keys=True, indent=2, ensure_ascii=False).encode('utf-8')).hexdigest()
    message = f'/sha256/{sha256_hash}'

    signature = sign_message(message=message, private_key=private_key)
    assert verify_message(address=address, message=message, signature=signature)

    data = {'address': address,
            'message': message,
            'signature': signature,
            'data': message_data}

    return data
