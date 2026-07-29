#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from darwin.model.model import Model


class TestModelInit:

    def test_init_default(self):
        model = Model()
        assert model.name is None
        assert model.description == ''

    def test_init_with_name(self):
        model = Model(name='test_model')
        assert model.name == 'test_model'
        assert model.description == ''


class TestConfigure:

    def test_configure_sets_attributes(self):
        model = Model()
        model.name = None
        model.description = ''
        model.custom_field = None
        model.configure({'name': 'test', 'custom_field': 42})
        assert model.name == 'test'
        assert model.custom_field == 42

    def test_configure_ignores_unknown_keys(self):
        model = Model()
        model.name = None
        model.configure({'name': 'test', 'unknown_key': 99})
        assert model.name == 'test'
        assert not hasattr(model, 'unknown_key')

    def test_configure_non_dict_raises(self):
        model = Model()
        with pytest.raises(Exception, match='config is not a dict'):
            model.configure("not a dict")

    def test_configure_empty_dict(self):
        model = Model()
        model.name = 'original'
        model.configure({})
        assert model.name == 'original'


class TestDarwinInitActions:

    def test_darwin_init_actions(self):
        model = Model()
        model.darwin_init_actions()


class TestChampionActions:

    def test_champion_actions(self):
        model = Model()
        model.champion_actions()


class TestInfo:

    def test_info(self):
        model = Model()
        model.info()


class TestPreGenerationActions:

    def test_pre_generation_actions(self, capsys):
        model = Model()
        model.pre_generation_actions()
        captured = capsys.readouterr()
        assert 'pre generation' in captured.out


class TestPostGenerationActions:

    def test_post_generation_actions(self, capsys):
        model = Model()
        model.post_generation_actions(champion=None)
        captured = capsys.readouterr()
        assert 'post generation' in captured.out
