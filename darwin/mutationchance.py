#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Constants for mutation probability thresholds in Darwin."""

class MutationChance(object):
    """Constants for mutation probability thresholds in Darwin."""
    def __init__(self):
        pass

    def load(self, config):
        """Load."""
        if not isinstance(config, dict):
            raise Exception('config is not a dict!')

        for key in self.__dict__.keys():
            if key in config:
                self.__setattr__(key, config[key])


class BooleanMutationChance(MutationChance):
    """Mutation probability thresholds for boolean genes."""
    def __init__(self):
        super(BooleanMutationChance, self).__init__()

        self.uniform = 0.0
        self.flip = 0.0


class IntegerMutationChance(MutationChance):
    """Mutation probability thresholds for integer genes."""
    def __init__(self):
        super(IntegerMutationChance, self).__init__()

        self.uniform = 0.0
        self.boundary = 0.0
        self.gaussian = 0.0
        self.gaussian_sigma = 1.0


class FloatMutationChance(MutationChance):
    """Mutation probability thresholds for float genes."""
    def __init__(self):
        super(FloatMutationChance, self).__init__()

        self.uniform = 0.0
        self.boundary = 0.0
        self.gaussian = 0.0
        self.gaussian_sigma = 1.0


class StringMutationChance(MutationChance):
    """Mutation probability thresholds for string genes."""
    def __init__(self):
        super(StringMutationChance, self).__init__()

        self.uniform = 0.0
        self.bitstring = 0.0
        self.duplication = 0.0
        self.deletion = 0.0
        self.insertion = 0.0
        self.swap = 0.0


class ChromosomeMutationChance(MutationChance):
    """Mutation probability thresholds for chromosome-level mutations."""
    def __init__(self):
        super(ChromosomeMutationChance, self).__init__()

        self.uniform = 0.0
        self.duplication = 0.0
        self.deletion = 0.0
        self.insertion = 0.0
        self.swap = 0.0
        self.split = 0.0
        self.merge = 0.0
