#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest.mock import patch

from darwin.gene import Gene, BooleanGene, IntegerGene, FloatGene, StringGene
from darwin.mutationchance import (BooleanMutationChance, IntegerMutationChance,
                                   FloatMutationChance, StringMutationChance)


class TestGene:

    def test_init(self):
        gene = Gene()
        assert gene.data is None

    def test_set_random_data_does_nothing(self):
        gene = Gene()
        gene.set_random_data()
        assert gene.data is None

    def test_info_returns_data(self):
        gene = Gene()
        gene.data = 'hello'
        assert gene.info() == 'hello'

    def test_apply_mutations_does_nothing(self):
        gene = Gene()
        gene.data = 'hello'
        gene.apply_mutations(mutation_chance=None)
        assert gene.data == 'hello'


class TestBooleanGene:

    def test_init(self):
        gene = BooleanGene()
        assert gene.data is None

    @patch('darwin.gene.random.randint', return_value=1)
    def test_set_random_data_true(self, _mock):
        gene = BooleanGene()
        gene.set_random_data()
        assert gene.data is True

    @patch('darwin.gene.random.randint', return_value=0)
    def test_set_random_data_false(self, _mock):
        gene = BooleanGene()
        gene.set_random_data()
        assert gene.data is False

    @patch('darwin.gene.random.uniform', return_value=100.0)
    def test_apply_mutations_no_mutation(self, _mock):
        gene = BooleanGene()
        gene.data = True
        chance = BooleanMutationChance()
        chance.uniform = 50.0
        chance.flip = 50.0
        gene.apply_mutations(mutation_chance=chance)
        assert gene.data is True

    @patch('darwin.gene.random.uniform', side_effect=[0.0, 100.0])
    @patch('darwin.gene.random.randint', return_value=1)
    def test_apply_mutations_uniform_triggered(self, _mock_randint, _mock_uniform):
        gene = BooleanGene()
        gene.data = False
        chance = BooleanMutationChance()
        chance.uniform = 50.0
        chance.flip = 0.0
        gene.apply_mutations(mutation_chance=chance)
        assert gene.data is True

    @patch('darwin.gene.random.uniform', side_effect=[100.0, 0.0])
    def test_apply_mutations_flip_triggered(self, _mock):
        gene = BooleanGene()
        gene.data = True
        chance = BooleanMutationChance()
        chance.uniform = 0.0
        chance.flip = 50.0
        gene.apply_mutations(mutation_chance=chance)
        assert gene.data is False

    @patch('darwin.gene.random.uniform', return_value=100.0)
    def test_apply_mutations_with_multiplier_no_mutation(self, _mock):
        gene = BooleanGene()
        gene.data = True
        chance = BooleanMutationChance()
        chance.uniform = 50.0
        chance.flip = 50.0
        gene.apply_mutations(mutation_chance=chance, multiplier=2.0)
        assert gene.data is True


