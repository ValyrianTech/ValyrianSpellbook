#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from time import sleep

from helpers.loghelpers import LOG
from data.transaction import TX, TxInput, TxOutput
from data.explorer_api import ExplorerAPI


class BlockstreamAPI(ExplorerAPI):
    def __init__(self, url='', key='', testnet=False):
        super(BlockstreamAPI, self).__init__(url=url, testnet=testnet)
        # Set the url of the api depending on testnet or mainnet
        self.url = 'https://blockstream.info/testnet/api' if self.testnet is True else 'https://blockstream.info/api'

    def get_latest_block(self):
        url = self.url + '/blocks/tip/hash'
        LOG.info('GET %s' % url)
        try:
            r = requests.get(url)
            block_hash = r.text
        except Exception as ex:
            LOG.error('Unable to get latest block_hash from Blockstream.info: %s' % ex)
            return {'error': 'Unable to get latest block_hash from Blockstream.info'}

        return self.get_block_by_hash(block_hash=block_hash)

    def get_block_by_hash(self, block_hash):
        url = self.url + '/block/{hash}'.format(hash=block_hash)
        LOG.info('GET %s' % url)
        try:
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get block %s from Blockstream.info: %s' % (block_hash, ex))
            return {'error': 'Unable to get block %s from Blockstream.info' % block_hash}

        if all(key in data for key in ('height', 'id', 'timestamp', 'merkle_root', 'size')):
            block = {'height': data['height'],
                     'hash': data['id'],
                     'time': data['timestamp'],
                     'merkleroot': data['merkle_root'],
                     'size': data['size']}  # Todo weight?
            return {'block': block}
        else:
            return {'error': 'Received invalid data: %s' % data}

    def get_block_by_height(self, height):
        url = self.url + '/block-height/{height}'.format(height=height)
        LOG.info('GET %s' % url)
        try:
            r = requests.get(url)
            block_hash = r.text
        except Exception as ex:
            LOG.error('Unable to get block %s from Blockstream.info: %s' % (height, ex))
            return {'error': 'Unable to get block %s from Blockstream.info' % height}

        return self.get_block_by_hash(block_hash=block_hash)

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
