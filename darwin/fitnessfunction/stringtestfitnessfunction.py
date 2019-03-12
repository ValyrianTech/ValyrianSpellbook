#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fitnessfunction import FitnessFunction
from model.stringtest import StringTest


class StringTestFitnessFunction(FitnessFunction):
    def __init__(self):
        super(StringTestFitnessFunction, self).__init__()

    def fitness(self, model):

        if not isinstance(model, StringTest):
            raise Exception('model for fitness function is not a StringTest!')

        fitness = 0
        hello_world = 'HelloWorld'
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        gattaca = 'GATTACA'

        fitness += 50 - abs(len(model.HelloWorld) - len(hello_world))
        fitness += 50 - abs(len(model.Alphabet) - len(alphabet))
        fitness += 50 - abs(len(model.Gattaca) - len(gattaca))

        for i, value in enumerate(model.HelloWorld):
            if len(model.HelloWorld) <= len(hello_world):
                fitness += 1 if value == hello_world[i] else -1
            else:
                fitness -= 1

        for i, value in enumerate(model.Alphabet):
            if len(model.Alphabet) <= len(alphabet):
                fitness += 1 if value == alphabet[i] else -1
            else:
                fitness -= 1

        for i, value in enumerate(model.Gattaca):
            if len(model.Gattaca) <= len(gattaca):
                fitness += 1 if value == gattaca[i] else -1
            else:
                fitness -= 1

        # perfect fitness = 193
        return fitness

