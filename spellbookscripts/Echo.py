#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from .spellbookscript import SpellbookScript
from helpers.loghelpers import LOG


class Echo(SpellbookScript):
    def __init__(self, *args, **kwargs):
        super(Echo, self).__init__(*args, **kwargs)

    def run(self):
        LOG.info('Running Spellbook Script: %s' % os.path.splitext(os.path.basename(__file__))[0])

        LOG.info('id: %s' % self.trigger_id)
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
        LOG.info('data: %s' % self.data)

        if self.data is not None:
            LOG.info('Sending echo: %s' % self.data)

            # just echo the json data if there is any
            self.http_response = self.data

    def cleanup(self):
        pass



