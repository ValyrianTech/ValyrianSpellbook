#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from abc import abstractmethod, ABCMeta
from datetime import datetime

from jsonhelpers import save_to_json_file
from validators.validators import valid_action_type

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

    def save(self):
        save_to_json_file(os.path.join(ACTIONS_DIR, '%s.json' % self.id), self.json_encodable())

    def json_encodable(self):
        return {'id': self.id,
                'action_type': self.action_type,
                'created': int(time.mktime(self.created.timetuple())),
                'run_command': self.run_command,
                'mail_recipients': self.mail_recipients,
                'mail_subject': self.mail_subject,
                'mail_body_template': self.mail_body_template}

    @abstractmethod
    def run(self):
        """
        Run the action

        :return: True upon success, False upon failure
        """
        pass
