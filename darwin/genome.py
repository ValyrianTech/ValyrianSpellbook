#!/usr/bin/env python
# -*- coding: utf-8 -*-

from chromosome import Chromosome

import hashlib
import binascii
import simplejson


class Genome(object):
    def __init__(self):
        self.chromosomes = {}
        self.fitness = None

    # def add_chromosome(self, chromosome):
    #     if not isinstance(chromosome, Chromosome):
    #         raise Exception('Can not add genome to population: unexpected type: %s' % type(chromosome))
    #
    #     self.chromosomes.append(chromosome)

    def add_chromosome(self, chromosome_id, encoding_type, min_value=None, max_value=None, charset=None, n_genes=None):
        chromosome = Chromosome(chromosome_id=chromosome_id, encoding_type=encoding_type, n_genes=n_genes)

        if min_value is not None:
            chromosome.min = min_value

        if max_value is not None:
            chromosome.max = max_value

        if charset is not None:
            chromosome.charset = charset

        chromosome.init_genes()

        self.chromosomes[chromosome_id] = chromosome

    def init_with_random_data(self):
        for chromosome_id, chromosome in self.chromosomes.items():
            for gene in chromosome.genes:
                gene.set_random_data()

    def info(self):
        info = 'Genome id: %s' % self.id()

        for chromosome_id, chromosome in self.chromosomes.items():
            info += '\nCHROMOSOME %s:\n%s' % (chromosome_id, chromosome.info())

        return info

    def id(self):
        data_string = ''
        for i, (chromosome_id, chromosome) in enumerate(self.chromosomes.items()):
            data_string += '|%s|' % i
            for j, gene in enumerate(chromosome.genes):
                data_string += '%s:%s ' % (j, gene.data)

        return binascii.hexlify(hashlib.sha256(simplejson.dumps(data_string, sort_keys=True)).digest())

    def to_dict(self):
        return {'chromosomes': {chromosome_id: chromosome.to_dict() for chromosome_id, chromosome in self.chromosomes.items()},
                'fitness': self.fitness,
                'id': self.id()}
