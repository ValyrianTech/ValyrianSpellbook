#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
from bitcoin.core.key import CPubKey
from bitcoin.wallet import P2PKHBitcoinAddress

import bitcoin
from bitcoin.wallet import CBitcoinSecret
from bitcoin.signmessage import BitcoinMessage, VerifyMessage, SignMessage

from helpers.configurationhelpers import get_use_testnet
bitcoin.SelectParams(name='testnet' if get_use_testnet() is True else 'mainnet')


def sign_message(message, private_key):
    key = CBitcoinSecret(private_key)
    return SignMessage(key=key, message=BitcoinMessage(message)).decode()


def verify_message(address, message, signature):
    print(f'chain mode: {bitcoin.params.NAME}')
    print(f'Verifying message: {message} with signature: {signature} for address: {address}')
    tmp = BitcoinMessage(message)
    print(f'BitcoinMessage: {tmp.GetHash()}')

    sig = base64.b64decode(signature)
    print(f'sig: {sig}')
    hash = tmp.GetHash()
    print(f'hash: {hash}')

    pubkey = CPubKey.recover_compact(hash, sig)
    print(f'pubkey: {pubkey}')
    print(f'{str(P2PKHBitcoinAddress.from_pubkey(pubkey))}')
    print(f'{str(address)}')

    print(f'Result: {str(P2PKHBitcoinAddress.from_pubkey(pubkey)) == str(address)}')


    try:
        return VerifyMessage(address=address, message=BitcoinMessage(message), sig=signature)
    except Exception as ex:
        return False


def sign_and_verify(private_key, message, address):
    key = CBitcoinSecret(private_key)
    signature = SignMessage(key=key, message=BitcoinMessage(message))
    assert VerifyMessage(address=address, message=BitcoinMessage(message), sig=signature)
    return signature
