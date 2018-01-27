#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from action import Action
from actiontype import ActionType


class RevealSecretAction(Action):
    def __init__(self, action_id):
        super(RevealSecretAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.REVEALSECRET

    def run(self):
        logging.getLogger('Spellbook').info('Allowing reveal of RevealSecret action %s' % self.id)
        self.allow_reveal = True
        self.save()
        return True
