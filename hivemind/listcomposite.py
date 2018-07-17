#!/usr/bin/env python
# -*- coding: utf-8 -*-

from helpers.loghelpers import LOG
from compositehivemind import CompositeHivemind
from hivemind import HivemindState
from helpers.hivemindhelpers import get_hivemind_state_hash


class ListComposite(CompositeHivemind):
    def get_result(self):
        if not all(key in self.components for key in ('items', 'max_length')):
            LOG.error('List Composite hivemind does not contain all necessary components!')
            return

        # Get the items for the list
        hivemind_id, question_index = self.components['items']
        items_hivemind_state_hash = get_hivemind_state_hash(hivemind_id=hivemind_id)
        items_hivemind_state = HivemindState(state_hash=items_hivemind_state_hash)

        # consensus type should be 'Ranked'
        if items_hivemind_state.hivemind_issue.consensus_type != 'Ranked':
            raise Exception('items hivemind does not have a Ranked consensus type')

        items = items_hivemind_state.get_consensus(question_index=question_index)

        # if there is no consensus, set items to an empty list
        if items is None:
            items = []

        # Get the maximum length of the list
        hivemind_id, question_index = self.components['max_length']
        max_length_hivemind_state_hash = get_hivemind_state_hash(hivemind_id=hivemind_id)
        max_length_hivemind_state = HivemindState(state_hash=max_length_hivemind_state_hash)

        # consensus type should be 'Single' and answer type must be integer
        if max_length_hivemind_state.hivemind_issue.consensus_type != 'Single':
            raise Exception('max length hivemind does not have a Single consensus type')

        if max_length_hivemind_state.hivemind_issue.answer_type != 'Integer':
            raise Exception('max length hivemind does not have a Integer answer type')

        max_length = max_length_hivemind_state.get_consensus(question_index=question_index)

        # if max_length is None the entire list will be returned
        return items[:max_length]
