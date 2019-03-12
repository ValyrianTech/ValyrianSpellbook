#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rosettastone import RosettaStone

from genome import Genome
from chromosome import Chromosome
from encodingtype import EncodingType


class BooleanTestRosettaStone(RosettaStone):

    def __init__(self, name=None):
        super(BooleanTestRosettaStone, self).__init__(name)
        

    def genome_template(self):
        """
        Get a template of the genome, all chromosomes will have empty genes

        :return:
        """
        genome = Genome()

        chromosome = Chromosome(chromosome_id='SingleTrue', encoding_type=EncodingType.BOOLEAN, n_genes=1)
        chromosome.init_genes()
        genome.add_chromosome(chromosome)

        chromosome = Chromosome(chromosome_id='SingleFalse', encoding_type=EncodingType.BOOLEAN, n_genes=1)
        chromosome.init_genes()
        genome.add_chromosome(chromosome)

        chromosome = Chromosome(chromosome_id='Fixed10True', encoding_type=EncodingType.BOOLEAN, n_genes=10)
        chromosome.init_genes()
        genome.add_chromosome(chromosome)

        chromosome = Chromosome(chromosome_id='Fixed10False', encoding_type=EncodingType.BOOLEAN, n_genes=10)
        chromosome.init_genes()
        genome.add_chromosome(chromosome)

        chromosome = Chromosome(chromosome_id='Variable10True', encoding_type=EncodingType.BOOLEAN)
        chromosome.init_genes()
        genome.add_chromosome(chromosome)

        chromosome = Chromosome(chromosome_id='Variable10False', encoding_type=EncodingType.BOOLEAN)
        chromosome.init_genes()
        genome.add_chromosome(chromosome)

        chromosome = Chromosome(chromosome_id='Alternating', encoding_type=EncodingType.BOOLEAN)
        chromosome.init_genes()
        genome.add_chromosome(chromosome)

        return genome

    def model_to_genome(self, model):
        pass

    def genome_to_model(self, genome):
        model = {'id': 'booleantest_%s' % genome.id(),
                 'name': 'booleantest',
                 'SingleTrue': genome.chromosomes[0].genes[0].data,
                 'SingleFalse': genome.chromosomes[1].genes[0].data,
                 'Fixed10True': [gene.data for gene in genome.chromosomes[2].genes],
                 'Fixed10False': [gene.data for gene in genome.chromosomes[3].genes],
                 'Variable10True': [gene.data for gene in genome.chromosomes[4].genes],
                 'Variable10False': [gene.data for gene in genome.chromosomes[5].genes],
                 'Alternating': [gene.data for gene in genome.chromosomes[6].genes]}

        return model

