#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fitnessfunction import FitnessFunction
from model.booleantest import BooleanTest


class BooleanTestFitnessFunction(FitnessFunction):
    def __init__(self):
        super(BooleanTestFitnessFunction, self).__init__()

    def fitness(self, model):

        if not isinstance(model, BooleanTest):
            raise Exception('model for fitness function is not a BooleanTest!')

        fitness = 0

        if model.SingleTrue is True:
            fitness += 100
        else:
            fitness -= 100

        if model.SingleFalse is False:
            fitness += 100
        else:
            fitness -= 100

        fitness -= abs(len(model.Fixed10True) - 10)
        fitness -= abs(len(model.Fixed10False) - 10)
        fitness -= abs(len(model.Variable10True) - 10)
        fitness -= abs(len(model.Variable10False) - 10)
        fitness -= abs(len(model.Alternating) - 10)

        for value in model.Fixed10True[:10]:
            fitness += 1 if value is True else -1

        for value in model.Fixed10False[:10]:
            fitness += 1 if value is False else -1

        for value in model.Variable10True[:10]:
            fitness += 1 if value is True else -1

        for value in model.Variable10False[:10]:
            fitness += 1 if value is False else -1

        for i, value in enumerate(model.Alternating[:10]):
            if i % 2 == 0:
                fitness += 1 if value is True else -1
            else:
                fitness += 1 if value is False else -1

        # perfect fitness = 250
        return fitness

