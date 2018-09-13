#!/usr/bin/env python
# -*- coding: utf-8 -*-


class ExplorerType(object):
    BLOCKCHAIN_INFO = 'Blockchain.info'
    BLOCKTRAIL_COM = 'Blocktrail.com'
    INSIGHT = 'Insight'
    CHAIN_SO = 'Chain.so'
    BTC_COM = 'BTC.com'


class Explorer(object):
    def __init__(self):
        """
        Constructor of the Explorer object
        """
        self.api_key = ''
        self.url = ''
        self.explorer_type = None
        self.priority = 0
        self.testnet = False

    def json_encodable(self):
        """
        Get the explorer configuration

        :return: A dict containing info about the explorer
        """
        return {'type': self.explorer_type,
                'priority': self.priority,
                'url': self.url,
                'api_key': self.api_key,
                'testnet': self.testnet}

