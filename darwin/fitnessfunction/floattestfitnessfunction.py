#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Float test fitness function for Darwin."""

from fitnessfunction import FitnessFunction
from model.floattest import FloatTest


class FloatTestFitnessFunction(FitnessFunction):
    """Float test fitness function for Darwin."""
    def __init__(self):
        """  init  ."""
        super(FloatTestFitnessFunction, self).__init__()

    def fitness(self, model):
        """Fitness."""

        if not isinstance(model, FloatTest):
            raise Exception('model for fitness function is not a FloatTest!')

        fitness = 100 - abs(model.Single42 - 42.0)
        fitness -= abs(len(model.ZeroToNine) - 10)

        for i, value in enumerate(model.ZeroToNine[:10]):
            fitness += 10 - abs(model.ZeroToNine[i] - i)

        # perfect fitness = 200
        return fitness

