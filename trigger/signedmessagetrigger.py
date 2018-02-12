#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import simplejson
import logging
import importlib

from trigger import Trigger
from triggertype import TriggerType
from spellbookscripts.spellbookscript import SpellbookScript


class SignedMessageTrigger(Trigger):
    def __init__(self, trigger_id):
        super(SignedMessageTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.SIGNEDMESSAGE
        self.address = None
        self.message_address = None
        self.message_signature = None
        self.multi = None

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

    def configure(self, **config):
        super(SignedMessageTrigger, self).configure(**config)
        if 'multi' in config and config['multi'] in [True, False]:
            self.multi = config['multi']

        elif 'address' in config and config['address'] == '':
            self.address = None

    def json_encodable(self):
        ret = super(SignedMessageTrigger, self).json_encodable()

        ret.update({
            'address': self.address,
            'multi': self.multi})
        return ret

    def process_message(self, address, message, signature):
        if not isinstance(message, (str, unicode)):
            return

        self.message_address = address
        self.message_signature = signature

        if self.script is not None:
            if not os.path.isfile('spellbookscripts\%s.py' % self.script):
                logging.getLogger('Spellbook').error('Can not find Spellbook Script %s' % self.script)
                return
            else:
                logging.getLogger('Spellbook').info('Loading Spellbook Script spellbookscripts\%s.py' % self.script)
                try:
                    script_module = importlib.import_module('spellbookscripts.%s' % self.script)
                except Exception as ex:
                    logging.getLogger('Spellbook').error('Failed to load Spellbook Script %s: %s' % (self.script, ex))
                    return

                spellbook_script = getattr(script_module, self.script)
                script = spellbook_script(address=self.message_address, signature=self.message_signature, message=message)

                if not isinstance(script, SpellbookScript):
                    logging.getLogger('Spellbook').error('Script %s is not a valid Spellbook Script, instead it is a %s' % (self.script, type(script)))
                    return

                script.run_script()

