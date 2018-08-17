#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import abstractmethod, ABCMeta


class ExplorerAPI(object):
    __metaclass__ = ABCMeta

    def __init__(self, url='', key='', testnet=False):
        """
        Constructor of the abstract class ExplorerAPI

        :param url: The url of the explorer
        :param key: An api key for the explorer
        :param testnet: True if testnet, default False (mainnet)
        """
        self.error = ''
        self.url = url
        self.key = key
        self.testnet = testnet

    @abstractmethod
    def get_latest_block(self):
        """
        Get the latest block
        """
        pass

    @abstractmethod
    def get_block_by_height(self, height):
        """
        Get a block by a block height

        :param height: The height of the block
        """
        pass

    @abstractmethod
    def get_block_by_hash(self, block_hash):
        """
        Get a block by a block hash

        :param block_hash: The block hash
        """
        pass

    @abstractmethod
    def get_transactions(self, address):
        """
        Get the transactions of an address

        :param address: The address
        """
        pass

    @abstractmethod
    def get_balance(self, address):
        """
        Get the balance of an address

        :param address: The address
        """
        pass

    @abstractmethod
    def get_utxos(self, address, confirmations=3):
        """
        Get the UTXOs of an address with at least x confirmations

        :param address: The address
        :param confirmations: The minimum number of confirmations
        """
        pass

    @abstractmethod
    def get_transaction(self, txid):
        """
        Get a transaction by its txid

        :param txid: The transaction id
        """
        pass

    @abstractmethod
    def get_prime_input_address(self, txid):
        """
        Get the prime input address of a transaction

        :param txid: The transaction id
        """
        pass

    def get_block(self, height_or_hash):
        """
        Get a block by a block height or a block hash

        :param height_or_hash: A block height OR a block hash
        :return: a dict containing info about the block
        """
        if isinstance(height_or_hash, int):
            return self.get_block_by_height(height_or_hash)
        else:
            return self.get_block_by_hash(height_or_hash)

    def get_latest_block_height(self):
        """
        Get the latest block height

        :return: The latest block height
        """
        latest_block = self.get_latest_block()
        if 'block' in latest_block and 'height' in latest_block['block']:
            return latest_block['block']['height']

