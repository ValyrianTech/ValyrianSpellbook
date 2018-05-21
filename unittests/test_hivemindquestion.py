import pytest
import logging
import sys
import os

# Change working dir up one level
os.chdir("..")

logger = logging.getLogger('Spellbook')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
logger.addHandler(stream_handler)

from hivemind.hivemind import HivemindQuestion


class TestHivemindQuestion(object):
    def test_initialization(self):
        assert isinstance(HivemindQuestion(), HivemindQuestion)

    def test_setting_question(self):
        hivemind_question = HivemindQuestion()
        question = 'What?'
        hivemind_question.set_question(question)
        assert hivemind_question.question == question

    def test_setting_description(self):
        hivemind_question = HivemindQuestion()
        description = 'this.'
        hivemind_question.set_description(description)
        assert hivemind_question.description == description

    def test_setting_tags(self):
        hivemind_question = HivemindQuestion()
        tags = 'some additional tags'
        hivemind_question.set_tags(tags=tags)
        assert hivemind_question.tags == tags

    @pytest.mark.parametrize("answer_type", ['String', 'Bool', 'Integer', 'Float', 'Hivemind', 'Image', 'Video', 'Complex'])
    def test_setting_a_valid_answer_type(self, answer_type):
        hivemind_question = HivemindQuestion()
        hivemind_question.set_answer_type(answer_type)
        assert hivemind_question.answer_type == answer_type

    def test_setting_an_invalid_answer_type(self):
        hivemind_question = HivemindQuestion()
        with pytest.raises(Exception):
            hivemind_question.set_answer_type('invalid_type')

    def test_setting_complex_constraints(self):
        hivemind_question = HivemindQuestion()
        hivemind_question.answer_type = 'Complex'
        hivemind_question.set_constraints(constraints={'specs': {'a_string': 'String', 'a_float': 'Float'}})

        with pytest.raises(Exception):
            hivemind_question.set_constraints(constraints={'specs': {'a_string': 'foo', 'a_float': 'Float'}})

        with pytest.raises(Exception):
            hivemind_question.set_constraints(constraints={'specs': {'a_string': 'String', 'a_float': 42.0}})

        with pytest.raises(Exception):
            hivemind_question.set_constraints(constraints={'specs': 'foo'})

    @pytest.mark.parametrize("constraint_type", ['min_length', 'max_length', 'min_value', 'max_value', 'decimals'])
    def test_setting_constraints_types(self, constraint_type):
        hivemind_question = HivemindQuestion()
        hivemind_question.set_constraints({constraint_type: 2})
        assert hivemind_question.constraints == {constraint_type: 2}

        with pytest.raises(Exception):
            hivemind_question.set_constraints({constraint_type: '2'})

    def test_setting_regex_constraints(self):
        hivemind_question = HivemindQuestion()
        hivemind_question.set_constraints({'regex': '^[a-z]+'})
        assert hivemind_question.constraints == {'regex': '^[a-z]+'}

        with pytest.raises(Exception):
            hivemind_question.set_constraints({'regex': 2})

    def test_setting_invalid_constraints(self):
        hivemind_question = HivemindQuestion()
        with pytest.raises(Exception):
            hivemind_question.set_constraints({'foo': 'bar'})

    def test_saving_a_hivemind_question(self):
        hivemind_question = HivemindQuestion()
        hivemind_question.set_question(question='What is the Answer to the Ultimate Question of Life, the Universe, and Everything?')
        hivemind_question.set_description(description='What is the meaning of life?')
        hivemind_question.set_tags(tags="Don't panic!")
        hivemind_question.answer_type = 'String'
        hivemind_question.set_constraints({'min_length': 2})

        question_hash = hivemind_question.save()
        print question_hash
        assert question_hash is not None

