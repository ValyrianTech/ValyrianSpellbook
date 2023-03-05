#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import bitcoin
import simplejson
from bitcoin.wallet import CBitcoinSecret
from bitcoin.signmessage import BitcoinMessage, VerifyMessage, SignMessage
from helpers.hotwallethelpers import get_address_from_wallet, get_private_key_from_wallet
from helpers.configurationhelpers import get_use_testnet
from helpers.loghelpers import LOG

bitcoin.SelectParams(name='testnet' if get_use_testnet() is True else 'mainnet')


def sign_message(message, private_key):
    key = CBitcoinSecret(private_key)
    return SignMessage(key=key, message=BitcoinMessage(message)).decode()


def verify_message(address, message, signature):
    try:
        return VerifyMessage(address=address, message=BitcoinMessage(message), sig=signature)
    except Exception as ex:
        return False


def sign_and_verify(private_key, message, address):
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
    sha256_hash = hashlib.sha256(simplejson.dumps(message_data, sort_keys=True, indent=2).encode('utf-8')).hexdigest()
    message = '/sha256/%s' % sha256_hash

    signature = sign_message(message=message, private_key=private_key)
    assert verify_message(address=address, message=message, signature=signature)

    data = {'address': address,
            'message': message,
            'signature': signature,
            'data': message_data}

    return data
