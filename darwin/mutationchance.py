#!/usr/bin/env python
# -*- coding: utf-8 -*-


class MutationChance(object):
    def __init__(self):
        pass

    def load(self, config):
        if not isinstance(config, dict):
            raise Exception('config is not a dict!')

        for key in self.__dict__.keys():
            if key in config:
                self.__setattr__(key, config[key])


class BooleanMutationChance(MutationChance):
    def __init__(self):
        super(BooleanMutationChance, self).__init__()

        self.uniform = 0.0
        self.flip = 0.0


class IntegerMutationChance(MutationChance):
    def __init__(self):
        super(IntegerMutationChance, self).__init__()

        self.uniform = 0.0
        self.boundary = 0.0
        self.gaussian = 0.0
        self.gaussian_sigma = 1.0


class FloatMutationChance(MutationChance):
    def __init__(self):
        super(FloatMutationChance, self).__init__()

        self.uniform = 0.0
        self.boundary = 0.0
        self.gaussian = 0.0
        self.gaussian_sigma = 1.0


class StringMutationChance(MutationChance):
    def __init__(self):
        super(StringMutationChance, self).__init__()

        self.uniform = 0.0
        self.bitstring = 0.0
        self.duplication = 0.0
        self.deletion = 0.0
        self.insertion = 0.0
        self.swap = 0.0


class ChromosomeMutationChance(MutationChance):
    def __init__(self):
        super(ChromosomeMutationChance, self).__init__()

        self.uniform = 0.0
        self.duplication = 0.0
        self.deletion = 0.0
        self.insertion = 0.0
        self.swap = 0.0
        self.split = 0.0
        self.merge = 0.0
