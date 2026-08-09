#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base fitness function class for Darwin."""

from abc import abstractmethod, ABCMeta


class FitnessFunction(object):
    """Base fitness function class for Darwin."""
    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        """  init  ."""
        self.results_file = None

    @abstractmethod
    def fitness(self, model):
        """Fitness."""
        pass

    def log_results(self, filename):
        """Log results."""
        self.results_file = filename

    def darwin_init_actions(self):
        """Darwin init actions."""
        pass


class Fitness(object):
    """Holds a fitness value and associated data for a genome."""
    def __init__(self, value, data):
        """  init  ."""
        self.value = value
        self.data = data
