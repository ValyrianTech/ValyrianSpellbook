#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rosettastone import RosettaStone

from genome import Genome
from chromosome import Chromosome
from encodingtype import EncodingType


class FullTestRosettaStone(RosettaStone):

    def __init__(self, name=None):
        super(FullTestRosettaStone, self).__init__(name)
        
    def genome_template(self):
        """
        Get a template of the genome, all chromosomes will have empty genes

        :return:
        """
        genome = Genome()

        # Boolean
        genome.add_chromosome(chromosome_id='SingleTrue', encoding_type=EncodingType.BOOLEAN, n_genes=1)
        genome.add_chromosome(chromosome_id='SingleFalse', encoding_type=EncodingType.BOOLEAN, n_genes=1)
        genome.add_chromosome(chromosome_id='Fixed10True', encoding_type=EncodingType.BOOLEAN, n_genes=10)
        genome.add_chromosome(chromosome_id='Fixed10False', encoding_type=EncodingType.BOOLEAN, n_genes=10)
        genome.add_chromosome(chromosome_id='Variable10True', encoding_type=EncodingType.BOOLEAN)
        genome.add_chromosome(chromosome_id='Variable10False', encoding_type=EncodingType.BOOLEAN)
        genome.add_chromosome(chromosome_id='Alternating', encoding_type=EncodingType.BOOLEAN)

        # Integer
        genome.add_chromosome(chromosome_id='Single42', encoding_type=EncodingType.INTEGER, n_genes=1)
        genome.add_chromosome(chromosome_id='ZeroToNine', encoding_type=EncodingType.INTEGER)
        genome.add_chromosome(chromosome_id='Lowest42', encoding_type=EncodingType.INTEGER)
        genome.add_chromosome(chromosome_id='Average42', encoding_type=EncodingType.INTEGER)
        genome.add_chromosome(chromosome_id='Highest42', encoding_type=EncodingType.INTEGER)

        # Float
        genome.add_chromosome(chromosome_id='Single42f', encoding_type=EncodingType.FLOAT, n_genes=1)
        genome.add_chromosome(chromosome_id='ZeroToNinef', encoding_type=EncodingType.FLOAT)
        genome.add_chromosome(chromosome_id='Lowest42f', encoding_type=EncodingType.FLOAT)
        genome.add_chromosome(chromosome_id='Average42f', encoding_type=EncodingType.FLOAT)
        genome.add_chromosome(chromosome_id='Highest42f', encoding_type=EncodingType.FLOAT)

        # String
        genome.add_chromosome(chromosome_id='HelloWorld', encoding_type=EncodingType.STRING, n_genes=1)
        genome.add_chromosome(chromosome_id='Alphabet', encoding_type=EncodingType.STRING)
        genome.add_chromosome(chromosome_id='Gattaca', encoding_type=EncodingType.STRING, n_genes=1, charset='GATC')

        return genome

    def model_to_genome(self, model):
        pass

    def genome_to_model(self, genome):
        model = {'id': 'fulltest_%s' % genome.id(),
                 'name': 'fulltest',
                 'SingleTrue': genome.chromosomes['SingleTrue'].value(),
                 'SingleFalse': genome.chromosomes['SingleFalse'].value(),
                 'Fixed10True': genome.chromosomes['Fixed10True'].list(),
                 'Fixed10False': genome.chromosomes['Fixed10False'].list(),
                 'Variable10True': genome.chromosomes['Variable10True'].list(),
                 'Variable10False': genome.chromosomes['Variable10False'].list(),
                 'Alternating': genome.chromosomes['Alternating'].list(),

                 'Single42': genome.chromosomes['Single42'].value(),
                 'ZeroToNine': genome.chromosomes['ZeroToNine'].list(),
                 'Lowest42': genome.chromosomes['Lowest42'].lowest(),
                 'Average42': genome.chromosomes['Average42'].average(),
                 'Highest42': genome.chromosomes['Highest42'].highest(),

                 'Single42f': genome.chromosomes['Single42f'].value(),
                 'ZeroToNinef': genome.chromosomes['ZeroToNinef'].list(),
                 'Lowest42f': genome.chromosomes['Lowest42f'].lowest(),
                 'Average42f': genome.chromosomes['Average42f'].average(),
                 'Highest42f': genome.chromosomes['Highest42f'].highest(),

                 'HelloWorld': genome.chromosomes['HelloWorld'].value(),
                 'Alphabet': genome.chromosomes['Alphabet'].concatenated(),
                 'Gattaca': genome.chromosomes['Gattaca'].value()
                 }

        return model

