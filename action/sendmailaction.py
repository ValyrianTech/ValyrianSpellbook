#!/usr/bin/env python
# -*- coding: utf-8 -*-

from action import Action
from actiontype import ActionType
from mailhelpers import sendmail


class SendMailAction(Action):
    def __init__(self, action_id):
        super(SendMailAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.SENDMAIL
        self.mail_recipients = None
        self.mail_subject = None
        self.mail_body_template = None
        self.mail_variables = None

    def run(self):
        """
        Run the action

        :return: True upon success, False upon failure
        """
        return sendmail(recipients=self.mail_recipients, subject=self.mail_subject, body_template=self.mail_body_template, variables=self.mail_variables)

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['mail_recipients']    : An email address or multiple email addresses separated with ';'
                       - config['mail_subject']       : The subject for the email
                       - config['mail_body_template'] : The name of the template for the body of the email
        """
        super(SendMailAction, self).configure(**config)
        if 'mail_recipients' in config:
            self.mail_recipients = config['mail_recipients']

        if 'mail_subject' in config:
            self.mail_subject = config['mail_subject']

        if 'mail_body_template' in config:
            self.mail_body_template = config['mail_body_template']

        if 'mail_variables' in config and isinstance(config['mail_variables'], dict):
            self.mail_variables = config['mail_variables']

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super(SendMailAction, self).json_encodable()
        ret.update({'mail_recipients': self.mail_recipients,
                    'mail_subject': self.mail_subject,
                    'mail_body_template': self.mail_body_template,
                    'mail_variables': self.mail_variables})
        return ret
