#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest.mock import patch

from darwin.parentselection import (roulette_wheel_selection, rank_selection,
                                     stochastic_universal_sampling,
                                     tournament_selection)


class MockGenome:
    def __init__(self, fitness, genome_id='genome'):
        self.fitness = fitness
        self._id = genome_id

    def id(self):
        return self._id


def make_genomes(fitnesses):
    return [MockGenome(f, f'genome_{i}') for i, f in enumerate(fitnesses)]


class TestRouletteWheelSelection:

    @patch('darwin.parentselection.numpy.random.choice')
    def test_select_two_parents(self, mock_choice):
        genomes = make_genomes([10, 20, 30, 40])
        mock_choice.return_value = [genomes[0], genomes[1]]
        result = roulette_wheel_selection(genomes, n_parents=2)
        assert len(result) == 2

    @patch('darwin.parentselection.numpy.random.choice')
    def test_all_equal_fitness_random_selection(self, mock_choice):
        genomes = make_genomes([10, 10, 10, 10])
        mock_choice.return_value = [genomes[0], genomes[1]]
        result = roulette_wheel_selection(genomes, n_parents=2)
        assert len(result) == 2

    @patch('darwin.parentselection.numpy.random.choice')
    def test_n_parents_greater_than_genomes(self, mock_choice):
        genomes = make_genomes([10, 20])
        mock_choice.return_value = genomes
        result = roulette_wheel_selection(genomes, n_parents=5)
        assert len(result) == 2

    @patch('darwin.parentselection.numpy.random.choice')
    def test_negative_fitness_shifted(self, mock_choice):
        genomes = make_genomes([-10, -20, -30])
        mock_choice.return_value = [genomes[0], genomes[1]]
        result = roulette_wheel_selection(genomes, n_parents=2)
        assert len(result) == 2


class TestRankSelection:

    @patch('darwin.parentselection.numpy.random.choice')
    def test_select_two_parents(self, mock_choice):
        genomes = make_genomes([10, 20, 30, 40])
        mock_choice.return_value = [genomes[0], genomes[1]]
        result = rank_selection(genomes, n_parents=2)
        assert len(result) == 2

    @patch('darwin.parentselection.numpy.random.choice')
    def test_n_parents_greater_than_genomes(self, mock_choice):
        genomes = make_genomes([10, 20])
        mock_choice.return_value = genomes
        result = rank_selection(genomes, n_parents=5)
        assert len(result) == 2

    @patch('darwin.parentselection.numpy.random.choice')
    def test_single_genome(self, mock_choice):
        genomes = make_genomes([10])
        mock_choice.return_value = [genomes[0]]
        result = rank_selection(genomes, n_parents=1)
        assert len(result) == 1


class TestStochasticUniversalSampling:

    def test_returns_n_parents(self):
        genomes = make_genomes([10, 20, 30, 40, 50])
        result = stochastic_universal_sampling(genomes, n_parents=3)
        assert len(result) == 3

    def test_returns_all_with_equal_fitness(self):
        genomes = make_genomes([10, 10, 10, 10, 10])
        result = stochastic_universal_sampling(genomes, n_parents=3)
        assert len(result) == 3

    def test_negative_fitness(self):
        genomes = make_genomes([-10, -20, -30, -40, -50])
        result = stochastic_universal_sampling(genomes, n_parents=2)
        assert len(result) == 2


class TestTournamentSelection:

    @patch('darwin.parentselection.numpy.random.choice')
    def test_select_two_parents(self, mock_choice):
        genomes = make_genomes([40, 30, 20, 10])
        mock_choice.return_value = [0, 1]
        result = tournament_selection(genomes, n_parents=2, tournament_size=3)
        assert len(result) == 2
        assert result[0] is genomes[0]

    @patch('darwin.parentselection.numpy.random.choice')
    def test_tournament_size_larger_than_genomes(self, mock_choice):
        genomes = make_genomes([10, 20])
        mock_choice.return_value = [0, 1]
        result = tournament_selection(genomes, n_parents=2, tournament_size=10)
        assert len(result) == 2

    @patch('darwin.parentselection.numpy.random.choice')
    def test_single_genome(self, mock_choice):
        genomes = make_genomes([10])
        mock_choice.return_value = [0]
        result = tournament_selection(genomes, n_parents=1, tournament_size=1)
        assert len(result) == 1
        assert result[0] is genomes[0]

    @patch('darwin.parentselection.numpy.random.choice')
    def test_selects_best_in_tournament(self, mock_choice):
        genomes = make_genomes([50, 40, 30, 20, 10])
        mock_choice.return_value = [3, 4, 2]
        result = tournament_selection(genomes, n_parents=1, tournament_size=3)
        assert result[0] is genomes[2]
