#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for Darwin model subclasses: BooleanTest, FloatTest, FullTest, IntegerTest, StringTest.

These model modules use intra-package imports like ``from model import Model`` which
only work when the darwin directory itself is on sys.path (done by ``darwin/__init__.py``).
We inject the base class into the ``model`` package namespace so those imports succeed.
"""
import darwin  # noqa: F401 - import side-effect: adds DARWIN_DIR to sys.path

# Inject Model into the model package so 'from model import Model' works
import model.model
import model
model.Model = model.model.Model

from model.booleantest import BooleanTest
from model.floattest import FloatTest
from model.fulltest import FullTest
from model.integertest import IntegerTest
from model.stringtest import StringTest


class TestBooleanTest:

    def test_init(self):
        bt = BooleanTest()
        assert bt.name is None
        assert bt.SingleTrue is None
        assert bt.SingleFalse is None
        assert bt.Fixed10True is None
        assert bt.Fixed10False is None
        assert bt.Variable10True is None
        assert bt.Variable10False is None
        assert bt.Alternating is None

    def test_init_with_name(self):
        bt = BooleanTest(name='boolean_test')
        assert bt.name == 'boolean_test'

    def test_configure(self):
        bt = BooleanTest()
        bt.configure({'SingleTrue': True, 'SingleFalse': False})
        assert bt.SingleTrue is True
        assert bt.SingleFalse is False

    def test_info(self):
        bt = BooleanTest()
        bt.info()  # base Model.info() is a no-op

    def test_darwin_init_actions(self):
        bt = BooleanTest()
        bt.darwin_init_actions()

    def test_champion_actions(self):
        bt = BooleanTest()
        bt.champion_actions()

    def test_pre_generation_actions(self, capsys):
        bt = BooleanTest()
        bt.pre_generation_actions()
        captured = capsys.readouterr()
        assert 'pre generation' in captured.out

    def test_post_generation_actions(self, capsys):
        bt = BooleanTest()
        bt.post_generation_actions(champion=None)
        captured = capsys.readouterr()
        assert 'post generation' in captured.out


class TestFloatTest:

    def test_init(self):
        ft = FloatTest()
        assert ft.name is None
        assert ft.Single42 is None
        assert ft.ZeroToNine is None

    def test_init_with_name(self):
        ft = FloatTest(name='float_test')
        assert ft.name == 'float_test'

    def test_configure(self):
        ft = FloatTest()
        ft.configure({'Single42': 42.0, 'ZeroToNine': [0.0, 1.0]})
        assert ft.Single42 == 42.0
        assert ft.ZeroToNine == [0.0, 1.0]


class TestIntegerTest:

    def test_init(self):
        it = IntegerTest()
        assert it.name is None
        assert it.Single42 is None
        assert it.ZeroToNine is None

    def test_init_with_name(self):
        it = IntegerTest(name='integer_test')
        assert it.name == 'integer_test'

    def test_configure(self):
        it = IntegerTest()
        it.configure({'Single42': 42, 'ZeroToNine': [0, 1]})
        assert it.Single42 == 42
        assert it.ZeroToNine == [0, 1]


class TestStringTest:

    def test_init(self):
        st = StringTest()
        assert st.name is None
        assert st.HelloWorld is None
        assert st.Alphabet is None
        assert st.Gattaca is None

    def test_init_with_name(self):
        st = StringTest(name='string_test')
        assert st.name == 'string_test'

    def test_configure(self):
        st = StringTest()
        st.configure({'HelloWorld': 'HelloWorld', 'Alphabet': 'abc', 'Gattaca': 'GATTACA'})
        assert st.HelloWorld == 'HelloWorld'
        assert st.Alphabet == 'abc'
        assert st.Gattaca == 'GATTACA'


class TestFullTest:

    def test_init(self):
        ft = FullTest()
        assert ft.name is None
        # Boolean attributes
        assert ft.SingleTrue is None
        assert ft.SingleFalse is None
        assert ft.Fixed10True is None
        assert ft.Fixed10False is None
        assert ft.Variable10True is None
        assert ft.Variable10False is None
        assert ft.Alternating is None
        # Integer attributes
        assert ft.Single42 is None
        assert ft.ZeroToNine is None
        assert ft.Lowest42 is None
        assert ft.Average42 is None
        assert ft.Highest42 is None
        # Float attributes
        assert ft.Single42f is None
        assert ft.ZeroToNinef is None
        assert ft.Lowest42f is None
        assert ft.Average42f is None
        assert ft.Highest42f is None
        # String attributes
        assert ft.HelloWorld is None
        assert ft.Alphabet is None
        assert ft.Gattaca is None

    def test_init_with_name(self):
        ft = FullTest(name='full_test')
        assert ft.name == 'full_test'

    def test_configure(self):
        ft = FullTest()
        config = {
            'SingleTrue': True, 'SingleFalse': False,
            'Fixed10True': [True] * 10, 'Fixed10False': [False] * 10,
            'Variable10True': [True] * 10, 'Variable10False': [False] * 10,
            'Alternating': [True, False] * 5,
            'Single42': 42, 'ZeroToNine': list(range(10)),
            'Lowest42': 42, 'Average42': 42, 'Highest42': 42,
            'Single42f': 42.0, 'ZeroToNinef': [float(i) for i in range(10)],
            'Lowest42f': 42.0, 'Average42f': 42.0, 'Highest42f': 42.0,
            'HelloWorld': 'HelloWorld', 'Alphabet': 'abcdefghijklmnopqrstuvwxyz',
            'Gattaca': 'GATTACA',
        }
        ft.configure(config=config)
        assert ft.SingleTrue is True
        assert ft.Single42 == 42
        assert ft.HelloWorld == 'HelloWorld'
