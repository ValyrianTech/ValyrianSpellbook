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
        self.script = None
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

        if 'trigger_type' in config and valid_trigger_type(config['trigger_type']):
            self.trigger_type = config['trigger_type']

        if 'script' in config:
            self.script = config['script']

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

        if 'confirmations' in config:
            self.confirmations = config['confirmations']

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
                'script': self.script,
                'confirmations': self.confirmations,
                'triggered': self.triggered,
                'description': self.description,
                'creator_name': self.creator_name,
                'creator_email': self.creator_email,
                'youtube': self.youtube,
                'status': self.status,
                'visibility': self.visibility,
                'created': int(time.mktime(self.created.timetuple())),
                'actions': self.actions}
