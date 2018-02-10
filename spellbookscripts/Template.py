#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging

from spellbookscript import SpellbookScript


class Template(SpellbookScript):

    def run_script(self):
        logging.getLogger('Spellbook').info('Running Spellbook Script: %s' % os.path.splitext(os.path.basename(__file__))[0])
        logging.getLogger('Spellbook').info('address: %s' % self.address)
        logging.getLogger('Spellbook').info('signature: %s' % self.signature)
        logging.getLogger('Spellbook').info('message: %s' % self.message)



