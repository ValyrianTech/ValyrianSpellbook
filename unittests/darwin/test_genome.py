#!/usr/bin/env python
# -*- coding: utf-8 -*-
from darwin.genome import Genome
from darwin.encodingtype import EncodingType
from darwin.gene import BooleanGene, IntegerGene, FloatGene, StringGene


class TestGenomeInit:

    def test_init(self):
        genome = Genome()
        assert genome.chromosomes == {}
        assert genome.fitness is None


class TestAddChromosome:

    def test_add_chromosome_boolean(self):
        genome = Genome()
        genome.add_chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=3)
        assert 'test' in genome.chromosomes
        assert len(genome.chromosomes['test'].genes) == 3
        for gene in genome.chromosomes['test'].genes:
            assert isinstance(gene, BooleanGene)

    def test_add_chromosome_integer_with_bounds(self):
        genome = Genome()
        genome.add_chromosome(chromosome_id='test', encoding_type=EncodingType.INTEGER,
                              min_value=0, max_value=50, n_genes=2)
        chrom = genome.chromosomes['test']
        assert chrom.min == 0
        assert chrom.max == 50
        for gene in chrom.genes:
            assert isinstance(gene, IntegerGene)
            assert gene.min == 0
            assert gene.max == 50

    def test_add_chromosome_float_with_bounds(self):
        genome = Genome()
        genome.add_chromosome(chromosome_id='test', encoding_type=EncodingType.FLOAT,
                              min_value=0.0, max_value=50.0, n_genes=2)
        chrom = genome.chromosomes['test']
        assert chrom.min == 0.0
        assert chrom.max == 50.0
        for gene in chrom.genes:
            assert isinstance(gene, FloatGene)
            assert gene.min == 0.0
            assert gene.max == 50.0

    def test_add_chromosome_string_with_charset(self):
        genome = Genome()
        genome.add_chromosome(chromosome_id='test', encoding_type=EncodingType.STRING,
                              charset='abc', n_genes=2)
        chrom = genome.chromosomes['test']
        assert chrom.charset == 'abc'
        for gene in chrom.genes:
            assert isinstance(gene, StringGene)
            assert gene.charset == 'abc'

    def test_add_multiple_chromosomes(self):
        genome = Genome()
        genome.add_chromosome(chromosome_id='c1', encoding_type=EncodingType.BOOLEAN, n_genes=1)
        genome.add_chromosome(chromosome_id='c2', encoding_type=EncodingType.INTEGER, n_genes=2)
        assert len(genome.chromosomes) == 2


class TestInitWithRandomData:

    def test_init_with_random_data(self):
        genome = Genome()
        genome.add_chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=3)
        for gene in genome.chromosomes['test'].genes:
            gene.data = None
        genome.init_with_random_data()
        for gene in genome.chromosomes['test'].genes:
            assert gene.data is not None


class TestInfo:

    def test_info(self):
        genome = Genome()
        genome.add_chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=1)
        info = genome.info()
        assert 'Genome id' in info
        assert 'CHROMOSOME test' in info


class TestId:

    def test_id_is_string(self):
        genome = Genome()
        genome.add_chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=1)
        assert isinstance(genome.id(), str)

    def test_id_deterministic(self):
        genome1 = Genome()
        genome1.add_chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=1)
        genome1.chromosomes['test'].genes[0].data = True

        genome2 = Genome()
        genome2.add_chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=1)
        genome2.chromosomes['test'].genes[0].data = True

        assert genome1.id() == genome2.id()

    def test_id_different_for_different_data(self):
        genome1 = Genome()
        genome1.add_chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=1)
        genome1.chromosomes['test'].genes[0].data = True

        genome2 = Genome()
        genome2.add_chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=1)
        genome2.chromosomes['test'].genes[0].data = False

        assert genome1.id() != genome2.id()


class TestToDict:

    def test_to_dict(self):
        genome = Genome()
        genome.add_chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=2)
        genome.fitness = 42
        d = genome.to_dict()
        assert 'chromosomes' in d
        assert 'test' in d['chromosomes']
        assert d['fitness'] == 42
        assert 'id' in d
        assert d['chromosomes']['test']['encoding_type'] == EncodingType.BOOLEAN
        assert len(d['chromosomes']['test']['genes']) == 2
