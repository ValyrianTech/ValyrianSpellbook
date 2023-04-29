#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

from helpers.loghelpers import LOG
from .action import Action
from .actiontype import ActionType
from validators.validators import valid_url


class WebhookAction(Action):
    def __init__(self, action_id):
        super(WebhookAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.WEBHOOK
        self.webhook = None
        self.body = None
        self.request_type = 'GET'

    def run(self):
        """
        Run the action

        :return: True upon success, False upon failure
        """
        if self.webhook is None:
            return False

        LOG.info('executing webhook: %s' % self.webhook)
        try:
            if self.request_type == 'GET':
                r = requests.get(self.webhook)
            elif self.request_type == 'POST':
                r = requests.post(self.webhook, data=self.body)
            else:
                LOG.error('Webhook failed: unsupported request type: %s' % self.request_type)
                return False

        except Exception as ex:
            LOG.error('Webhook failed: %s' % ex)
            return False
        else:
            if r.status_code == 200:
                LOG.info('status code webhook: %s' % r.status_code)
                return True, r.text
            else:
                LOG.error('Webhook failed: status code webhook: %s' % r.status_code)
                return False, r.text

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['webhook']    : An url of the webhook
        """
        super(WebhookAction, self).configure(**config)
        if 'webhook' in config and valid_url(config['webhook']):
            self.webhook = config['webhook']

        self.body = config.get('body', None)
        self.request_type = config.get('request_type', 'GET')

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super(WebhookAction, self).json_encodable()
        ret.update({'webhook': self.webhook,
                    'body': self.body,
                    'request_type': self.request_type})
        return ret
