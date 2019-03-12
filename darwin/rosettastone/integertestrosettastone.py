#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rosettastone import RosettaStone

from genome import Genome
from chromosome import Chromosome
from encodingtype import EncodingType


class IntegerTestRosettaStone(RosettaStone):

    def __init__(self, name=None):
        super(IntegerTestRosettaStone, self).__init__(name)
        

    def genome_template(self):
        """
        Get a template of the genome, all chromosomes will have empty genes

        :return:
        """
        genome = Genome()

        chromosome = Chromosome(chromosome_id='Single42', encoding_type=EncodingType.INTEGER, n_genes=1)
        chromosome.init_genes()
        genome.add_chromosome(chromosome)

        chromosome = Chromosome(chromosome_id='ZeroToNine', encoding_type=EncodingType.INTEGER)
        chromosome.init_genes()
        genome.add_chromosome(chromosome)

        return genome

    def model_to_genome(self, model):
        pass

    def genome_to_model(self, genome):
        model = {'id': 'integertest_%s' % genome.id(),
                 'name': 'integertest',
                 'Single42': genome.chromosomes[0].genes[0].data,
                 'ZeroToNine': [gene.data for gene in genome.chromosomes[1].genes]}

        return model

