#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Integer test fitness function for Darwin."""

from fitnessfunction import FitnessFunction
from model.integertest import IntegerTest


class IntegerTestFitnessFunction(FitnessFunction):
    """Integer test fitness function for Darwin."""
    def __init__(self):
        super(IntegerTestFitnessFunction, self).__init__()

    def fitness(self, model):
        """Fitness."""

        if not isinstance(model, IntegerTest):
            raise Exception('model for fitness function is not a IntegerTest!')

        fitness = 100 - abs(model.Single42 - 42)
        fitness -= abs(len(model.ZeroToNine) - 10)

        for i, value in enumerate(model.ZeroToNine[:10]):
            fitness += 10 - abs(model.ZeroToNine[i] - i)
            fitness += 1 if value == i else -1

        # perfect fitness = 210
        return fitness

