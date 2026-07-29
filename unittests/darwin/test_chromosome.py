#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from unittest.mock import patch

from darwin.chromosome import Chromosome
from darwin.encodingtype import EncodingType
from darwin.gene import Gene, BooleanGene, IntegerGene, FloatGene, StringGene
from darwin.mutationchance import ChromosomeMutationChance


class TestChromosomeInit:

    def test_init(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN)
        assert chrom.id == 'test'
        assert chrom.encoding_type == EncodingType.BOOLEAN
        assert chrom.n_genes is None
        assert chrom.genes == []
        assert chrom.min is None
        assert chrom.max is None
        assert chrom.charset is None

    def test_init_with_n_genes(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.INTEGER, n_genes=5)
        assert chrom.n_genes == 5


class TestAddGene:

    def test_add_gene(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN)
        gene = BooleanGene()
        chrom.add_gene(gene)
        assert len(chrom.genes) == 1
        assert chrom.genes[0] is gene

    def test_add_gene_non_gene_raises(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN)
        with pytest.raises(Exception, match='unexpected type'):
            chrom.add_gene("not a gene")

    def test_add_gene_integer_gene_raises(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN)
        with pytest.raises(Exception, match='unexpected type'):
            chrom.add_gene(42)


class TestInitGenes:

    @patch('darwin.chromosome.random.randint', return_value=3)
    def test_init_genes_boolean_fixed(self, _mock):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=3)
        chrom.init_genes()
        assert len(chrom.genes) == 3
        for gene in chrom.genes:
            assert isinstance(gene, BooleanGene)

    @patch('darwin.chromosome.random.randint', return_value=3)
    def test_init_genes_integer_fixed(self, _mock):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.INTEGER, n_genes=3)
        chrom.min = 0
        chrom.max = 50
        chrom.init_genes()
        assert len(chrom.genes) == 3
        for gene in chrom.genes:
            assert isinstance(gene, IntegerGene)
            assert gene.min == 0
            assert gene.max == 50

    @patch('darwin.chromosome.random.randint', return_value=3)
    def test_init_genes_float_fixed(self, _mock):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.FLOAT, n_genes=3)
        chrom.min = 0.0
        chrom.max = 50.0
        chrom.init_genes()
        assert len(chrom.genes) == 3
        for gene in chrom.genes:
            assert isinstance(gene, FloatGene)
            assert gene.min == 0.0
            assert gene.max == 50.0

    @patch('darwin.chromosome.random.randint', return_value=3)
    def test_init_genes_string_fixed(self, _mock):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.STRING, n_genes=3)
        chrom.charset = 'abc'
        chrom.init_genes()
        assert len(chrom.genes) == 3
        for gene in chrom.genes:
            assert isinstance(gene, StringGene)
            assert gene.charset == 'abc'

    @patch('darwin.chromosome.random.randint', return_value=5)
    def test_init_genes_random_count(self, _mock):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN)
        chrom.init_genes()
        assert len(chrom.genes) == 5

    def test_init_genes_unknown_encoding_raises(self):
        chrom = Chromosome(chromosome_id='test', encoding_type='Unknown')
        with pytest.raises(NotImplementedError, match='Unknown Encoding type'):
            chrom.init_genes()


class TestInfo:

    def test_info(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=1)
        chrom.init_genes()
        info = chrom.info()
        assert 'Boolean' in info
        assert 'GENE 0' in info


class TestApplyMutations:

    @patch('darwin.chromosome.random.uniform', return_value=100.0)
    def test_apply_mutations_no_mutation(self, _mock):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=2)
        chrom.init_genes()
        original_genes = list(chrom.genes)
        chance = ChromosomeMutationChance()
        chrom.apply_mutations(mutation_chance=chance)
        assert chrom.genes == original_genes

    @patch('darwin.chromosome.random.uniform', return_value=0.0)
    def test_apply_mutations_all_triggered(self, _mock):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.STRING, n_genes=2)
        chrom.init_genes()
        chance = ChromosomeMutationChance()
        chance.duplication = 50.0
        chance.deletion = 50.0
        chance.insertion = 50.0
        chance.swap = 50.0
        chance.split = 50.0
        chance.merge = 50.0
        chrom.apply_mutations(mutation_chance=chance)
        assert len(chrom.genes) >= 1


class TestToDict:

    def test_to_dict(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.INTEGER, n_genes=2)
        chrom.min = 0
        chrom.max = 50
        chrom.init_genes()
        d = chrom.to_dict()
        assert d['id'] == 'test'
        assert d['n_genes'] == 2
        assert d['encoding_type'] == EncodingType.INTEGER
        assert d['min'] == 0
        assert d['max'] == 50
        assert d['charset'] is None
        assert len(d['genes']) == 2


class TestValue:

    def test_value(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.INTEGER, n_genes=1)
        chrom.init_genes()
        assert chrom.value() == chrom.genes[0].data


class TestAverage:

    def test_average_integer(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.INTEGER, n_genes=3)
        chrom.genes = []
        for v in [10, 20, 30]:
            gene = IntegerGene()
            gene.data = v
            chrom.add_gene(gene)
        assert chrom.average() == 20

    def test_average_float(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.FLOAT, n_genes=3)
        chrom.genes = []
        for v in [10.0, 20.0, 30.0]:
            gene = FloatGene()
            gene.data = v
            chrom.add_gene(gene)
        assert chrom.average() == 20.0

    def test_average_empty_genes(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.INTEGER)
        assert chrom.average() is None

    def test_average_boolean_raises(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN)
        with pytest.raises(Exception, match='Invalid encoding type'):
            chrom.average()

    def test_average_string_raises(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.STRING)
        with pytest.raises(Exception, match='Invalid encoding type'):
            chrom.average()


class TestLowest:

    def test_lowest_integer(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.INTEGER)
        for v in [30, 10, 20]:
            gene = IntegerGene()
            gene.data = v
            chrom.add_gene(gene)
        assert chrom.lowest() == 10

    def test_lowest_float(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.FLOAT)
        for v in [30.0, 10.0, 20.0]:
            gene = FloatGene()
            gene.data = v
            chrom.add_gene(gene)
        assert chrom.lowest() == 10.0

    def test_lowest_boolean_raises(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN)
        with pytest.raises(Exception, match='Invalid encoding type'):
            chrom.lowest()


class TestHighest:

    def test_highest_integer(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.INTEGER)
        for v in [30, 10, 20]:
            gene = IntegerGene()
            gene.data = v
            chrom.add_gene(gene)
        assert chrom.highest() == 30

    def test_highest_float(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.FLOAT)
        for v in [30.0, 10.0, 20.0]:
            gene = FloatGene()
            gene.data = v
            chrom.add_gene(gene)
        assert chrom.highest() == 30.0

    def test_highest_boolean_raises(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN)
        with pytest.raises(Exception, match='Invalid encoding type'):
            chrom.highest()


class TestConcatenated:

    def test_concatenated_string(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.STRING)
        for s in ['hello', 'world']:
            gene = StringGene()
            gene.data = s
            chrom.add_gene(gene)
        assert chrom.concatenated() == 'helloworld'

    def test_concatenated_integer_raises(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.INTEGER)
        with pytest.raises(Exception, match='Invalid encoding type'):
            chrom.concatenated()


class TestList:

    def test_list(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.INTEGER)
        for v in [10, 20, 30]:
            gene = IntegerGene()
            gene.data = v
            chrom.add_gene(gene)
        assert chrom.list() == [10, 20, 30]

    def test_list_empty(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN)
        assert chrom.list() == []
