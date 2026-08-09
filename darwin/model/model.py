#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base model class for the Darwin evolutionary framework."""


class Model(object):
    """Base model class for Darwin."""
    def __init__(self, name=None, **kwargs):
        """  init  ."""
        self.name = name
        self.description = ''

    def configure(self, config):
        """Configure."""
        if not isinstance(config, dict):
            raise Exception('config is not a dict!')

        for key in self.__dict__.keys():
            if key in config:
                self.__setattr__(key, config[key])

    def darwin_init_actions(self):
        """Darwin init actions."""
        pass

    def champion_actions(self):
        """Champion actions."""
        pass

    def info(self):
        """Info."""
        pass

    def pre_generation_actions(self):
        """Pre generation actions."""
        print('executing pre generation actions')

    def post_generation_actions(self, champion):
        """Post generation actions."""
        print('executing post generation actions')
