#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import simplejson

from abc import abstractmethod, ABCMeta
from validators.validators import valid_address


class SpellbookScript(object):
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        self.address = kwargs['address'] if 'address' in kwargs else None
        if self.address is not None and not valid_address(self.address):
            raise Exception('%s is not a valid address!' % self.address)

        self.message = kwargs['message'] if 'message' in kwargs else None
        self.signature = kwargs['signature'] if 'signature' in kwargs else None

        self.id = kwargs['id'] if 'id' in kwargs else None
        self.trigger_type = kwargs['trigger_type'] if 'trigger_type' in kwargs else None
        self.script = kwargs['script'] if 'script' in kwargs else None
        self.triggered = kwargs['triggered'] if 'triggered' in kwargs else None
        self.multi = kwargs['multi'] if 'multi' in kwargs else None
        self.description = kwargs['description'] if 'description' in kwargs else None
        self.creator_name = kwargs['creator_name'] if 'creator_name' in kwargs else None
        self.creator_email = kwargs['creator_email'] if 'creator_email' in kwargs else None
        self.youtube = kwargs['youtube'] if 'youtube' in kwargs else None
        self.status = kwargs['status'] if 'status' in kwargs else None
        self.visibility = kwargs['visibility'] if 'visibility' in kwargs else None
        self.created = kwargs['created'] if 'created' in kwargs else None
        self.actions = kwargs['actions'] if 'actions' in kwargs else None

        self.json = None
        self.ipfs = None
        self.text = None

    @abstractmethod
    def run_script(self):
        pass

    @abstractmethod
    def cleanup(self):
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
