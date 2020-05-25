#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import abstractmethod, ABCMeta


class RosettaStone(object):
    __metaclass__ = ABCMeta

    def __init__(self, name=None, **kwargs):
        self.name = name

    def configure(self, config):
        if not isinstance(config, dict):
            raise Exception('config is not a dict!')

        for key in self.__dict__.keys():
            if key in config:
                self.__setattr__(key, config[key])

    @abstractmethod
    def genome_template(self):
        pass

    @abstractmethod
    def model_to_genome(self, model):
        pass

    @abstractmethod
    def genome_to_model(self, genome):
        pass


