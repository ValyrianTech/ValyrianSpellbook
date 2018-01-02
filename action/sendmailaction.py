#!/usr/bin/env python
# -*- coding: utf-8 -*-

from action import Action
from actiontype import ActionType
from mailhelpers import sendmail


class SendMailAction(Action):
    def __init__(self, action_id):
        super(SendMailAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.SENDMAIL

    def run(self):
        return sendmail(self.mail_recipients, self.mail_subject, self.mail_body_template)
