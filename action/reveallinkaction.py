#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from action import Action
from actiontype import ActionType


class RevealLinkAction(Action):
    def __init__(self, action_id):
        super(RevealLinkAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.REVEALLINK

    def run(self):
        logging.getLogger('Spellbook').info('Allowing reveal of RevealLink action %s' % self.id)
        self.allow_reveal = True
        self.save()
        return True
