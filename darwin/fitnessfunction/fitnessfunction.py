#!/usr/bin/env python
"""Base fitness function class for Darwin."""

from abc import ABCMeta, abstractmethod


class FitnessFunction:
    """Base fitness function class for Darwin."""
    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        self.results_file = None

    @abstractmethod
    def fitness(self, model):
        """Fitness."""

    def log_results(self, filename):
        """Log results."""
        self.results_file = filename

    def darwin_init_actions(self):
        """Darwin init actions."""


class Fitness:
    """Holds a fitness value and associated data for a genome."""
    def __init__(self, value, data):
        self.value = value
        self.data = data
