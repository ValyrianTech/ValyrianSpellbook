#!/usr/bin/env python
# -*- coding: utf-8 -*-


class CompositeHivemind(object):
    def __init__(self, composite_id):
        self.composite_id = composite_id
        self.components = {}

    def add_component(self, component_name, hivemind_id):
        self.components[component_name] = hivemind_id

    def get_result(self):
        pass
