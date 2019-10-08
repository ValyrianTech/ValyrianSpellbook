#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from copy import deepcopy

from darwin.gene import BooleanGene, IntegerGene, FloatGene, StringGene
from darwin.encodingtype import EncodingType


class ChromosomeMutation(object):
    def __init__(self, chromosome):
        self.chromosome = chromosome

    def duplication(self):
        # Duplicate a random gene in a chromosome
        if self.chromosome.n_genes is None and 0 < len(self.chromosome.genes) < 1000:
            index = random.randint(0, len(self.chromosome.genes)-1)
            self.chromosome.genes.insert(index, deepcopy(self.chromosome.genes[index]))

    def deletion(self):
        # Delete a random gene in a chromosome
        if self.chromosome.n_genes is None and len(self.chromosome.genes) > 1:
            random_gene = random.choice(self.chromosome.genes)
            self.chromosome.genes.remove(random_gene)

    def insertion(self):
        # Insert a random gene in a chromosome
        if self.chromosome.n_genes is None:
            if self.chromosome.encoding_type == EncodingType.BOOLEAN:
                gene = BooleanGene()

            elif self.chromosome.encoding_type == EncodingType.INTEGER:
                gene = IntegerGene()
                if self.chromosome.min is not None:
                    gene.min = self.chromosome.min

                if self.chromosome.max is not None:
                    gene.max = self.chromosome.max

            elif self.chromosome.encoding_type == EncodingType.FLOAT:
                gene = FloatGene()
                if self.chromosome.min is not None:
                    gene.min = self.chromosome.min

                if self.chromosome.max is not None:
                    gene.max = self.chromosome.max

            elif self.chromosome.encoding_type == EncodingType.STRING:
                gene = StringGene()
                if self.chromosome.charset is not None:
                    gene.charset = self.chromosome.charset

            else:
                raise NotImplementedError('Unknown encoding type: %s' % self.chromosome.encoding_type)

            gene.set_random_data()
            self.chromosome.genes.insert(random.randint(0, len(self.chromosome.genes)), gene)

    def swap(self):
        # Swap 2 random genes in a chromosome
        n_genes = len(self.chromosome.genes)
        if n_genes >= 2:
            i = random.randint(0, n_genes-1)
            j = random.randint(0, n_genes-1)
            self.chromosome.genes[i], self.chromosome.genes[j] = self.chromosome.genes[j], self.chromosome.genes[i]

    def split(self):
        # Split a string gene in 2 genes
        if not self.chromosome.encoding_type == EncodingType.STRING:
            return

        if self.chromosome.n_genes is None and 0 < len(self.chromosome.genes) < 1000:
            i = random.randint(0, len(self.chromosome.genes)-1)
            gene = deepcopy(self.chromosome.genes[i])

            if len(gene.data) >= 2:
                j = random.randint(0, len(gene.data)-1)

                self.chromosome.genes[i].data = gene.data[:j]
                gene.data = gene.data[j:]
                self.chromosome.genes.insert(i+1, gene)

    def merge(self):
        # Merge 2 genes together
        if not self.chromosome.encoding_type == EncodingType.STRING:
            return

        n_genes = len(self.chromosome.genes)
        if n_genes >= 2:
            i = random.randint(0, len(self.chromosome.genes)-2)

            self.chromosome.genes[i].data = self.chromosome.genes[i].data + self.chromosome.genes[i+1].data
            del self.chromosome.genes[i+1]
