#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import abstractmethod, ABCMeta


class ExplorerAPI(object):
    __metaclass__ = ABCMeta

    def __init__(self, url='', key=''):
        self.error = ''
        self.url = url
        self.key = key

    @abstractmethod
    def get_latest_block(self):
        pass

    @abstractmethod
    def get_block_by_height(self, height):
        pass

    @abstractmethod
    def get_block_by_hash(self, block_hash):
        pass

    @abstractmethod
    def get_transactions(self, address):
        pass

    @abstractmethod
    def get_balance(self, address):
        pass

    @abstractmethod
    def get_utxos(self, addresses, confirmations=3):
        pass

    @abstractmethod
    def get_prime_input_address(self, txid):
        pass

    def get_block(self, height_or_hash):
        if isinstance(height_or_hash, int):
            return self.get_block_by_height(height_or_hash)
        else:
            return self.get_block_by_hash(height_or_hash)

    def get_latest_block_height(self):
        latest_block = self.get_latest_block()
        if 'block' in latest_block and 'height' in latest_block['block']:
            return latest_block['block']['height']

