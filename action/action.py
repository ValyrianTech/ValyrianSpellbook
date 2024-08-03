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
        """
        Constructor for an Action object
        This is an abstract class of which the different action types will be derived

        :param action_id: An id for the action
        """
        self.id = action_id
        self.action_type = None
        self.created = None

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['created']     : A timestamp when the action was created
                       - config['action_type'] : The type of action ['Command', 'SpawnProcess', 'RevealSecret', 'SendMail', 'SendTransaction', 'Webhook']
        """
        self.created = datetime.fromtimestamp(config['created']) if 'created' in config else datetime.now()

        if 'action_type' in config and valid_action_type(config['action_type']):
            self.action_type = config['action_type']

    def save(self):
        """
        Save the action as a json file
        """
        print('save action to json file: %s' % os.path.join(ACTIONS_DIR, '%s.json' % self.id))
        save_to_json_file(os.path.join(ACTIONS_DIR, '%s.json' % self.id), self.json_encodable())

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        if self.created is None:
            self.created = datetime.now()

        return {'id': self.id,
                'action_type': self.action_type,
                'created': int(time.mktime(self.created.timetuple()))}

    @abstractmethod
    def run(self, **kwargs):
        """
        Run the action

        :return: True upon success, False upon failure
        """
        pass
