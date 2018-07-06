#!/usr/bin/env python
# -*- coding: utf-8 -*-


class CompositeHivemind(object):
    def __init__(self, composite_id):
        self.composite_id = composite_id
        self.components = {}

    def add_component(self, component_name, hivemind_id):
        question_index = 0
        if ':' in hivemind_id:
            hivemind_id, question_index = hivemind_id.split(':')
            question_index = int(question_index)

        self.components[component_name] = (hivemind_id, question_index)

    def get_result(self):
        pass
