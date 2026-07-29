#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from darwin.mutationchance import (MutationChance, BooleanMutationChance,
                                   IntegerMutationChance, FloatMutationChance,
                                   StringMutationChance, ChromosomeMutationChance)


class TestMutationChance:

    def test_load_with_non_dict_raises(self):
        mc = MutationChance()
        with pytest.raises(Exception, match='config is not a dict'):
            mc.load("not a dict")

    def test_load_updates_attributes(self):
        mc = MutationChance()
        mc.uniform = 0.0
        mc.load({'uniform': 50.0})
        assert mc.uniform == 50.0

    def test_load_ignores_unknown_keys(self):
        mc = MutationChance()
        mc.uniform = 0.0
        mc.load({'unknown_key': 99, 'uniform': 25.0})
        assert mc.uniform == 25.0


class TestBooleanMutationChance:

    def test_defaults(self):
        mc = BooleanMutationChance()
        assert mc.uniform == 0.0
        assert mc.flip == 0.0

    def test_load(self):
        mc = BooleanMutationChance()
        mc.load({'uniform': 10.0, 'flip': 20.0})
        assert mc.uniform == 10.0
        assert mc.flip == 20.0


class TestIntegerMutationChance:

    def test_defaults(self):
        mc = IntegerMutationChance()
        assert mc.uniform == 0.0
        assert mc.boundary == 0.0
        assert mc.gaussian == 0.0
        assert mc.gaussian_sigma == 1.0

    def test_load(self):
        mc = IntegerMutationChance()
        mc.load({'uniform': 5.0, 'boundary': 10.0, 'gaussian': 15.0, 'gaussian_sigma': 2.0})
        assert mc.uniform == 5.0
        assert mc.boundary == 10.0
        assert mc.gaussian == 15.0
        assert mc.gaussian_sigma == 2.0


class TestFloatMutationChance:

    def test_defaults(self):
        mc = FloatMutationChance()
        assert mc.uniform == 0.0
        assert mc.boundary == 0.0
        assert mc.gaussian == 0.0
        assert mc.gaussian_sigma == 1.0

    def test_load(self):
        mc = FloatMutationChance()
        mc.load({'uniform': 5.0, 'boundary': 10.0, 'gaussian': 15.0, 'gaussian_sigma': 3.0})
        assert mc.uniform == 5.0
        assert mc.boundary == 10.0
        assert mc.gaussian == 15.0
        assert mc.gaussian_sigma == 3.0


class TestStringMutationChance:

    def test_defaults(self):
        mc = StringMutationChance()
        assert mc.uniform == 0.0
        assert mc.bitstring == 0.0
        assert mc.duplication == 0.0
        assert mc.deletion == 0.0
        assert mc.insertion == 0.0
        assert mc.swap == 0.0

    def test_load(self):
        mc = StringMutationChance()
        mc.load({'uniform': 1.0, 'bitstring': 2.0, 'duplication': 3.0,
                 'deletion': 4.0, 'insertion': 5.0, 'swap': 6.0})
        assert mc.uniform == 1.0
        assert mc.bitstring == 2.0
        assert mc.duplication == 3.0
        assert mc.deletion == 4.0
        assert mc.insertion == 5.0
        assert mc.swap == 6.0


class TestChromosomeMutationChance:

    def test_defaults(self):
        mc = ChromosomeMutationChance()
        assert mc.uniform == 0.0
        assert mc.duplication == 0.0
        assert mc.deletion == 0.0
        assert mc.insertion == 0.0
        assert mc.swap == 0.0
        assert mc.split == 0.0
        assert mc.merge == 0.0

    def test_load(self):
        mc = ChromosomeMutationChance()
        mc.load({'uniform': 1.0, 'duplication': 2.0, 'deletion': 3.0,
                 'insertion': 4.0, 'swap': 5.0, 'split': 6.0, 'merge': 7.0})
        assert mc.uniform == 1.0
        assert mc.duplication == 2.0
        assert mc.deletion == 3.0
        assert mc.insertion == 4.0
        assert mc.swap == 5.0
        assert mc.split == 6.0
        assert mc.merge == 7.0
