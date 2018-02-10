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

    @abstractmethod
    def run_script(self):
        pass

    def process_message(self, message):
        if message[:7] == 'IPFS=Qm':  # Todo better ipfs hash detection
            ipfs_hash = message[5:]
            logging.getLogger('Spellbook').info('Message contains a IPFS hash: %s' % ipfs_hash)
            return self.process_ipfs_hash(ipfs_hash=ipfs_hash)
        else:
            try:
                json_data = simplejson.loads(message)
            except ValueError:
                json_data = None

            if json_data is not None:
                logging.getLogger('Spellbook').info('Message contains json data: %s' % message)
                return self.process_json_data(json_data=json_data)

            else:
                logging.getLogger('Spellbook').info('Message contains simple text: %s' % message)
                return self.process_text(message)

    def process_ipfs_hash(self, ipfs_hash):
        logging.getLogger('Spellbook').info('Retrieving IPFS object if necessary')

    def process_json_data(self, json_data):
        logging.getLogger('Spellbook').info('Processing JSON data')

    def process_text(self, text):
        logging.getLogger('Spellbook').info('Processing text data')
