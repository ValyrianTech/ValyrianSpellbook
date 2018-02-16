#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from action import Action
from actiontype import ActionType


class RevealSecretAction(Action):
    def __init__(self, action_id):
        super(RevealSecretAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.REVEALSECRET
        self.reveal_text = None
        self.reveal_link = None
        self.allow_reveal = False

    def run(self):
        """
        Run the action

        :return: True upon success, False upon failure
        """
        logging.getLogger('Spellbook').info('Allowing reveal of RevealSecret action %s' % self.id)
        self.allow_reveal = True
        self.save()
        return True

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['reveal_text']  : A secret text
                       - config['reveal_link']  : A secret link
                       - config['allow_reveal'] : Is the secret allowed to be revealed?
        """
        super(RevealSecretAction, self).configure(**config)
        if 'reveal_text' in config:
            self.reveal_text = config['reveal_text']

        if 'reveal_link' in config:
            self.reveal_link = config['reveal_link']

        if 'allow_reveal' in config:
            self.allow_reveal = config['allow_reveal']

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super(RevealSecretAction, self).json_encodable()
        ret.update({'reveal_text': self.reveal_text,
                    'reveal_link': self.reveal_link,
                    'allow_reveal': self.allow_reveal})
        return ret
