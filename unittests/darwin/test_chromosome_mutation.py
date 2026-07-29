#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest.mock import patch

from darwin.chromosome import Chromosome
from darwin.chromosomemutation import ChromosomeMutation
from darwin.encodingtype import EncodingType
from darwin.gene import BooleanGene, IntegerGene, FloatGene, StringGene


class TestDuplication:

    @patch('darwin.chromosomemutation.random.randint', return_value=0)
    def test_duplication(self, _mock):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=None)
        gene = BooleanGene()
        gene.data = True
        chrom.add_gene(gene)
        ChromosomeMutation(chrom).duplication()
        assert len(chrom.genes) == 2
        assert chrom.genes[0].data is True
        assert chrom.genes[1].data is True

    def test_duplication_with_fixed_n_genes(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=3)
        chrom.init_genes()
        original_count = len(chrom.genes)
        ChromosomeMutation(chrom).duplication()
        assert len(chrom.genes) == original_count

    def test_duplication_empty_chromosome(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=None)
        ChromosomeMutation(chrom).duplication()
        assert len(chrom.genes) == 0

    def test_duplication_too_many_genes(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=None)
        for _ in range(1001):
            gene = BooleanGene()
            gene.data = True
            chrom.add_gene(gene)
        ChromosomeMutation(chrom).duplication()
        assert len(chrom.genes) == 1001


class TestDeletion:

    def test_deletion(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=None)
        for _ in range(3):
            gene = BooleanGene()
            gene.data = True
            chrom.add_gene(gene)
        ChromosomeMutation(chrom).deletion()
        assert len(chrom.genes) == 2

    def test_deletion_single_gene(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=None)
        gene = BooleanGene()
        gene.data = True
        chrom.add_gene(gene)
        ChromosomeMutation(chrom).deletion()
        assert len(chrom.genes) == 1

    def test_deletion_empty_chromosome(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=None)
        ChromosomeMutation(chrom).deletion()
        assert len(chrom.genes) == 0

    def test_deletion_fixed_n_genes(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=3)
        chrom.init_genes()
        original_count = len(chrom.genes)
        ChromosomeMutation(chrom).deletion()
        assert len(chrom.genes) == original_count


class TestInsertion:

    @patch('darwin.chromosomemutation.random.randint', return_value=0)
    def test_insertion_boolean(self, _mock):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=None)
        gene = BooleanGene()
        gene.data = True
        chrom.add_gene(gene)
        ChromosomeMutation(chrom).insertion()
        assert len(chrom.genes) == 2
        assert isinstance(chrom.genes[0], BooleanGene)

    @patch('darwin.chromosomemutation.random.randint', return_value=0)
    def test_insertion_integer_with_bounds(self, _mock):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.INTEGER, n_genes=None)
        chrom.min = 0
        chrom.max = 50
        gene = IntegerGene()
        gene.data = 25
        chrom.add_gene(gene)
        ChromosomeMutation(chrom).insertion()
        assert len(chrom.genes) == 2
        assert chrom.genes[0].min == 0
        assert chrom.genes[0].max == 50

    @patch('darwin.chromosomemutation.random.randint', return_value=0)
    def test_insertion_float_with_bounds(self, _mock):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.FLOAT, n_genes=None)
        chrom.min = 0.0
        chrom.max = 50.0
        gene = FloatGene()
        gene.data = 25.0
        chrom.add_gene(gene)
        ChromosomeMutation(chrom).insertion()
        assert len(chrom.genes) == 2
        assert chrom.genes[0].min == 0.0
        assert chrom.genes[0].max == 50.0

    @patch('darwin.chromosomemutation.random.randint', return_value=0)
    def test_insertion_string_with_charset(self, _mock):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.STRING, n_genes=None)
        chrom.charset = 'abc'
        gene = StringGene()
        gene.data = 'hello'
        chrom.add_gene(gene)
        ChromosomeMutation(chrom).insertion()
        assert len(chrom.genes) == 2
        assert chrom.genes[0].charset == 'abc'

    def test_insertion_fixed_n_genes(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=3)
        chrom.init_genes()
        original_count = len(chrom.genes)
        ChromosomeMutation(chrom).insertion()
        assert len(chrom.genes) == original_count

    def test_insertion_unknown_encoding_raises(self):
        chrom = Chromosome(chromosome_id='test', encoding_type='Unknown', n_genes=None)
        gene = BooleanGene()
        gene.data = True
        chrom.add_gene(gene)
        import pytest
        with pytest.raises(NotImplementedError, match='Unknown encoding type'):
            ChromosomeMutation(chrom).insertion()


