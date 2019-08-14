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

    def run(self):
        """
        Run the action

        :return: True upon success, False upon failure
        """
        if self.webhook is None:
            return False

        LOG.info('executing webhook: %s' % self.webhook)
        try:
            r = requests.get(self.webhook)
        except Exception as ex:
            LOG.error('Webhook failed: %s' % ex)
            return False
        else:
            if r.status_code == 200:
                LOG.info('status code webhook: %s' % r.status_code)
                return True
            else:
                LOG.error('Webhook failed: status code webhook: %s' % r.status_code)
                return False

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['webhook']    : An url of the webhook
        """
        super(WebhookAction, self).configure(**config)
        if 'webhook' in config and valid_url(config['webhook']):
            self.webhook = config['webhook']

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super(WebhookAction, self).json_encodable()
        ret.update({'webhook': self.webhook})
        return ret
