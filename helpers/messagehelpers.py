#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bitcoin
from bitcoin.wallet import CBitcoinSecret
from bitcoin.signmessage import BitcoinMessage, VerifyMessage, SignMessage

from helpers.configurationhelpers import get_use_testnet
bitcoin.SelectParams(name='testnet' if get_use_testnet() is True else 'mainnet')


def sign_message(message, private_key):
    key = CBitcoinSecret(private_key)
    return SignMessage(key=key, message=BitcoinMessage(message)).decode()


def verify_message(address, message, signature):
    print(f'Verifying message: {message} with signature: {signature} for address: {address}')
    tmp = BitcoinMessage(message)
    print(f'BitcoinMessage: {tmp}')
    try:
        return VerifyMessage(address=address, message=BitcoinMessage(message), sig=signature)
    except Exception as ex:
        return False


def sign_and_verify(private_key, message, address):
    key = CBitcoinSecret(private_key)
    signature = SignMessage(key=key, message=BitcoinMessage(message))
    assert VerifyMessage(address=address, message=BitcoinMessage(message), sig=signature)
    return signature
