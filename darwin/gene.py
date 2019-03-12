#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import string

from genemutation import BooleanGeneMutation, IntegerGeneMutation, FloatGeneMutation, StringGeneMutation


class Gene(object):
    def __init__(self):
        self.data = None

    def set_random_data(self):
        pass

    def info(self):
        return self.data

    def apply_mutations(self, mutation_chance, multiplier=1.0):
        pass


class BooleanGene(Gene):
    def __init__(self):
        super(BooleanGene, self).__init__()

    def set_random_data(self):
        self.data = True if random.randint(0, 1) else False

    def apply_mutations(self, mutation_chance, multiplier=1.0):
        if mutation_chance.uniform * multiplier > random.uniform(0, 100):
            BooleanGeneMutation(gene=self).uniform()

        if mutation_chance.flip * multiplier > random.uniform(0, 100):
            BooleanGeneMutation(gene=self).flip()


class IntegerGene(Gene):
    def __init__(self):
        super(IntegerGene, self).__init__()
        self.min = 0
        self.max = 100

    def set_random_data(self):
        self.data = random.randint(self.min, self.max)

    def apply_mutations(self, mutation_chance, multiplier=1.0):
        if mutation_chance.uniform * multiplier > random.uniform(0, 100):
            IntegerGeneMutation(gene=self).uniform()

        if mutation_chance.boundary * multiplier > random.uniform(0, 100):
            IntegerGeneMutation(gene=self).boundary()

        if mutation_chance.gaussian * multiplier > random.uniform(0, 100):
            IntegerGeneMutation(gene=self).gaussian(sigma=mutation_chance.gaussian_sigma)


class FloatGene(Gene):
    def __init__(self):
        super(FloatGene, self).__init__()
        self.min = 0.0
        self.max = 100.0

    def set_random_data(self):
        self.data = random.uniform(self.min, self.max)

    def apply_mutations(self, mutation_chance, multiplier=1.0):
        if mutation_chance.uniform * multiplier > random.uniform(0, 100):
            FloatGeneMutation(gene=self).uniform()

        if mutation_chance.boundary * multiplier > random.uniform(0, 100):
            FloatGeneMutation(gene=self).boundary()

        if mutation_chance.gaussian * multiplier > random.uniform(0, 100):
            FloatGeneMutation(gene=self).gaussian(sigma=mutation_chance.gaussian_sigma)


class StringGene(Gene):
    def __init__(self):
        super(StringGene, self).__init__()
        self.charset = string.ascii_letters + string.digits

    def set_random_data(self):
        self.data = ''.join(random.choice(self.charset) for _ in range(random.randint(1, 10)))

    def apply_mutations(self, mutation_chance, multiplier=1.0):
        if mutation_chance.uniform * multiplier > random.uniform(0, 100):
            StringGeneMutation(gene=self).uniform()

        if mutation_chance.bitstring * multiplier > random.uniform(0, 100):
            StringGeneMutation(gene=self).bitstring()

        if mutation_chance.duplication * multiplier > random.uniform(0, 100):
            StringGeneMutation(gene=self).duplication()

        if mutation_chance.deletion * multiplier > random.uniform(0, 100):
            StringGeneMutation(gene=self).deletion()

        if mutation_chance.insertion * multiplier > random.uniform(0, 100):
            StringGeneMutation(gene=self).insertion()

        if mutation_chance.swap * multiplier > random.uniform(0, 100):
            StringGeneMutation(gene=self).swap()
