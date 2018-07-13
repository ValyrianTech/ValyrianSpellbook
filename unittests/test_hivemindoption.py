#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import os

# Change working dir up one level
os.chdir("..")

from hivemind.hivemind import HivemindIssue, HivemindOption

hivemind_issue = HivemindIssue()
hivemind_issue.add_question(question='What is the Answer to the Ultimate Question of Life, the Universe, and Everything?')
hivemind_issue.set_description(description='What is the meaning of life?')
hivemind_issue.set_tags(tags="Don't panic!")
hivemind_issue.answer_type = 'String'
hivemind_issue.set_constraints({'min_length': 2, 'max_length': 10, 'regex': '^[a-zA-Z0-9]+'})
STRING_QUESTION_HASH = hivemind_issue.save()

hivemind_issue.answer_type = 'Float'
hivemind_issue.set_constraints({'min_value': 2, 'max_value': 50, 'decimals': 2})
FLOAT_QUESTION_HASH = hivemind_issue.save()

hivemind_issue.answer_type = 'Integer'
hivemind_issue.set_constraints({'min_value': 2, 'max_value': 50})
INTEGER_QUESTION_HASH = hivemind_issue.save()

hivemind_issue.answer_type = 'Bool'
hivemind_issue.set_constraints({})
BOOL_QUESTION_HASH = hivemind_issue.save()

hivemind_issue.answer_type = 'Complex'
hivemind_issue.set_constraints({'specs': {'a_string': 'String', 'a_float': 'Float'}})
COMPLEX_QUESTION_HASH = hivemind_issue.save()


class TestHivemindOption(object):
    def test_initialization(self):
        option = HivemindOption()
        assert isinstance(option, HivemindOption)

    def test_initializing_with_option_hash(self):
        option = HivemindOption()
        option.set_hivemind_issue(hivemind_issue_hash=STRING_QUESTION_HASH)
        option.set('42')

        option_hash = option.save()

        option2 = HivemindOption(option_hash=option_hash)
        assert option2.hivemind_issue_hash == option.hivemind_issue_hash
        assert option2.value == option.value
        assert option2.answer_type == option.answer_type

    def test_setting_value_that_conflicts_with_constraints(self):
        option = HivemindOption()
        option.set_hivemind_issue(hivemind_issue_hash=STRING_QUESTION_HASH)
        with pytest.raises(Exception):
            option.set('a')  # constraint min_length: 2

    def test_setting_value_that_conflicts_with_answer_type(self):
        option = HivemindOption()
        option.set_hivemind_issue(hivemind_issue_hash=STRING_QUESTION_HASH)
        with pytest.raises(Exception):
            option.set(42)  # must be string instead of number

    @pytest.mark.parametrize("value, expected", [
        ('42', True),
        ('a', False),
        ('12345678901', False),
        ('!éç', False),

    ])
    def test_is_valid_string_option(self, value, expected):
        option = HivemindOption()
        option.set_hivemind_issue(hivemind_issue_hash=STRING_QUESTION_HASH)
        option.value = value
        assert option.is_valid_string_option() is expected

    @pytest.mark.parametrize("value, expected", [
        (42.42, True),
        ('a', False),
        (42, False),
        (51, False),
        (1, False),
        (42, False),
        (42.123, False),
        (42.1, False),

    ])
    def test_is_valid_float_option(self, value, expected):
        option = HivemindOption()
        option.set_hivemind_issue(hivemind_issue_hash=FLOAT_QUESTION_HASH)
        option.value = value
        assert option.is_valid_float_option() is expected

    @pytest.mark.parametrize("value, expected", [
        (42, True),
        ('a', False),
        (42.0, False),
        (51, False),
        (1, False),
        ('42', False),
        (42.123, False),
        (42.1, False),

    ])
    def test_is_valid_integer_option(self, value, expected):
        option = HivemindOption()
        option.set_hivemind_issue(hivemind_issue_hash=INTEGER_QUESTION_HASH)
        option.value = value
        assert option.is_valid_integer_option() is expected

    @pytest.mark.parametrize("value, expected", [
        (True, True),
        (False, True),
        ('True', False),
        ('true', False),
        ('False', False),
        ('false', False),
        (0, False),
        (1.12, False),

    ])
    def test_is_valid_bool_option(self, value, expected):
        option = HivemindOption()
        option.set_hivemind_issue(hivemind_issue_hash=BOOL_QUESTION_HASH)
        option.value = value
        assert option.is_valid_bool_option() is expected

    @pytest.mark.parametrize("value, expected", [
        ({'a_string': 'foo', 'a_float': 42.0}, True),
        ({'a_string': 'foo'}, False),
        ({'a_float': 42}, False),
        ({'foo': 'foo', 'a_float': 42}, False),
        ({'a_string': 'foo', 'a_float': 42, 'foo': 'bar'}, False),
        ({'a_string': 42, 'a_float': 42}, False),
        ({'a_string': 'foo', 'a_float': 'bar'}, False),
    ])
    def test_is_valid_complex_option(self, value, expected):
        option = HivemindOption()
        option.set_hivemind_issue(hivemind_issue_hash=COMPLEX_QUESTION_HASH)
        option.value = value
        assert option.is_valid_complex_option() is expected

