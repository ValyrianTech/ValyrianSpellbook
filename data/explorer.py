#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Base blockchain explorer abstraction with priority fallback."""

class ExplorerType(object):
    """Base blockchain explorer abstraction with priority fallback."""
    BLOCKCHAIN_INFO = 'Blockchain.info'
    BLOCKTRAIL_COM = 'Blocktrail.com'
    INSIGHT = 'Insight'
    CHAIN_SO = 'Chain.so'
    BTC_COM = 'BTC.com'
    BLOCKSTREAM = 'Blockstream.info'


class Explorer(object):
    """
    Represents a blockchain explorer configuration with API key, URL, priority, and testnet flag.
    """
    def __init__(self):
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

