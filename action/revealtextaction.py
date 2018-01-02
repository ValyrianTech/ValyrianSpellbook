#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from action import Action
from actiontype import ActionType


class RevealTextAction(Action):
    def __init__(self, action_id):
        super(RevealTextAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.REVEALTEXT

    def run(self):
        logging.getLogger('Spellbook').info('Allowing reveal of RevealText action %s' % self.id)
        self.allow_reveal = True
        self.save()
        return True

