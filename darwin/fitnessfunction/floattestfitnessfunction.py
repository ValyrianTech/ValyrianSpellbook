#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fitnessfunction import FitnessFunction
from model.floattest import FloatTest


class FloatTestFitnessFunction(FitnessFunction):
    def __init__(self):
        super(FloatTestFitnessFunction, self).__init__()

    def fitness(self, model):

        if not isinstance(model, FloatTest):
            raise Exception('model for fitness function is not a FloatTest!')

        fitness = 100 - abs(model.Single42 - 42.0)
        fitness -= abs(len(model.ZeroToNine) - 10)

        for i, value in enumerate(model.ZeroToNine[:10]):
            fitness += 10 - abs(model.ZeroToNine[i] - i)

        # perfect fitness = 200
        return fitness

