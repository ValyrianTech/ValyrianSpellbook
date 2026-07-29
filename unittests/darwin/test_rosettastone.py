#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from darwin.rosettastone.rosettastone import RosettaStone


class TestRosettaStoneInit:

    def test_init_default(self):
        rs = RosettaStone()
        assert rs.name is None

    def test_init_with_name(self):
        rs = RosettaStone(name='test_rs')
        assert rs.name == 'test_rs'

    def test_init_with_kwargs(self):
        rs = RosettaStone(name='test', custom='value')
        assert rs.name == 'test'


class TestConfigure:

    def test_configure_sets_attributes(self):
        rs = RosettaStone()
        rs.name = None
        rs.custom_field = None
        rs.configure({'name': 'test', 'custom_field': 42})
        assert rs.name == 'test'
        assert rs.custom_field == 42

    def test_configure_ignores_unknown_keys(self):
        rs = RosettaStone()
        rs.name = 'original'
        rs.configure({'unknown_key': 99})
        assert rs.name == 'original'

    def test_configure_non_dict_raises(self):
        rs = RosettaStone()
        with pytest.raises(Exception, match='config is not a dict'):
            rs.configure("not a dict")

    def test_configure_empty_dict(self):
        rs = RosettaStone()
        rs.name = 'original'
        rs.configure({})
        assert rs.name == 'original'


class TestAbstractMethods:

    def test_genome_template_returns_none(self):
        rs = RosettaStone()
        result = rs.genome_template()
        assert result is None

    def test_model_to_genome_returns_none(self):
        rs = RosettaStone()
        result = rs.model_to_genome(model=None)
        assert result is None

    def test_genome_to_model_returns_none(self):
        rs = RosettaStone()
        result = rs.genome_to_model(genome=None)
        assert result is None
