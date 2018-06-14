#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from compositehivemind import CompositeHivemind
from hivemind import HivemindState
from helpers.hivemindhelpers import get_hivemind_state_hash


class DistributionComposite(CompositeHivemind):
    def get_result(self):
        if not all(key in self.components for key in ('priority', 'number_of_recipients', 'budget', 'budget_slope')):
            logging.getLogger('Spellbook').error('Distribution Composite hivemind does not contain all necessary components!')
            return

        priority_state_hash = get_hivemind_state_hash(self.components['priority'])
        number_of_recipients_state_hash = get_hivemind_state_hash(self.components['number_of_recipients'])
        budget_state_hash = get_hivemind_state_hash(self.components['budget'])
        budget_slope_state_hash = get_hivemind_state_hash(self.components['budget_slope'])

        priority_state = HivemindState(state_hash=priority_state_hash)
        number_of_recipients_state = HivemindState(state_hash=number_of_recipients_state_hash)
        budget_state = HivemindState(state_hash=budget_state_hash)
        budget_slope_state = HivemindState(state_hash=budget_slope_state_hash)

        # todo check if there is a consensus on each value
        priority = priority_state.get_consensus()
        number_of_recipients = number_of_recipients_state.get_consensus()
        budget = budget_state.get_consensus()
        budget_slope = budget_slope_state.get_consensus()

        logging.getLogger('Spellbook').info('Distribution composite hivemind %s:' % self.composite_id)
        logging.getLogger('Spellbook').info('Recipients ordered by priority: %s' % priority)
        logging.getLogger('Spellbook').info('Number of recipients: %s' % number_of_recipients)
        logging.getLogger('Spellbook').info('Recipients ordered by budget: %s' % budget)
        logging.getLogger('Spellbook').info('Budget slope: %s' % budget_slope)

        recipients = priority[:number_of_recipients]

        distribution = {}
        units = 1

        if budget is not None and budget_slope is not None:
            for recipient in reversed(budget):
                if recipient in recipients:
                    logging.getLogger('Spellbook').info('adding recipient %s with %s units' %(recipient, units))
                    distribution[recipient] = units
                    units += budget_slope

        logging.getLogger('Spellbook').info(distribution)

        return distribution
