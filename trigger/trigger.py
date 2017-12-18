#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import logging
from datetime import datetime
from abc import abstractmethod, ABCMeta

from validators.validators import valid_description, valid_creator, valid_email, valid_youtube_id, valid_status, valid_visibility
from validators.validators import valid_address, valid_amount, valid_block_height

from jsonhelpers import save_to_json_file

TRIGGERS_DIR = 'json/public/triggers'


class Trigger(object):
    __metaclass__ = ABCMeta

    def __init__(self, trigger_id):
        self.id = trigger_id
        self.trigger_type = None
        self.block_height = None
        self.address = None
        self.amount = None
        self.confirmations = 0
        self.triggered = False
        self.description = None
        self.creator_name = None
        self.creator_email = None
        self.youtube = None
        self.status = None
        self.visibility = None
        self.created = None
        self.actions = []

    def configure(self, **config):
        self.created = datetime.fromtimestamp(config['created']) if 'created' in config else datetime.now()

        if 'trigger_type' in config and config['trigger_type'] in ['Manual', 'Balance', 'Received', 'Sent', 'Block_height']:
            self.trigger_type = config['trigger_type']

        if 'reset' in config and config['reset'] is True:
            self.triggered = False
        elif 'triggered' in config and config['triggered'] in [True, False]:
            self.triggered = config['triggered']

        if 'description' in config and valid_description(config['description']):
            self.description = config['description']

        if 'creator_name' in config and valid_creator(config['creator_name']):
            self.creator_name = config['creator_name']

        if 'creator_email' in config and valid_email(config['creator_email']):
            self.creator_email = config['creator_email']

        if 'youtube' in config and valid_youtube_id(config['youtube']):
            self.youtube = config['youtube']

        if 'status' in config and valid_status(config['status']):
            self.status = config['status']

        if 'visibility' in config and valid_visibility(config['visibility']):
            self.visibility = config['visibility']

        if 'address' in config and valid_address(config['address']):
            self.address = config['address']

        if 'amount' in config and valid_amount(config['amount']):
            self.amount = config['amount']

        if 'confirmations' in config:
            self.confirmations = config['confirmations']

        if 'block_height' in config and valid_block_height(config['block_height']):
            self.block_height = config['block_height']

    @abstractmethod
    def conditions_fulfilled(self):
        """
        Abstract method to check if the conditions of the trigger have been fulfilled.

        :return: True or False
        """
        pass

    def activate(self):
        logging.getLogger('Spellbook').info('Activating trigger %s' % self.id)
        for action in self.actions:
            print action

        self.triggered = True
        self.save()

    def save(self):
        save_to_json_file(os.path.join(TRIGGERS_DIR, '%s.json' % self.id), self.json_encodable())

    def json_encodable(self):
        return {'id': self.id,
                'trigger_type': self.trigger_type,
                'address': self.address,
                'amount': self.amount,
                'confirmations': self.confirmations,
                'block_height': self.block_height,
                'triggered': self.triggered,
                'description': self.description,
                'creator_name': self.creator_name,
                'creator_email': self.creator_email,
                'youtube': self.youtube,
                'status': self.status,
                'visibility': self.visibility,
                'created': int(time.mktime(self.created.timetuple()))}
