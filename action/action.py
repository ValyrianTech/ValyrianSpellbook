#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from abc import abstractmethod, ABCMeta
from datetime import datetime

from helpers.jsonhelpers import save_to_json_file
from validators.validators import valid_action_type

ACTIONS_DIR = 'json/public/actions'


class Action(object):
    __metaclass__ = ABCMeta

    def __init__(self, action_id):
        self.id = action_id
        self.action_type = None
        self.created = None

    def configure(self, **config):
        self.created = datetime.fromtimestamp(config['created']) if 'created' in config else datetime.now()

        if 'action_type' in config and valid_action_type(config['action_type']):
            self.action_type = config['action_type']

    def save(self):
        save_to_json_file(os.path.join(ACTIONS_DIR, '%s.json' % self.id), self.json_encodable())

    def json_encodable(self):
        return {'id': self.id,
                'action_type': self.action_type,
                'created': int(time.mktime(self.created.timetuple()))}

    @abstractmethod
    def run(self):
        """
        Run the action

        :return: True upon success, False upon failure
        """
        pass
