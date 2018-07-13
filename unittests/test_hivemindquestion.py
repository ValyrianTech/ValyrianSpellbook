import pytest
import os

# Change working dir up one level
os.chdir("..")

from hivemind.hivemind import HivemindIssue


class TestHivemindQuestion(object):
    def test_initialization(self):
        assert isinstance(HivemindIssue(), HivemindIssue)

    def test_setting_question(self):
        hivemind_issue = HivemindIssue()
        question = 'What?'
        hivemind_issue.add_question(question)
        assert hivemind_issue.questions[0] == question

    def test_setting_description(self):
        hivemind_issue = HivemindIssue()
        description = 'this.'
        hivemind_issue.set_description(description)
        assert hivemind_issue.description == description

    def test_setting_tags(self):
        hivemind_issue = HivemindIssue()
        tags = 'some additional tags'
        hivemind_issue.set_tags(tags=tags)
        assert hivemind_issue.tags == tags

    @pytest.mark.parametrize("answer_type", ['String', 'Bool', 'Integer', 'Float', 'Hivemind', 'Image', 'Video', 'Complex'])
    def test_setting_a_valid_answer_type(self, answer_type):
        hivemind_issue = HivemindIssue()
        hivemind_issue.set_answer_type(answer_type)
        assert hivemind_issue.answer_type == answer_type

    def test_setting_an_invalid_answer_type(self):
        hivemind_issue = HivemindIssue()
        with pytest.raises(Exception):
            hivemind_issue.set_answer_type('invalid_type')

    def test_setting_complex_constraints(self):
        hivemind_issue = HivemindIssue()
        hivemind_issue.answer_type = 'Complex'
        hivemind_issue.set_constraints(constraints={'specs': {'a_string': 'String', 'a_float': 'Float'}})

        with pytest.raises(Exception):
            hivemind_issue.set_constraints(constraints={'specs': {'a_string': 'foo', 'a_float': 'Float'}})

        with pytest.raises(Exception):
            hivemind_issue.set_constraints(constraints={'specs': {'a_string': 'String', 'a_float': 42.0}})

        with pytest.raises(Exception):
            hivemind_issue.set_constraints(constraints={'specs': 'foo'})

    @pytest.mark.parametrize("constraint_type", ['min_length', 'max_length', 'min_value', 'max_value', 'decimals'])
    def test_setting_constraints_types(self, constraint_type):
        hivemind_issue = HivemindIssue()
        hivemind_issue.set_constraints({constraint_type: 2})
        assert hivemind_issue.constraints == {constraint_type: 2}

        with pytest.raises(Exception):
            hivemind_issue.set_constraints({constraint_type: '2'})

    def test_setting_regex_constraints(self):
        hivemind_issue = HivemindIssue()
        hivemind_issue.set_constraints({'regex': '^[a-z]+'})
        assert hivemind_issue.constraints == {'regex': '^[a-z]+'}

        with pytest.raises(Exception):
            hivemind_issue.set_constraints({'regex': 2})

    def test_setting_invalid_constraints(self):
        hivemind_issue = HivemindIssue()
        with pytest.raises(Exception):
            hivemind_issue.set_constraints({'foo': 'bar'})

    def test_saving_a_hivemind_question(self):
        hivemind_issue = HivemindIssue()
        hivemind_issue.add_question(question='What is the Answer to the Ultimate Question of Life, the Universe, and Everything?')
        hivemind_issue.set_description(description='What is the meaning of life?')
        hivemind_issue.set_tags(tags="Don't panic!")
        hivemind_issue.answer_type = 'String'
        hivemind_issue.set_constraints({'min_length': 2})

        issue_hash = hivemind_issue.save()
        print issue_hash
        assert issue_hash is not None

