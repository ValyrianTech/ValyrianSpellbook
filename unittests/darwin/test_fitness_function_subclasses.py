#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for Darwin fitness function subclasses.

These modules use intra-package imports like ``from fitnessfunction import FitnessFunction``
which only work when the darwin directory itself is on sys.path (done by ``darwin/__init__.py``).
We inject the base class into the ``fitnessfunction`` package namespace so those imports succeed.
"""
import pytest

import darwin  # noqa: F401 - import side-effect: adds DARWIN_DIR to sys.path

# Inject FitnessFunction into the fitnessfunction package
import fitnessfunction.fitnessfunction
import fitnessfunction
fitnessfunction.FitnessFunction = fitnessfunction.fitnessfunction.FitnessFunction

# Also inject Model into model package (needed by fitness functions that import models)
import model.model
import model
model.Model = model.model.Model

from fitnessfunction.booleantestfitnessfunction import BooleanTestFitnessFunction
from fitnessfunction.floattestfitnessfunction import FloatTestFitnessFunction
from fitnessfunction.fulltestfitnessfunction import FullTestFitnessFunction
from fitnessfunction.integertestfitnessfunction import IntegerTestFitnessFunction
from fitnessfunction.stringtestfitnessfunction import StringTestFitnessFunction

from model.booleantest import BooleanTest
from model.floattest import FloatTest
from model.fulltest import FullTest
from model.integertest import IntegerTest
from model.stringtest import StringTest


class TestBooleanTestFitnessFunction:

    def test_init(self):
        ff = BooleanTestFitnessFunction()
        assert ff.results_file is None

    def test_fitness_perfect(self):
        ff = BooleanTestFitnessFunction()
        model = BooleanTest()
        model.SingleTrue = True
        model.SingleFalse = False
        model.Fixed10True = [True] * 10
        model.Fixed10False = [False] * 10
        model.Variable10True = [True] * 10
        model.Variable10False = [False] * 10
        model.Alternating = [True, False] * 5
        result = ff.fitness(model=model)
        assert result == 250

    def test_fitness_worst(self):
        ff = BooleanTestFitnessFunction()
        model = BooleanTest()
        model.SingleTrue = False
        model.SingleFalse = True
        model.Fixed10True = [False] * 10
        model.Fixed10False = [True] * 10
        model.Variable10True = [False] * 10
        model.Variable10False = [True] * 10
        model.Alternating = [False, True] * 5
        result = ff.fitness(model=model)
        assert result == -250

    def test_fitness_wrong_model_type_raises(self):
        ff = BooleanTestFitnessFunction()
        with pytest.raises(Exception, match='not a BooleanTest'):
            ff.fitness(model="not a model")

    def test_log_results(self):
        ff = BooleanTestFitnessFunction()
        ff.log_results(filename='/tmp/results.txt')
        assert ff.results_file == '/tmp/results.txt'

    def test_darwin_init_actions(self):
        ff = BooleanTestFitnessFunction()
        ff.darwin_init_actions()


class TestFloatTestFitnessFunction:

    def test_init(self):
        ff = FloatTestFitnessFunction()
        assert ff.results_file is None

    def test_fitness_perfect(self):
        ff = FloatTestFitnessFunction()
        model = FloatTest()
        model.Single42 = 42.0
        model.ZeroToNine = [float(i) for i in range(10)]
        result = ff.fitness(model=model)
        assert result == 200

    def test_fitness_partial(self):
        ff = FloatTestFitnessFunction()
        model = FloatTest()
        model.Single42 = 40.0
        model.ZeroToNine = [float(i) for i in range(10)]
        result = ff.fitness(model=model)
        assert result == 198  # 100 - 2 = 98 for Single42, +100 for ZeroToNine

    def test_fitness_wrong_model_type_raises(self):
        ff = FloatTestFitnessFunction()
        with pytest.raises(Exception, match='not a FloatTest'):
            ff.fitness(model="not a model")


class TestIntegerTestFitnessFunction:

    def test_init(self):
        ff = IntegerTestFitnessFunction()
        assert ff.results_file is None

    def test_fitness_perfect(self):
        ff = IntegerTestFitnessFunction()
        model = IntegerTest()
        model.Single42 = 42
        model.ZeroToNine = list(range(10))
        result = ff.fitness(model=model)
        assert result == 210

    def test_fitness_partial(self):
        ff = IntegerTestFitnessFunction()
        model = IntegerTest()
        model.Single42 = 40
        model.ZeroToNine = list(range(10))
        result = ff.fitness(model=model)
        assert result == 208  # 100 - 2 = 98, +110 for ZeroToNine

    def test_fitness_wrong_model_type_raises(self):
        ff = IntegerTestFitnessFunction()
        with pytest.raises(Exception, match='not a IntegerTest'):
            ff.fitness(model="not a model")


class TestStringTestFitnessFunction:

    def test_init(self):
        ff = StringTestFitnessFunction()
        assert ff.results_file is None

    def test_fitness_perfect(self):
        ff = StringTestFitnessFunction()
        model = StringTest()
        model.HelloWorld = 'HelloWorld'
        model.Alphabet = 'abcdefghijklmnopqrstuvwxyz'
        model.Gattaca = 'GATTACA'
        result = ff.fitness(model=model)
        assert result == 193

    def test_fitness_wrong_model_type_raises(self):
        ff = StringTestFitnessFunction()
        with pytest.raises(Exception, match='not a StringTest'):
            ff.fitness(model="not a model")

    def test_fitness_long_strings(self):
        ff = StringTestFitnessFunction()
        model = StringTest()
        model.HelloWorld = 'HelloWorldExtra'
        model.Alphabet = 'abcdefghijklmnopqrstuvwxyz'
        model.Gattaca = 'GATTACA'
        result = ff.fitness(model=model)
        # Length penalty for HelloWorld: 50 - abs(14 - 10) = 46
        # Each char in HelloWorld matches up to len('HelloWorld')=10, then -1 for extras
        assert result < 193

    def test_fitness_alphabet_too_long(self):
        ff = StringTestFitnessFunction()
        model = StringTest()
        model.HelloWorld = 'HelloWorld'
        model.Alphabet = 'abcdefghijklmnopqrstuvwxyzEXTRA'
        model.Gattaca = 'GATTACA'
        result = ff.fitness(model=model)
        assert result < 193

    def test_fitness_gattaca_too_long(self):
        ff = StringTestFitnessFunction()
        model = StringTest()
        model.HelloWorld = 'HelloWorld'
        model.Alphabet = 'abcdefghijklmnopqrstuvwxyz'
        model.Gattaca = 'GATTACAEEXTRA'
        result = ff.fitness(model=model)
        assert result < 193


class TestFullTestFitnessFunction:

    def test_init(self):
        ff = FullTestFitnessFunction()
        assert ff.results_file is None

    def test_fitness_perfect(self):
        ff = FullTestFitnessFunction()
        model = FullTest()
        # Boolean
        model.SingleTrue = True
        model.SingleFalse = False
        model.Fixed10True = [True] * 10
        model.Fixed10False = [False] * 10
        model.Variable10True = [True] * 10
        model.Variable10False = [False] * 10
        model.Alternating = [True, False] * 5
        # Integer
        model.Single42 = 42
        model.ZeroToNine = list(range(10))
        model.Lowest42 = 42
        model.Average42 = 42
        model.Highest42 = 42
        # Float
        model.Single42f = 42.0
        model.ZeroToNinef = [float(i) for i in range(10)]
        model.Lowest42f = 42.0
        model.Average42f = 42.0
        model.Highest42f = 42.0
        # String
        model.HelloWorld = 'HelloWorld'
        model.Alphabet = 'abcdefghijklmnopqrstuvwxyz'
        model.Gattaca = 'GATTACA'
        result = ff.fitness(model=model)
        # 250 (boolean) + 210 (integer) + 200 (float) + 430 (string, +10 per char match) = 1090
        assert result == 1090

    def test_fitness_wrong_model_type_raises(self):
        ff = FullTestFitnessFunction()
        with pytest.raises(Exception, match='not a FullTest'):
            ff.fitness(model="not a model")

    def test_fitness_worst(self):
        ff = FullTestFitnessFunction()
        model = FullTest()
        # Boolean - all wrong
        model.SingleTrue = False
        model.SingleFalse = True
        model.Fixed10True = [False] * 10
        model.Fixed10False = [True] * 10
        model.Variable10True = [False] * 10
        model.Variable10False = [True] * 10
        model.Alternating = [False, True] * 5
        # Integer - wrong
        model.Single42 = 0
        model.ZeroToNine = [0] * 10
        model.Lowest42 = 0
        model.Average42 = 0
        model.Highest42 = 0
        # Float - wrong
        model.Single42f = 0.0
        model.ZeroToNinef = [0.0] * 10
        model.Lowest42f = 0.0
        model.Average42f = 0.0
        model.Highest42f = 0.0
        # String - wrong
        model.HelloWorld = ''
        model.Alphabet = ''
        model.Gattaca = ''
        result = ff.fitness(model=model)
        assert result < 0

    def test_fitness_strings_too_long(self):
        """Exercise the else branches when string length exceeds target (lines 92, 98, 104)."""
        ff = FullTestFitnessFunction()
        model = FullTest()
        # Boolean - perfect
        model.SingleTrue = True
        model.SingleFalse = False
        model.Fixed10True = [True] * 10
        model.Fixed10False = [False] * 10
        model.Variable10True = [True] * 10
        model.Variable10False = [False] * 10
        model.Alternating = [True, False] * 5
        # Integer - perfect
        model.Single42 = 42
        model.ZeroToNine = list(range(10))
        model.Lowest42 = 42
        model.Average42 = 42
        model.Highest42 = 42
        # Float - perfect
        model.Single42f = 42.0
        model.ZeroToNinef = [float(i) for i in range(10)]
        model.Lowest42f = 42.0
        model.Average42f = 42.0
        model.Highest42f = 42.0
        # String - all too long (triggers else branches at lines 92, 98, 104)
        model.HelloWorld = 'HelloWorldXXXXX'
        model.Alphabet = 'abcdefghijklmnopqrstuvwxyzXXXXX'
        model.Gattaca = 'GATTACAXXXX'
        result = ff.fitness(model=model)
        # Should be less than perfect (1090) due to string penalties
        assert result < 1090
