#!/usr/bin/python
# -*- coding: utf-8 -*-


class ExplorerType(object):
    BLOCKCHAIN_INFO = 'Blockchain.info'
    BLOCKTRAIL_COM = 'Blocktrail.com'
    INSIGHT = 'Insight'
    BITCOIN_CORE = 'Bitcoin Core'
    GOCOIN = 'GoCoin'


class Explorer(object):
    def __init__(self):
        self.api_key = ''
        self.url = ''
        self.explorer_type = None
        self.priority = 0
        self.testnet = False

    def json_encodable(self):
        return {'type': self.explorer_type,
                'priority': self.priority,
                'url': self.url,
                'api_key': self.api_key,
                'testnet': self.testnet}