class TestIntegerGene:

    def test_init(self):
        gene = IntegerGene()
        assert gene.data is None
        assert gene.min == 0
        assert gene.max == 100

    @patch('darwin.gene.random.randint', return_value=42)
    def test_set_random_data(self, _mock):
        gene = IntegerGene()
        gene.set_random_data()
        assert gene.data == 42

    def test_set_random_data_with_custom_range(self):
        gene = IntegerGene()
        gene.min = 10
        gene.max = 20
        gene.set_random_data()
        assert 10 <= gene.data <= 20

    @patch('darwin.gene.random.uniform', return_value=100.0)
    def test_apply_mutations_no_mutation(self, _mock):
        gene = IntegerGene()
        gene.data = 42
        chance = IntegerMutationChance()
        gene.apply_mutations(mutation_chance=chance)
        assert gene.data == 42

    @patch('darwin.gene.random.uniform', side_effect=[0.0, 100.0, 100.0])
    @patch('darwin.gene.random.randint', return_value=42)
    def test_apply_mutations_uniform_triggered(self, _mock_randint, _mock_uniform):
        gene = IntegerGene()
        gene.data = 10
        chance = IntegerMutationChance()
        chance.uniform = 50.0
        chance.boundary = 0.0
        chance.gaussian = 0.0
        gene.apply_mutations(mutation_chance=chance)
        assert gene.data == 42

    @patch('darwin.gene.random.uniform', side_effect=[100.0, 0.0, 100.0])
    @patch('darwin.gene.random.randint', return_value=0)
    def test_apply_mutations_boundary_triggered_min(self, _mock_randint, _mock_uniform):
        gene = IntegerGene()
        gene.data = 50
        gene.min = 0
        gene.max = 100
        chance = IntegerMutationChance()
        chance.uniform = 0.0
        chance.boundary = 50.0
        chance.gaussian = 0.0
        gene.apply_mutations(mutation_chance=chance)
        assert gene.data == 0

    @patch('darwin.gene.random.uniform', side_effect=[100.0, 0.0, 100.0])
    @patch('darwin.gene.random.randint', return_value=1)
    def test_apply_mutations_boundary_triggered_max(self, _mock_randint, _mock_uniform):
        gene = IntegerGene()
        gene.data = 50
        gene.min = 0
        gene.max = 100
        chance = IntegerMutationChance()
        chance.uniform = 0.0
        chance.boundary = 50.0
        chance.gaussian = 0.0
        gene.apply_mutations(mutation_chance=chance)
        assert gene.data == 100

    @patch('darwin.gene.random.uniform', side_effect=[100.0, 100.0, 0.0])
    @patch('darwin.genemutation.np.random.normal', return_value=5)
    def test_apply_mutations_gaussian_triggered(self, _mock_normal, _mock_uniform):
        gene = IntegerGene()
        gene.data = 50
        gene.min = 0
        gene.max = 100
        chance = IntegerMutationChance()
        chance.uniform = 0.0
        chance.boundary = 0.0
        chance.gaussian = 50.0
        chance.gaussian_sigma = 2.0
        gene.apply_mutations(mutation_chance=chance)
        assert gene.data == 55


class TestFloatGene:

    def test_init(self):
        gene = FloatGene()
        assert gene.data is None
        assert gene.min == 0.0
        assert gene.max == 100.0

    @patch('darwin.gene.random.uniform', return_value=42.5)
    def test_set_random_data(self, _mock):
        gene = FloatGene()
        gene.set_random_data()
        assert gene.data == 42.5

    @patch('darwin.gene.random.uniform', return_value=100.0)
    def test_apply_mutations_no_mutation(self, _mock):
        gene = FloatGene()
        gene.data = 42.5
        chance = FloatMutationChance()
        gene.apply_mutations(mutation_chance=chance)
        assert gene.data == 42.5

    @patch('darwin.gene.random.uniform', side_effect=[0.0, 42.5, 100.0, 100.0])
    def test_apply_mutations_uniform_triggered(self, _mock):
        gene = FloatGene()
        gene.data = 10.0
        chance = FloatMutationChance()
        chance.uniform = 50.0
        chance.boundary = 0.0
        chance.gaussian = 0.0
        gene.apply_mutations(mutation_chance=chance)
        assert gene.data == 42.5

    @patch('darwin.gene.random.uniform', side_effect=[100.0, 0.0, 100.0])
    @patch('darwin.gene.random.randint', return_value=0)
    def test_apply_mutations_boundary_triggered_min(self, _mock_randint, _mock_uniform):
        gene = FloatGene()
        gene.data = 50.0
        gene.min = 0.0
        gene.max = 100.0
        chance = FloatMutationChance()
        chance.uniform = 0.0
        chance.boundary = 50.0
        chance.gaussian = 0.0
        gene.apply_mutations(mutation_chance=chance)
        assert gene.data == 0.0

    @patch('darwin.gene.random.uniform', side_effect=[100.0, 0.0, 100.0])
    @patch('darwin.gene.random.randint', return_value=1)
    def test_apply_mutations_boundary_triggered_max(self, _mock_randint, _mock_uniform):
        gene = FloatGene()
        gene.data = 50.0
        gene.min = 0.0
        gene.max = 100.0
        chance = FloatMutationChance()
        chance.uniform = 0.0
        chance.boundary = 50.0
        chance.gaussian = 0.0
        gene.apply_mutations(mutation_chance=chance)
        assert gene.data == 100.0

    @patch('darwin.gene.random.uniform', side_effect=[100.0, 100.0, 0.0])
    @patch('darwin.genemutation.np.random.normal', return_value=5.5)
    def test_apply_mutations_gaussian_triggered(self, _mock_normal, _mock_uniform):
        gene = FloatGene()
        gene.data = 50.0
        gene.min = 0.0
        gene.max = 100.0
        chance = FloatMutationChance()
        chance.uniform = 0.0
        chance.boundary = 0.0
        chance.gaussian = 50.0
        chance.gaussian_sigma = 2.0
        gene.apply_mutations(mutation_chance=chance)
        assert gene.data == 55.5


