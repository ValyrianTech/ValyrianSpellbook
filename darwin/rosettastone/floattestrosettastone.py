#!/usr/bin/env python

"""Float test Rosetta Stone for Darwin."""

from chromosome import Chromosome
from encodingtype import EncodingType
from genome import Genome
from rosettastone import RosettaStone


class FloatTestRosettaStone(RosettaStone):
    """Float test Rosetta Stone for Darwin."""

    def __init__(self, name=None):
        super().__init__(name)
        

    def genome_template(self):
        """
        Get a template of the genome, all chromosomes will have empty genes

        :return:
        """
        genome = Genome()

        chromosome = Chromosome(chromosome_id='Single42', encoding_type=EncodingType.FLOAT, n_genes=1)
        chromosome.init_genes()
        genome.add_chromosome(chromosome)

        chromosome = Chromosome(chromosome_id='ZeroToNine', encoding_type=EncodingType.FLOAT)
        chromosome.init_genes()
        genome.add_chromosome(chromosome)

        return genome

    def model_to_genome(self, model):
        """Model to genome."""

    def genome_to_model(self, genome):
        """Genome to model."""
        model = {'id': f'floattest_{genome.id()}',
                 'name': 'floattest',
                 'Single42': genome.chromosomes[0].genes[0].data,
                 'ZeroToNine': [gene.data for gene in genome.chromosomes[1].genes]}

        return model

