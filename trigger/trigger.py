#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import logging
from datetime import datetime
from abc import abstractmethod, ABCMeta

from validators.validators import valid_description, valid_creator, valid_email, valid_youtube_id, valid_status, valid_visibility
from validators.validators import valid_address, valid_amount, valid_block_height, valid_actions, valid_timestamp, valid_trigger_type
from action.actionhelpers import get_actions, get_action

from jsonhelpers import save_to_json_file

TRIGGERS_DIR = 'json/public/triggers'


class Trigger(object):
    __metaclass__ = ABCMeta

    def __init__(self, trigger_id):
        self.id = trigger_id
        self.trigger_type = None
        self.block_height = None
        self.timestamp = None
        self.begin_time = None
        self.end_time = None
        self.interval = None
        self.next_activation = None
        self.address = None
        self.amount = None
        self.confirmations = 0
        self.previous_trigger = None
        self.previous_trigger_status = None
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

        if 'trigger_type' in config and valid_trigger_type(config['trigger_type']):
            self.trigger_type = config['trigger_type']

        if 'status' in config and valid_status(config['status']):
            self.status = config['status']

        if 'reset' in config and config['reset'] is True:
            self.triggered = False
            self.status = 'Active'
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

        if 'visibility' in config and valid_visibility(config['visibility']):
            self.visibility = config['visibility']

        if 'address' in config and valid_address(config['address']):
            self.address = config['address']

        if 'amount' in config and valid_amount(config['amount']):
            self.amount = config['amount']

        if 'confirmations' in config:
            self.confirmations = config['confirmations']

        if 'previous_trigger' in config:
            self.previous_trigger = config['previous_trigger']

        if 'previous_trigger_status' in config and config['previous_trigger_status'] in ['Succeeded', 'Failed']:
            self.previous_trigger_status = config['previous_trigger_status']

        if 'block_height' in config and valid_block_height(config['block_height']):
            self.block_height = config['block_height']

        if 'timestamp' in config and valid_timestamp(config['timestamp']):
            self.timestamp = config['timestamp']

        if 'interval' in config and valid_amount(config['interval']):
            self.interval = config['interval']

        if 'begin_time' in config and valid_timestamp(config['begin_time']):
            self.begin_time = config['begin_time']

        if 'end_time' in config and valid_timestamp(config['end_time']):
            self.end_time = config['end_time']

        if 'next_activation' in config and valid_timestamp(config['next_activation']):
            self.next_activation = config['next_activation']
        elif self.begin_time is not None:
            self.next_activation = self.begin_time
            logging.getLogger('Spellbook').info('Setting first activation of recurring trigger %s to %s' % (self.id, datetime.fromtimestamp(self.next_activation)))

        if 'actions' in config and valid_actions(config['actions']):
            self.actions = config['actions']
            configured_actions = get_actions()
            for action_id in self.actions:
                if action_id not in configured_actions:
                    logging.getLogger('Spellbook').warning('Trigger %s contains unknown action: %s' % (self.id, action_id))

    @abstractmethod
    def conditions_fulfilled(self):
        """
        Abstract method to check if the conditions of the trigger have been fulfilled.

        :return: True or False
        """
        pass

    def activate(self):
        """
        Activate all actions on this trigger, if all actions are successful the 'triggered' status will be True
        If an action fails, the remaining actions will not be executed and the 'triggered' status remains False so another attempt can be made the next time the trigger is checked

        Important: actions of type SendTransaction should always be the last action in the list and there should only be maximum 1 SendTransaction

        :return:
        """
        logging.getLogger('Spellbook').info('Activating trigger %s' % self.id)
        configured_actions = get_actions()
        for action_id in self.actions:
            if action_id not in configured_actions:
                logging.getLogger('Spellbook').error('Unknown action id: %s' % action_id)
                return

        for i, action_id in enumerate(self.actions):
            logging.getLogger('Spellbook').info('Running action %s: %s' % (i+1, action_id))

            action = get_action(action_id)
            success = action.run()

            if not success:
                self.triggered = True
                self.status = 'Failed'
                self.save()
                return

        # All actions were successful
        self.triggered = True
        self.status = 'Succeeded'
        self.save()

    def save(self):
        save_to_json_file(os.path.join(TRIGGERS_DIR, '%s.json' % self.id), self.json_encodable())

    def json_encodable(self):
        return {'id': self.id,
                'trigger_type': self.trigger_type,
                'address': self.address,
                'amount': self.amount,
                'confirmations': self.confirmations,
                'previous_trigger': self.previous_trigger,
                'previous_trigger_status': self.previous_trigger_status,
                'block_height': self.block_height,
                'timestamp': self.timestamp,
                'begin_time': self.begin_time,
                'end_time': self.end_time,
                'interval': self.interval,
                'next_activation': self.next_activation,
                'triggered': self.triggered,
                'description': self.description,
                'creator_name': self.creator_name,
                'creator_email': self.creator_email,
                'youtube': self.youtube,
                'status': self.status,
                'visibility': self.visibility,
                'created': int(time.mktime(self.created.timetuple())),
                'actions': self.actions}