class TestStringGene:

    def test_init(self):
        gene = StringGene()
        assert gene.data is None
        import string
        assert gene.charset == string.ascii_letters + string.digits

    @patch('darwin.gene.random.randint', return_value=5)
    @patch('darwin.gene.random.choice', return_value='a')
    def test_set_random_data(self, _mock_choice, _mock_randint):
        gene = StringGene()
        gene.set_random_data()
        assert gene.data == 'aaaaa'

    @patch('darwin.gene.random.uniform', return_value=100.0)
    def test_apply_mutations_no_mutation(self, _mock):
        gene = StringGene()
        gene.data = 'hello'
        chance = StringMutationChance()
        gene.apply_mutations(mutation_chance=chance)
        assert gene.data == 'hello'

    @patch('darwin.gene.random.uniform', side_effect=[0.0, 100.0, 100.0, 100.0, 100.0, 100.0])
    @patch('darwin.gene.random.randint', return_value=5)
    @patch('darwin.gene.random.choice', return_value='x')
    def test_apply_mutations_uniform_triggered(self, _mock_choice, _mock_randint, _mock_uniform):
        gene = StringGene()
        gene.data = 'hello'
        chance = StringMutationChance()
        chance.uniform = 50.0
        gene.apply_mutations(mutation_chance=chance)
        assert gene.data == 'xxxxx'

    @patch('darwin.gene.random.uniform', side_effect=[100.0, 0.0, 100.0, 100.0, 100.0, 100.0])
    @patch('darwin.gene.random.randint', return_value=0)
    @patch('darwin.gene.random.choice', return_value='x')
    def test_apply_mutations_bitstring_triggered(self, _mock_choice, _mock_randint, _mock_uniform):
        gene = StringGene()
        gene.data = 'hello'
        chance = StringMutationChance()
        chance.bitstring = 50.0
        gene.apply_mutations(mutation_chance=chance)
        assert gene.data == 'xello'

    @patch('darwin.gene.random.uniform', side_effect=[100.0, 100.0, 0.0, 100.0, 100.0, 100.0])
    def test_apply_mutations_duplication_triggered(self, _mock_uniform):
        gene = StringGene()
        gene.data = 'hello'
        chance = StringMutationChance()
        chance.duplication = 50.0
        gene.apply_mutations(mutation_chance=chance)
        assert gene.data == 'hellohello'

    @patch('darwin.gene.random.uniform', side_effect=[100.0, 100.0, 100.0, 0.0, 100.0, 100.0])
    @patch('darwin.gene.random.randint', side_effect=[2, 4])
    def test_apply_mutations_deletion_triggered(self, _mock_randint, _mock_uniform):
        gene = StringGene()
        gene.data = 'hello'
        chance = StringMutationChance()
        chance.deletion = 50.0
        gene.apply_mutations(mutation_chance=chance)
        # deletion removes data[2:4] from 'hello' -> 'he' + 'o' = 'heo'
        assert gene.data == 'heo'

    @patch('darwin.gene.random.uniform', side_effect=[100.0, 100.0, 100.0, 100.0, 0.0, 100.0])
    @patch('darwin.gene.random.randint', return_value=2)
    @patch('darwin.gene.random.choice', return_value='x')
    def test_apply_mutations_insertion_triggered(self, _mock_choice, _mock_randint, _mock_uniform):
        gene = StringGene()
        gene.data = 'hello'
        chance = StringMutationChance()
        chance.insertion = 50.0
        gene.apply_mutations(mutation_chance=chance)
        assert 'x' in gene.data

    @patch('darwin.gene.random.uniform', side_effect=[100.0, 100.0, 100.0, 100.0, 100.0, 0.0])
    @patch('darwin.gene.random.randint', side_effect=[0, 4])
    def test_apply_mutations_swap_triggered(self, _mock_randint, _mock_uniform):
        gene = StringGene()
        gene.data = 'hello'
        chance = StringMutationChance()
        chance.swap = 50.0
        gene.apply_mutations(mutation_chance=chance)
        assert gene.data == 'oellh'
