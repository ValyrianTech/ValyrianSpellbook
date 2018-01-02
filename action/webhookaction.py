#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import logging

from action import Action
from actiontype import ActionType


class WebhookAction(Action):
    def __init__(self, action_id):
        super(WebhookAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.WEBHOOK

    def run(self):
        if self.webhook is None:
            return False

        logging.getLogger('Spellbook').info('executing webhook: %s' % self.webhook)
        r = requests.get(self.webhook)

        if r.status_code == 200:
            logging.getLogger('Spellbook').info('status code webhook: %s' % r.status_code)
            return True
        else:
            logging.getLogger('Spellbook').error('Webhook failed: status code webhook: %s' % r.status_code)
            return False
