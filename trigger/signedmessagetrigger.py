#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import importlib

from .trigger import Trigger
from .triggertype import TriggerType
from spellbookscripts.spellbookscript import SpellbookScript
from validators.validators import valid_address


class SignedMessageTrigger(Trigger):
    def __init__(self, trigger_id):
        super(SignedMessageTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.SIGNEDMESSAGE
        self.address = None
        self.message = None
        self.message_address = None
        self.message_signature = None

    def conditions_fulfilled(self):
        # SignedMessage triggers can only be triggered when a verified signed message is received, so always return False
        return False

    def configure(self, **config):
        super(SignedMessageTrigger, self).configure(**config)
        if 'address' in config and valid_address(config['address']):
            self.address = config['address']
        elif 'address' in config and config['address'] == '':
            self.address = None

    def json_encodable(self):
        ret = super(SignedMessageTrigger, self).json_encodable()
        ret.update({'address': self.address})
        return ret

    def get_script_variables(self):
        ret = super(SignedMessageTrigger, self).json_encodable()
        ret.update({'message': self.message,
                    'address': self.message_address,
                    'signature': self.message_signature})
        return ret

    def process_message(self, address, message, signature):
        if not isinstance(message, (str, unicode)):
            return

        self.message = message
        self.message_address = address
        self.message_signature = signature

