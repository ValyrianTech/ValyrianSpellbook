#!/usr/bin/env python
# -*- coding: utf-8 -*-
from darwin.fitnessfunction.fitnessfunction import FitnessFunction, Fitness


class TestFitness:

    def test_init(self):
        fitness = Fitness(value=42, data='some data')
        assert fitness.value == 42
        assert fitness.data == 'some data'

    def test_init_with_none(self):
        fitness = Fitness(value=None, data=None)
        assert fitness.value is None
        assert fitness.data is None


class TestFitnessFunction:

    def test_init(self):
        ff = FitnessFunction()
        assert ff.results_file is None

    def test_init_with_kwargs(self):
        ff = FitnessFunction(custom_param='test')
        assert ff.results_file is None

    def test_fitness_returns_none(self):
        ff = FitnessFunction()
        result = ff.fitness(model=None)
        assert result is None

    def test_log_results(self):
        ff = FitnessFunction()
        ff.log_results(filename='/tmp/results.txt')
        assert ff.results_file == '/tmp/results.txt'

    def test_darwin_init_actions(self):
        ff = FitnessFunction()
        ff.darwin_init_actions()
