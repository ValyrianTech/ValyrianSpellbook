#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fitnessfunction import FitnessFunction
from model.fulltest import FullTest


class FullTestFitnessFunction(FitnessFunction):
    def __init__(self):
        super(FullTestFitnessFunction, self).__init__()

    def fitness(self, model):

        if not isinstance(model, FullTest):
            raise Exception('model for fitness function is not a FullTest!')

        boolean_fitness = 0

        if model.SingleTrue is True:
            boolean_fitness += 100
        else:
            boolean_fitness -= 100

        if model.SingleFalse is False:
            boolean_fitness += 100
        else:
            boolean_fitness -= 100

        boolean_fitness -= abs(len(model.Fixed10True) - 10)
        boolean_fitness -= abs(len(model.Fixed10False) - 10)
        boolean_fitness -= abs(len(model.Variable10True) - 10)
        boolean_fitness -= abs(len(model.Variable10False) - 10)
        boolean_fitness -= abs(len(model.Alternating) - 10)

        for value in model.Fixed10True[:10]:
            boolean_fitness += 1 if value is True else -1

        for value in model.Fixed10False[:10]:
            boolean_fitness += 1 if value is False else -1

        for value in model.Variable10True[:10]:
            boolean_fitness += 1 if value is True else -1

        for value in model.Variable10False[:10]:
            boolean_fitness += 1 if value is False else -1

        for i, value in enumerate(model.Alternating[:10]):
            if i % 2 == 0:
                boolean_fitness += 1 if value is True else -1
            else:
                boolean_fitness += 1 if value is False else -1

        # perfect fitness = 250

        integer_fitness = 100 - abs(model.Single42 - 42)
        integer_fitness -= abs(len(model.ZeroToNine) - 10)

        for i, value in enumerate(model.ZeroToNine[:10]):
            integer_fitness += 10 - abs(model.ZeroToNine[i] - i)
            integer_fitness += 1 if value == i else -1

        integer_fitness -= abs(model.Lowest42 - 42)
        integer_fitness -= abs(model.Average42 - 42)
        integer_fitness -= abs(model.Highest42 - 42)

        # perfect fitness = 210

        float_fitness = 100 - abs(model.Single42f - 42.0)
        float_fitness -= abs(len(model.ZeroToNinef) - 10)

        for i, value in enumerate(model.ZeroToNinef[:10]):
            float_fitness += 10 - abs(model.ZeroToNinef[i] - i)

        float_fitness -= abs(model.Lowest42f - 42.0)
        float_fitness -= abs(model.Average42f - 42.0)
        float_fitness -= abs(model.Highest42f - 42.0)

        # perfect fitness = 200

        string_fitness = 0
        hello_world = 'HelloWorld'
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        gattaca = 'GATTACA'

        string_fitness -= abs(len(model.HelloWorld) - len(hello_world))*100
        string_fitness -= abs(len(model.Alphabet) - len(alphabet))*100
        string_fitness -= abs(len(model.Gattaca) - len(gattaca))*100

        for i, value in enumerate(model.HelloWorld):
            if len(model.HelloWorld) <= len(hello_world):
                string_fitness += 10 if value == hello_world[i] else -10
            else:
                string_fitness -= 10

        for i, value in enumerate(model.Alphabet):
            if len(model.Alphabet) <= len(alphabet):
                string_fitness += 10 if value == alphabet[i] else -10
            else:
                string_fitness -= 10

        for i, value in enumerate(model.Gattaca):
            if len(model.Gattaca) <= len(gattaca):
                string_fitness += 10 if value == gattaca[i] else -10
            else:
                string_fitness -= 10

        # perfect fitness = 193

        return boolean_fitness + integer_fitness + float_fitness + string_fitness

