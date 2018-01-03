#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from abc import abstractmethod, ABCMeta
from datetime import datetime

from jsonhelpers import save_to_json_file
from validators.validators import valid_action_type, valid_address, valid_percentage

ACTIONS_DIR = 'json/public/actions'


class Action(object):
    __metaclass__ = ABCMeta

    def __init__(self, action_id):
        self.id = action_id
        self.action_type = None
        self.created = None
        self.run_command = None
        self.mail_recipients = None
        self.mail_subject = None
        self.mail_body_template = None
        self.webhook = None
        self.reveal_text = None
        self.reveal_link = None
        self.allow_reveal = False
        self.fee_address = None
        self.fee_percentage = 0

    def configure(self, **config):
        self.created = datetime.fromtimestamp(config['created']) if 'created' in config else datetime.now()

        if 'action_type' in config and valid_action_type(config['action_type']):
            self.action_type = config['action_type']

        if 'run_command' in config:
            self.run_command = config['run_command']

        if 'mail_recipients' in config:
            self.mail_recipients = config['mail_recipients']

        if 'mail_subject' in config:
            self.mail_subject = config['mail_subject']

        if 'mail_body_template' in config:
            self.mail_body_template = config['mail_body_template']

        if 'webhook' in config:
            self.webhook = config['webhook']

        if 'reveal_text' in config:
            self.reveal_text = config['reveal_text']

        if 'reveal_link' in config:
            self.reveal_link = config['reveal_link']

        if 'allow_reveal' in config:
            self.allow_reveal = config['allow_reveal']

        if 'fee_address' in config and valid_address(config['fee_address']):
            self.fee_address = config['fee_address']

        if 'fee_percentage' in config and valid_percentage(config['fee_percentage']):
            self.fee_percentage = config['fee_percentage']

    def save(self):
        save_to_json_file(os.path.join(ACTIONS_DIR, '%s.json' % self.id), self.json_encodable())

    def json_encodable(self):
        return {'id': self.id,
                'action_type': self.action_type,
                'created': int(time.mktime(self.created.timetuple())),
                'run_command': self.run_command,
                'mail_recipients': self.mail_recipients,
                'mail_subject': self.mail_subject,
                'mail_body_template': self.mail_body_template,
                'webhook': self.webhook,
                'reveal_text': self.reveal_text,
                'reveal_link': self.reveal_link,
                'allow_reveal': self.allow_reveal,
                'fee_address': self.fee_address,
                'fee_percentage': self.fee_percentage}

    @abstractmethod
    def run(self):
        """
        Run the action

        :return: True upon success, False upon failure
        """
        pass
