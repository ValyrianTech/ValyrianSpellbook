#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .compositehivemind import CompositeHivemind
from .hivemind import HivemindState
from helpers.hivemindhelpers import get_hivemind_state_hash
from helpers.loghelpers import LOG


class DistributionComposite(CompositeHivemind):
    def get_result(self):
        if not all(key in self.components for key in ('priority', 'number_of_recipients', 'budget', 'budget_slope')):
            LOG.error('Distribution Composite hivemind does not contain all necessary components!')
            return

        priority_state_hash = get_hivemind_state_hash(self.components['priority'][0])
        number_of_recipients_state_hash = get_hivemind_state_hash(self.components['number_of_recipients'][0])
        budget_state_hash = get_hivemind_state_hash(self.components['budget'][0])
        budget_slope_state_hash = get_hivemind_state_hash(self.components['budget_slope'][0])

        priority_state = HivemindState(multihash=priority_state_hash)
        number_of_recipients_state = HivemindState(multihash=number_of_recipients_state_hash)
        budget_state = HivemindState(multihash=budget_state_hash)
        budget_slope_state = HivemindState(multihash=budget_slope_state_hash)

        # todo check if there is a consensus on each value
        priority = priority_state.get_consensus(question_index=self.components['priority'][1])
        number_of_recipients = number_of_recipients_state.get_consensus(question_index=self.components['number_of_recipients'][1])
        budget = budget_state.get_consensus(question_index=self.components['budget'][1])
        budget_slope = budget_slope_state.get_consensus(question_index=self.components['budget_slope'][1])

        LOG.info('Distribution composite hivemind %s:' % self.composite_id)
        LOG.info('Recipients ordered by priority: %s' % priority)
        LOG.info('Number of recipients: %s' % number_of_recipients)
        LOG.info('Recipients ordered by budget: %s' % budget)
        LOG.info('Budget slope: %s' % budget_slope)

        recipients = priority[:number_of_recipients] if number_of_recipients is not None else []

        distribution = {}
        units = 1

        if budget is not None and budget_slope is not None:
            for recipient in reversed(budget):
                if recipient in recipients:
                    LOG.info('adding recipient %s with %s units' %(recipient, units))
                    distribution[recipient] = units
                    units += budget_slope

        LOG.info(distribution)

        return distribution
