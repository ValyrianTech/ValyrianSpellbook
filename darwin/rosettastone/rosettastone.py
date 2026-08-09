#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base Rosetta Stone class for Darwin."""

from abc import abstractmethod, ABCMeta


class RosettaStone(object):
    """Base Rosetta Stone class for Darwin."""
    __metaclass__ = ABCMeta

    def __init__(self, name=None, **kwargs):
        """  init  ."""
        self.name = name

    def configure(self, config):
        """Configure."""
        if not isinstance(config, dict):
            raise Exception('config is not a dict!')

        for key in self.__dict__.keys():
            if key in config:
                self.__setattr__(key, config[key])

    @abstractmethod
    def genome_template(self):
        """Genome template."""
        pass

    @abstractmethod
    def model_to_genome(self, model):
        """Model to genome."""
        pass

    @abstractmethod
    def genome_to_model(self, genome):
        """Genome to model."""
        pass


