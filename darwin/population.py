#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import glob
import shutil
import time

from genome import Genome
from gene import BooleanGene, IntegerGene, FloatGene, StringGene

from helpers.jsonhelpers import save_to_json_file, load_from_json_file


class Population(object):
    def __init__(self):
        self.genomes = []

    def add_genome(self, genome):
        self.genomes.append(genome)

    def save(self, directory):
        shutil.rmtree(directory)
        time.sleep(1)
        for genome in self.genomes:
            save_to_json_file(os.path.join(directory, '%s.json' % genome.id()), data=genome.to_dict())

    def load_directory(self, directory):
        filenames = glob.glob(os.path.join(directory, '*.json'))

        for filename in filenames:
            genome_data = load_from_json_file(filename=filename)
            self.load_genome(genome_data=genome_data)

    def load_genome(self, genome_data):

            genome = Genome()

            for chromosome_id, chromosome_data in genome_data['chromosomes'].items():
                genome.add_chromosome(chromosome_id=chromosome_id,
                                      encoding_type=chromosome_data['encoding_type'],
                                      n_genes=chromosome_data['n_genes'],
                                      min_value=chromosome_data['min'],
                                      max_value=chromosome_data['max'],
                                      charset=chromosome_data['charset'])

                genome.chromosomes[chromosome_id].genes = []

                for gene_data in chromosome_data['genes']:

                    if chromosome_data['encoding_type'] == 'Boolean':
                        gene = BooleanGene()

                    elif chromosome_data['encoding_type'] == 'Integer':
                        gene = IntegerGene()
                        if chromosome_data['min'] is not None:
                            gene.min = chromosome_data['min']
                        if chromosome_data['max'] is not None:
                            gene.max = chromosome_data['max']

                    elif chromosome_data['encoding_type'] == 'Float':
                        gene = FloatGene()
                        if chromosome_data['min'] is not None:
                            gene.min = chromosome_data['min']
                        if chromosome_data['max'] is not None:
                            gene.max = chromosome_data['max']

                    elif chromosome_data['encoding_type'] == 'String':
                        gene = StringGene()
                        if chromosome_data['charset'] is not None:
                            gene.charset = chromosome_data['charset']

                    else:
                        raise NotImplementedError('Unknown encoding type: %s' % chromosome_data['encoding_type'])

                    gene.data = gene_data
                    genome.chromosomes[chromosome_id].genes.append(gene)

            self.genomes.append(genome)