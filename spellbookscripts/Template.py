#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from helpers.loghelpers import LOG
from spellbookscript import SpellbookScript


class Template(SpellbookScript):
    def __init__(self, *args, **kwargs):
        super(Template, self).__init__(*args, **kwargs)

    def run(self):
        LOG.info('Running Spellbook Script: %s' % os.path.splitext(os.path.basename(__file__))[0])

        LOG.info('id: %s' % self.id)
        LOG.info('trigger_type: %s' % self.trigger_type)
        LOG.info('script: %s' % self.script)
        LOG.info('triggered: %s' % self.triggered)
        LOG.info('multi: %s' % self.multi)
        LOG.info('description: %s' % self.description)
        LOG.info('creator_name: %s' % self.creator_name)
        LOG.info('creator_email: %s' % self.creator_email)
        LOG.info('youtube: %s' % self.youtube)
        LOG.info('status: %s' % self.status)
        LOG.info('visibility: %s' % self.visibility)
        LOG.info('created: %s' % self.created)
        LOG.info('actions: %s' % self.actions)

        LOG.info('address: %s' % self.address)
        LOG.info('signature: %s' % self.signature)
        LOG.info('message: %s' % self.message)

        if self.json is not None:
            if 'address' not in self.json:
                LOG.info('Request data does not contain key: address')
                return
            if 'sentiment' not in self.json:
                LOG.info('Request data does not contain key: sentiment')
                return
            if 'duration' not in self.json:
                LOG.info('Request data does not contain key: duration')
                return

    def cleanup(self):
        pass



