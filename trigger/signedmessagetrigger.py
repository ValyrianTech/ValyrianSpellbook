#!/usr/bin/env python
# -*- coding: utf-8 -*-
import simplejson
import logging

from trigger import Trigger
from triggertype import TriggerType


class SignedMessageTrigger(Trigger):
    def __init__(self, trigger_id):
        super(SignedMessageTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.SIGNEDMESSAGE
        self.message_address = None
        self.message_signature = None

    def conditions_fulfilled(self):
        # SignedMessage triggers can only be triggered when a verified signed message is received, so always return False
        return False

    def activate(self):
        super(SignedMessageTrigger, self).activate()

        # SignedMessage triggers must always be ready to receive a new signed message if multi is True
        # If multi is False then the trigger can only be activated once
        if self.multi is True and self.triggered is True:
            self.triggered = False
            self.save()

    def process_message(self, address, message, signature):
        if not isinstance(message, (str, unicode)):
            return

        self.message_address = address
        self.message_signature = signature

        if message[:7] == 'IPFS=Qm':  # Todo better ipfs hash detection
            ipfs_hash = message[5:]
            logging.getLogger('Spellbook').info('Message contains a IPFS hash: %s' % ipfs_hash)
            return self.process_ipfs_hash(ipfs_hash=ipfs_hash)
        else:
            try:
                json_data = simplejson.loads(message)
            except ValueError:
                json_data = None

            if json_data is not None:
                logging.getLogger('Spellbook').info('Message contains json data: %s' % message)
                return self.process_json_data(json_data=json_data)

            else:
                logging.getLogger('Spellbook').info('Message contains simple text: %s' % message)
                return self.process_text(message)

    def process_ipfs_hash(self, ipfs_hash):
        pass

    def process_json_data(self, json_data):
        pass

    def process_text(self, text):
        pass