class TestSwap:

    @patch('darwin.chromosomemutation.random.randint', side_effect=[0, 2])
    def test_swap(self, _mock):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.INTEGER, n_genes=3)
        chrom.genes = []
        for v in [10, 20, 30]:
            gene = IntegerGene()
            gene.data = v
            chrom.add_gene(gene)
        ChromosomeMutation(chrom).swap()
        assert chrom.genes[0].data == 30
        assert chrom.genes[2].data == 10

    def test_swap_single_gene(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=1)
        chrom.init_genes()
        original_data = chrom.genes[0].data
        ChromosomeMutation(chrom).swap()
        assert chrom.genes[0].data == original_data

    def test_swap_empty(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN)
        ChromosomeMutation(chrom).swap()
        assert len(chrom.genes) == 0


class TestSplit:

    @patch('darwin.chromosomemutation.random.randint', side_effect=[0, 2])
    def test_split(self, _mock):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.STRING, n_genes=None)
        gene = StringGene()
        gene.data = 'hello'
        chrom.add_gene(gene)
        ChromosomeMutation(chrom).split()
        assert len(chrom.genes) == 2
        assert chrom.genes[0].data == 'he'
        assert chrom.genes[1].data == 'llo'

    def test_split_non_string_encoding(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.INTEGER, n_genes=None)
        gene = IntegerGene()
        gene.data = 42
        chrom.add_gene(gene)
        ChromosomeMutation(chrom).split()
        assert len(chrom.genes) == 1

    def test_split_fixed_n_genes(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.STRING, n_genes=3)
        chrom.init_genes()
        original_count = len(chrom.genes)
        ChromosomeMutation(chrom).split()
        assert len(chrom.genes) == original_count

    def test_split_empty_chromosome(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.STRING, n_genes=None)
        ChromosomeMutation(chrom).split()
        assert len(chrom.genes) == 0

    @patch('darwin.chromosomemutation.random.randint', return_value=0)
    def test_split_single_char_gene(self, _mock):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.STRING, n_genes=None)
        gene = StringGene()
        gene.data = 'a'
        chrom.add_gene(gene)
        ChromosomeMutation(chrom).split()
        assert len(chrom.genes) == 1


class TestMerge:

    @patch('darwin.chromosomemutation.random.randint', return_value=0)
    def test_merge(self, _mock):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.STRING, n_genes=None)
        gene1 = StringGene()
        gene1.data = 'hello'
        gene2 = StringGene()
        gene2.data = 'world'
        chrom.add_gene(gene1)
        chrom.add_gene(gene2)
        ChromosomeMutation(chrom).merge()
        assert len(chrom.genes) == 1
        assert chrom.genes[0].data == 'helloworld'

    def test_merge_non_string_encoding(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.INTEGER, n_genes=None)
        gene = IntegerGene()
        gene.data = 42
        chrom.add_gene(gene)
        ChromosomeMutation(chrom).merge()
        assert len(chrom.genes) == 1

    def test_merge_single_gene(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.STRING, n_genes=None)
        gene = StringGene()
        gene.data = 'hello'
        chrom.add_gene(gene)
        ChromosomeMutation(chrom).merge()
        assert len(chrom.genes) == 1
        assert chrom.genes[0].data == 'hello'

    def test_merge_empty(self):
        chrom = Chromosome(chromosome_id='test', encoding_type=EncodingType.STRING, n_genes=None)
        ChromosomeMutation(chrom).merge()
        assert len(chrom.genes) == 0
