#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging

from spellbookscript import SpellbookScript


class Template(SpellbookScript):
    def __init__(self, *args, **kwargs):
        super(Template, self).__init__(*args, **kwargs)


    def run_script(self):
        logging.getLogger('Spellbook').info('Running Spellbook Script: %s' % os.path.splitext(os.path.basename(__file__))[0])

        logging.getLogger('Spellbook').info('id: %s' % self.id)
        logging.getLogger('Spellbook').info('trigger_type: %s' % self.trigger_type)
        logging.getLogger('Spellbook').info('script: %s' % self.script)
        logging.getLogger('Spellbook').info('triggered: %s' % self.triggered)
        logging.getLogger('Spellbook').info('multi: %s' % self.multi)
        logging.getLogger('Spellbook').info('description: %s' % self.description)
        logging.getLogger('Spellbook').info('creator_name: %s' % self.creator_name)
        logging.getLogger('Spellbook').info('creator_email: %s' % self.creator_email)
        logging.getLogger('Spellbook').info('youtube: %s' % self.youtube)
        logging.getLogger('Spellbook').info('status: %s' % self.status)
        logging.getLogger('Spellbook').info('visibility: %s' % self.visibility)
        logging.getLogger('Spellbook').info('created: %s' % self.created)
        logging.getLogger('Spellbook').info('actions: %s' % self.actions)

        logging.getLogger('Spellbook').info('address: %s' % self.address)
        logging.getLogger('Spellbook').info('signature: %s' % self.signature)
        logging.getLogger('Spellbook').info('message: %s' % self.message)

        if self.json is not None:
            if 'address' not in self.json:
                logging.getLogger('Spellbook').info('Request data does not contain key: address')
                return
            if 'sentiment' not in self.json:
                logging.getLogger('Spellbook').info('Request data does not contain key: sentiment')
                return
            if 'duration' not in self.json:
                logging.getLogger('Spellbook').info('Request data does not contain key: duration')
                return

    def cleanup(self):
        pass



