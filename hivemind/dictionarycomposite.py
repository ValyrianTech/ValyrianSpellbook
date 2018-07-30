#!/usr/bin/env python
# -*- coding: utf-8 -*-

from helpers.loghelpers import LOG
from compositehivemind import CompositeHivemind
from hivemind import HivemindState
from helpers.hivemindhelpers import get_hivemind_state_hash


class DictionaryComposite(CompositeHivemind):
    def get_result(self):
        ret = {}
        for component_name, (hivemind_id, question_index) in self.components.items():
            hivemind_state_hash = get_hivemind_state_hash(hivemind_id=hivemind_id)
            hivemind_state = HivemindState(multihash=hivemind_state_hash)
            value = hivemind_state.get_consensus(question_index=question_index)
            LOG.info('Dictionary composite component %s: %s' % (component_name, value))
            ret[component_name] = value

        return ret
