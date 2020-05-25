#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Model(object):
    def __init__(self, name=None, **kwargs):
        self.name = name
        self.description = ''

    def configure(self, config):
        if not isinstance(config, dict):
            raise Exception('config is not a dict!')

        for key in self.__dict__.keys():
            if key in config:
                self.__setattr__(key, config[key])

    def darwin_init_actions(self):
        pass

    def champion_actions(self):
        pass

    def info(self):
        pass

    def pre_generation_actions(self):
        print('executing pre generation actions')

    def post_generation_actions(self, champion):
        print('executing post generation actions')
