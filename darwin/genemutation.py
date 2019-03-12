#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import numpy as np


class GeneMutation(object):
    def __init__(self, gene):
        self.gene = gene

    def uniform(self):
        # Put random data in a gene
        self.gene.set_random_data()


class BooleanGeneMutation(GeneMutation):
    def __init__(self, gene):
        super(BooleanGeneMutation, self).__init__(gene)

    def flip(self):
        self.gene.data = False if self.gene.data is True else True


class IntegerGeneMutation(GeneMutation):
    def __init__(self, gene):
        super(IntegerGeneMutation, self).__init__(gene)

    def boundary(self):
        # set value to either min or max value
        if self.gene.min is not None and self.gene.max is not None:
            self.gene.data = self.gene.min if random.randint(0, 1) == 0 else self.gene.max

    def gaussian(self, mu=0, sigma=1.0):
        # add a random value from a normal (gaussian) distribution to the existing value
        change = int(np.random.normal(mu, sigma))

        if self.gene.min is not None and self.gene.max is not None:
            if self.gene.min <= self.gene.data + change <= self.gene.max:
                self.gene.data += change
        else:
            self.gene.data += change


class FloatGeneMutation(GeneMutation):
    def __init__(self, gene):
        super(FloatGeneMutation, self).__init__(gene)

    def boundary(self):
        # set value to either min or max value
        if self.gene.min is not None and self.gene.max is not None:
            self.gene.data = self.gene.min if random.randint(0, 1) == 0 else self.gene.max

    def gaussian(self, mu=0, sigma=1.0):
        # add a random value from a normal (gaussian) distribution to the existing value
        change = np.random.normal(mu, sigma)

        if self.gene.min is not None and self.gene.max is not None:
            if self.gene.min <= self.gene.data + change <= self.gene.max:
                self.gene.data += change
        else:
            self.gene.data += change


class StringGeneMutation(GeneMutation):
    def __init__(self, gene):
        super(StringGeneMutation, self).__init__(gene)

    def bitstring(self):
        # Change a random character in the gene
        if len(self.gene.data) >= 1:
            index = random.randint(0, len(self.gene.data)-1)
            self.gene.data = self.gene.data[:index] + random.choice(self.gene.charset) + self.gene.data[index + 1:]

    def duplication(self):
        # Duplicate the gene data
        if 0 < len(self.gene.data) < 1000:  # hard limit so genes don't get to big
            self.gene.data += self.gene.data

    def deletion(self):
        # Delete a random part of the gene
        n_chars = len(self.gene.data)
        begin = random.randint(0, n_chars)
        end = random.randint(begin, n_chars)

        self.gene.data = self.gene.data[:begin] + self.gene.data[end:]

    def insertion(self):
        # Insert some random characters in the gene
        if len(self.gene.data) < 1000:
            n_characters = random.randint(1, 10)
            random_data = ''.join([random.choice(self.gene.charset) for _ in range(n_characters)])
            index = random.randint(0, len(self.gene.data)) if len(self.gene.data) >= 1 else 0

            self.gene.data = self.gene.data[:index+1] + random_data + self.gene.data[index + 1:]

    def swap(self):
        # Swap 2 random characters in the gene
        if len(self.gene.data) >= 2:
            i = random.randint(0, len(self.gene.data) - 1)
            j = random.randint(0, len(self.gene.data) - 1)

            lst = list(self.gene.data)
            lst[i], lst[j] = lst[j], lst[i]
            self.gene.data = ''.join(lst)
