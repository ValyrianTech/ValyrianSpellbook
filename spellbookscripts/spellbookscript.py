#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import simplejson

from abc import abstractmethod, ABCMeta
from validators.validators import valid_address


class SpellbookScript(object):
    __metaclass__ = ABCMeta

    def __init__(self, address, message, signature):
        self.address = address
        self.message = message
        self.signature = signature

        if not valid_address(self.address):
            raise Exception('%s is not a valid address!' % self.address)

        self.json = None
        self.ipfs = None
        self.text = None

        self.process_message()

    @abstractmethod
    def run_script(self):
        pass

    def process_message(self):
        if self.message[:7] == 'IPFS=Qm':  # Todo better ipfs hash detection
            ipfs_hash = self.message[5:]
            logging.getLogger('Spellbook').info('Message contains a IPFS hash: %s' % ipfs_hash)
            return self.process_ipfs_hash(ipfs_hash=ipfs_hash)
        else:
            try:
                json_data = simplejson.loads(self.message)
            except ValueError:
                json_data = None

            if json_data is not None:
                logging.getLogger('Spellbook').info('Message contains json data: %s' % self.message)
                return self.process_json_data(json_data=json_data)

            else:
                logging.getLogger('Spellbook').info('Message contains simple text: %s' % self.message)
                return self.process_text(self.message)

    def process_ipfs_hash(self, ipfs_hash):
        logging.getLogger('Spellbook').info('Retrieving IPFS object if necessary')
        self.ipfs = ipfs_hash

    def process_json_data(self, json_data):
        logging.getLogger('Spellbook').info('Processing JSON data')
        self.json = json_data

    def process_text(self, text):
        logging.getLogger('Spellbook').info('Processing text data')
        self.text = text
