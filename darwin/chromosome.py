#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from gene import Gene, BooleanGene, IntegerGene, FloatGene, StringGene
from chromosomemutation import ChromosomeMutation
from encodingtype import EncodingType


class Chromosome(object):
    def __init__(self, chromosome_id, encoding_type, n_genes=None):
        self.id = chromosome_id
        self.n_genes = n_genes
        self.genes = []
        self.encoding_type = encoding_type

        self.min = None
        self.max = None
        self.charset = None

    def add_gene(self, gene):
        if not isinstance(gene, Gene):
            raise Exception('Can not add genome to population: unexpected type: %s' % type(gene))

        self.genes.append(gene)

    def init_genes(self):
        # If a fixed number of genes is set, init that amount of genes, otherwise init a random number of genes
        if isinstance(self.n_genes, int) and self.n_genes > 0:
            number_of_genes = self.n_genes
        else:
            number_of_genes = random.randint(1, 10)

        for i in range(number_of_genes):
            if self.encoding_type == EncodingType.BOOLEAN:
                gene = BooleanGene()

            elif self.encoding_type == EncodingType.INTEGER:
                gene = IntegerGene()
                if self.min is not None:
                    gene.min = self.min

                if self.max is not None:
                    gene.max = self.max

            elif self.encoding_type == EncodingType.FLOAT:
                gene = FloatGene()
                if self.min is not None:
                    gene.min = self.min

                if self.max is not None:
                    gene.max = self.max

            elif self.encoding_type == EncodingType.STRING:
                gene = StringGene()
                if self.charset is not None:
                    gene.charset = self.charset

            else:
                raise NotImplementedError('Unknown Encoding type: %s' % self.encoding_type)

            gene.set_random_data()
            self.add_gene(gene=gene)

    def info(self):
        info = 'Encoding: %s\n' % self.encoding_type

        for i, gene in enumerate(self.genes):
            info += '\tGENE %s: %s\n' % (i, gene.info())

        return info

    def apply_mutations(self, mutation_chance, multiplier=1.0):
        if mutation_chance.duplication * multiplier > random.uniform(0, 100):
            ChromosomeMutation(chromosome=self).duplication()

        if mutation_chance.deletion * multiplier > random.uniform(0, 100):
            ChromosomeMutation(chromosome=self).deletion()

        if mutation_chance.insertion * multiplier > random.uniform(0, 100):
            ChromosomeMutation(chromosome=self).insertion()

        if mutation_chance.swap * multiplier > random.uniform(0, 100):
            ChromosomeMutation(chromosome=self).swap()

        if mutation_chance.split * multiplier > random.uniform(0, 100):
            ChromosomeMutation(chromosome=self).split()

        if mutation_chance.merge * multiplier > random.uniform(0, 100):
            ChromosomeMutation(chromosome=self).merge()

    def to_dict(self):
        return {'id': self.id,
                'n_genes': self.n_genes,
                'genes': [gene.data for gene in self.genes],
                'encoding_type': self.encoding_type,
                'min': self.min,
                'max': self.max,
                'charset': self.charset}

    def value(self):
        return self.genes[0].data

    def average(self):
        if self.encoding_type not in [EncodingType.INTEGER, EncodingType.FLOAT]:
            raise Exception('Invalid encoding type to calculate average value of genes: %s' % self.encoding_type)

        total = sum([gene.data for gene in self.genes])
        return total/len(self.genes) if len(self.genes) > 0 else None

    def lowest(self):
        if self.encoding_type not in [EncodingType.INTEGER, EncodingType.FLOAT]:
            raise Exception('Invalid encoding type to calculate lowest value of genes: %s' % self.encoding_type)

        return min([gene.data for gene in self.genes])

    def highest(self):
        if self.encoding_type not in [EncodingType.INTEGER, EncodingType.FLOAT]:
            raise Exception('Invalid encoding type to calculate highest value of genes: %s' % self.encoding_type)

        return max([gene.data for gene in self.genes])

    def concatenated(self):
        if self.encoding_type not in [EncodingType.STRING]:
            raise Exception('Invalid encoding type to concatenate values of genes: %s' % self.encoding_type)

        return ''.join([gene.data for gene in self.genes])

    def list(self):
        return [gene.data for gene in self.genes]
