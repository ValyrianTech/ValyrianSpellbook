#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from time import sleep

from helpers.txhelpers import push_tx
from helpers.loghelpers import LOG
from data.transaction import TX, TxInput, TxOutput
from data.explorer_api import ExplorerAPI


class BlockstreamAPI(ExplorerAPI):
    def __init__(self, url='', key='', testnet=False):
        super(BlockstreamAPI, self).__init__(url=url, testnet=testnet)
        # Set the url of the api depending on testnet or mainnet
        self.url = 'https://blockstream.info/testnet' if self.testnet is True else 'https://blockstream.info'

    def get_latest_block(self):
        pass

    def get_block_by_hash(self, block_hash):
        pass

    def get_block_by_height(self, height):
        pass

    def get_transactions(self, address):
        pass

    def get_balance(self, address):
        pass

    def get_transaction(self, txid):
        pass

    def get_prime_input_address(self, txid):
        pass

    def get_utxos(self, address, confirmations=3):
        pass

    @staticmethod
    def push_tx(tx):
        pass
