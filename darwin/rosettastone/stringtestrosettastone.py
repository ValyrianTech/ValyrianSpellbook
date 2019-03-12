#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rosettastone import RosettaStone

from genome import Genome
from chromosome import Chromosome
from encodingtype import EncodingType


class StringTestRosettaStone(RosettaStone):

    def __init__(self, name=None):
        super(StringTestRosettaStone, self).__init__(name)
        

    def genome_template(self):
        """
        Get a template of the genome, all chromosomes will have empty genes

        :return:
        """
        genome = Genome()

        chromosome = Chromosome(chromosome_id='HelloWorld', encoding_type=EncodingType.STRING, n_genes=1)
        chromosome.init_genes()
        genome.add_chromosome(chromosome)

        chromosome = Chromosome(chromosome_id='Alphabet', encoding_type=EncodingType.STRING)
        chromosome.init_genes()
        genome.add_chromosome(chromosome)

        chromosome = Chromosome(chromosome_id='Gattaca', encoding_type=EncodingType.STRING, n_genes=1)
        chromosome.charset = 'GATC'
        chromosome.init_genes()
        genome.add_chromosome(chromosome)

        return genome

    def model_to_genome(self, model):
        pass

    def genome_to_model(self, genome):
        model = {'id': 'stringtest_%s' % genome.id(),
                 'name': 'stringtest',
                 'HelloWorld': genome.chromosomes[0].genes[0].data,
                 'Alphabet': ''.join([gene.data for gene in genome.chromosomes[1].genes]),
                 'Gattaca': genome.chromosomes[2].genes[0].data}

        return model

