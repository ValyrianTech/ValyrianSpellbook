#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest.mock import patch

from darwin.gene import BooleanGene, IntegerGene, FloatGene, StringGene
from darwin.genemutation import (GeneMutation, BooleanGeneMutation,
                                  IntegerGeneMutation, FloatGeneMutation,
                                  StringGeneMutation)


class TestGeneMutation:

    def test_uniform_calls_set_random_data(self):
        gene = BooleanGene()
        gene.data = True
        mutation = GeneMutation(gene)
        mutation.uniform()
        assert gene.data in [True, False]


class TestBooleanGeneMutation:

    def test_flip_true_to_false(self):
        gene = BooleanGene()
        gene.data = True
        BooleanGeneMutation(gene).flip()
        assert gene.data is False

    def test_flip_false_to_true(self):
        gene = BooleanGene()
        gene.data = False
        BooleanGeneMutation(gene).flip()
        assert gene.data is True


class TestIntegerGeneMutation:

    def test_boundary_sets_min(self):
        gene = IntegerGene()
        gene.data = 50
        gene.min = 0
        gene.max = 100
        with patch('darwin.genemutation.random.randint', return_value=0):
            IntegerGeneMutation(gene).boundary()
        assert gene.data == 0

    def test_boundary_sets_max(self):
        gene = IntegerGene()
        gene.data = 50
        gene.min = 0
        gene.max = 100
        with patch('darwin.genemutation.random.randint', return_value=1):
            IntegerGeneMutation(gene).boundary()
        assert gene.data == 100

    def test_boundary_no_min_max(self):
        gene = IntegerGene()
        gene.data = 50
        gene.min = None
        gene.max = None
        IntegerGeneMutation(gene).boundary()
        assert gene.data == 50

    @patch('darwin.genemutation.np.random.normal', return_value=5)
    def test_gaussian_within_bounds(self, _mock):
        gene = IntegerGene()
        gene.data = 50
        gene.min = 0
        gene.max = 100
        IntegerGeneMutation(gene).gaussian(sigma=2.0)
        assert gene.data == 55

    @patch('darwin.genemutation.np.random.normal', return_value=-60)
    def test_gaussian_exceeds_bounds_not_applied(self, _mock):
        gene = IntegerGene()
        gene.data = 50
        gene.min = 0
        gene.max = 100
        IntegerGeneMutation(gene).gaussian(sigma=2.0)
        assert gene.data == 50

    @patch('darwin.genemutation.np.random.normal', return_value=5)
    def test_gaussian_no_bounds(self, _mock):
        gene = IntegerGene()
        gene.data = 50
        gene.min = None
        gene.max = None
        IntegerGeneMutation(gene).gaussian(sigma=2.0)
        assert gene.data == 55


class TestFloatGeneMutation:

    def test_boundary_sets_min(self):
        gene = FloatGene()
        gene.data = 50.0
        gene.min = 0.0
        gene.max = 100.0
        with patch('darwin.genemutation.random.randint', return_value=0):
            FloatGeneMutation(gene).boundary()
        assert gene.data == 0.0

    def test_boundary_sets_max(self):
        gene = FloatGene()
        gene.data = 50.0
        gene.min = 0.0
        gene.max = 100.0
        with patch('darwin.genemutation.random.randint', return_value=1):
            FloatGeneMutation(gene).boundary()
        assert gene.data == 100.0

    def test_boundary_no_min_max(self):
        gene = FloatGene()
        gene.data = 50.0
        gene.min = None
        gene.max = None
        FloatGeneMutation(gene).boundary()
        assert gene.data == 50.0

    @patch('darwin.genemutation.np.random.normal', return_value=5.5)
    def test_gaussian_within_bounds(self, _mock):
        gene = FloatGene()
        gene.data = 50.0
        gene.min = 0.0
        gene.max = 100.0
        FloatGeneMutation(gene).gaussian(sigma=2.0)
        assert gene.data == 55.5

    @patch('darwin.genemutation.np.random.normal', return_value=-60.0)
    def test_gaussian_exceeds_bounds_not_applied(self, _mock):
        gene = FloatGene()
        gene.data = 50.0
        gene.min = 0.0
        gene.max = 100.0
        FloatGeneMutation(gene).gaussian(sigma=2.0)
        assert gene.data == 50.0

    @patch('darwin.genemutation.np.random.normal', return_value=5.5)
    def test_gaussian_no_bounds(self, _mock):
        gene = FloatGene()
        gene.data = 50.0
        gene.min = None
        gene.max = None
        FloatGeneMutation(gene).gaussian(sigma=2.0)
        assert gene.data == 55.5


class TestStringGeneMutation:

    @patch('darwin.genemutation.random.randint', return_value=2)
    @patch('darwin.genemutation.random.choice', return_value='Z')
    def test_bitstring(self, _mock_choice, _mock_randint):
        gene = StringGene()
        gene.data = 'hello'
        StringGeneMutation(gene).bitstring()
        assert gene.data == 'heZlo'

    def test_bitstring_empty_string(self):
        gene = StringGene()
        gene.data = ''
        StringGeneMutation(gene).bitstring()
        assert gene.data == ''

    def test_duplication(self):
        gene = StringGene()
        gene.data = 'abc'
        StringGeneMutation(gene).duplication()
        assert gene.data == 'abcabc'

    def test_duplication_too_long(self):
        gene = StringGene()
        gene.data = 'x' * 1001
        StringGeneMutation(gene).duplication()
        assert len(gene.data) == 1001

    @patch('darwin.genemutation.random.randint', side_effect=[1, 3])
    def test_deletion(self, _mock):
        gene = StringGene()
        gene.data = 'hello'
        StringGeneMutation(gene).deletion()
        assert gene.data == 'hlo'

    @patch('darwin.genemutation.random.randint', side_effect=[0, 5])
    def test_deletion_full_range(self, _mock):
        gene = StringGene()
        gene.data = 'hello'
        StringGeneMutation(gene).deletion()
        assert gene.data == ''

    @patch('darwin.genemutation.random.randint', return_value=5)
    @patch('darwin.genemutation.random.choice', return_value='X')
    @patch('darwin.genemutation.random.randint', return_value=2)
    def test_insertion(self, _mock_idx, _mock_choice, _mock_nchars):
        gene = StringGene()
        gene.data = 'hello'
        StringGeneMutation(gene).insertion()
        assert 'X' in gene.data

    def test_insertion_empty_string(self):
        gene = StringGene()
        gene.data = ''
        StringGeneMutation(gene).insertion()
        assert len(gene.data) >= 1

    @patch('darwin.genemutation.random.randint', side_effect=[0, 3])
    def test_swap(self, _mock):
        gene = StringGene()
        gene.data = 'hello'
        StringGeneMutation(gene).swap()
        assert gene.data == 'lelho'

    def test_swap_single_char(self):
        gene = StringGene()
        gene.data = 'a'
        StringGeneMutation(gene).swap()
        assert gene.data == 'a'

    def test_swap_empty_string(self):
        gene = StringGene()
        gene.data = ''
        StringGeneMutation(gene).swap()
        assert gene.data == ''
