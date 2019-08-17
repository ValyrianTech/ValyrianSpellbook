#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from hivemind.hivemind import HivemindIssue, HivemindOption, HivemindState, HivemindOpinion

hivemind_issue = HivemindIssue()
hivemind_issue.add_question(question='What is the Answer to the Ultimate Question of Life, the Universe, and Everything?')
hivemind_issue.set_description(description='What is the meaning of life?')
hivemind_issue.set_tags(tags="Don't panic!")
hivemind_issue.answer_type = 'String'
hivemind_issue.set_constraints({'min_length': 2, 'max_length': 10, 'regex': '^[a-zA-Z0-9]+'})
STRING_ISSUE_HASH = hivemind_issue.save()

hivemind_option = HivemindOption()
hivemind_option.set_hivemind_issue(STRING_ISSUE_HASH)
hivemind_option.set('42')

print(hivemind_option.get())
STRING_OPTION1_HASH = hivemind_option.save()
print(STRING_OPTION1_HASH)

hivemind_option.set('fortytwo')
STRING_OPTION2_HASH = hivemind_option.save()

hivemind_state = HivemindState()
hivemind_state.set_hivemind_issue(issue_hash=STRING_ISSUE_HASH)
hivemind_state.add_option(STRING_OPTION1_HASH)
hivemind_state.add_option(STRING_OPTION2_HASH)

STRING_STATE_HASH = hivemind_state.save()

hivemind_issue = HivemindIssue()
hivemind_issue.add_question(question='Choose a number')
hivemind_issue.set_description(description='Choose a number')
hivemind_issue.answer_type = 'Integer'
hivemind_issue.set_constraints({'min_value': 0, 'max_value': 10})
INTEGER_QUESTION_HASH = hivemind_issue.save()

hivemind_option = HivemindOption()
hivemind_option.set_hivemind_issue(INTEGER_QUESTION_HASH)
hivemind_option.set(8)

INTEGER_OPTION1_HASH = hivemind_option.save()

hivemind_option.set(5)
INTEGER_OPTION2_HASH = hivemind_option.save()

hivemind_option.set(6)
INTEGER_OPTION3_HASH = hivemind_option.save()

hivemind_option.set(7)
INTEGER_OPTION4_HASH = hivemind_option.save()

hivemind_option.set(4)
INTEGER_OPTION5_HASH = hivemind_option.save()

hivemind_state = HivemindState()
hivemind_state.set_hivemind_issue(issue_hash=INTEGER_QUESTION_HASH)
hivemind_state.add_option(INTEGER_OPTION1_HASH)
hivemind_state.add_option(INTEGER_OPTION2_HASH)
hivemind_state.add_option(INTEGER_OPTION3_HASH)
hivemind_state.add_option(INTEGER_OPTION4_HASH)
hivemind_state.add_option(INTEGER_OPTION5_HASH)

INTEGER_STATE_HASH = hivemind_state.save()


class TestHivemindOpinion(object):

    def test_initialization(self):
        assert isinstance(HivemindOpinion(), HivemindOpinion)

    def test_hivemind_state_is_set_before_setting_ranked_choice(self):
        opinion = HivemindOpinion()
        with pytest.raises(Exception):
            opinion.set(opinionator='me', ranked_choice=[STRING_OPTION1_HASH, STRING_OPTION2_HASH])

        opinion.set_hivemind_state(hivemind_state_hash=STRING_STATE_HASH)
        opinion.set(opinionator='me', ranked_choice=[STRING_OPTION1_HASH, STRING_OPTION2_HASH])

    def test_setting_ranked_choice_only_contains_valid_option_hashes(self):
        opinion = HivemindOpinion()
        opinion.set_hivemind_state(hivemind_state_hash=STRING_STATE_HASH)
        with pytest.raises(Exception):
            opinion.set(opinionator='me', ranked_choice=[STRING_OPTION1_HASH, STRING_OPTION2_HASH, 'foo', 'bar'])

        with pytest.raises(Exception):
            opinion.set(opinionator='me', ranked_choice=STRING_OPTION1_HASH)  # must be a list of option hashes

    def test_setting_ranked_choice_does_not_contain_duplicate_option_hashes(self):
        opinion = HivemindOpinion()
        opinion.set_hivemind_state(hivemind_state_hash=STRING_STATE_HASH)
        with pytest.raises(Exception):
            opinion.set(opinionator='me', ranked_choice=[STRING_OPTION1_HASH, STRING_OPTION2_HASH, STRING_OPTION1_HASH])

    def test_auto_complete(self):
        opinion = HivemindOpinion()
        opinion.set_hivemind_state(hivemind_state_hash=INTEGER_STATE_HASH)
        opinion.set(opinionator='me', ranked_choice=[INTEGER_OPTION3_HASH])
        assert opinion.ranking() == [INTEGER_OPTION3_HASH]

        print('\nAuto_completing using opinion as MAX value')
        opinion.auto_complete = 'MAX'
        for option_hash in opinion.ranking():
            print(HivemindOption(multihash=option_hash).value, option_hash)
        assert opinion.ranking() == [INTEGER_OPTION5_HASH, INTEGER_OPTION2_HASH, INTEGER_OPTION3_HASH]

        print('\nAuto_completing using opinion as MIN value')
        opinion.auto_complete = 'MIN'
        for option_hash in opinion.ranking():
            print(HivemindOption(multihash=option_hash).value, option_hash)
        assert opinion.ranking() == [INTEGER_OPTION3_HASH, INTEGER_OPTION4_HASH, INTEGER_OPTION1_HASH]

        print('\nAuto_completing using opinion as CLOSEST value if 2 other options are equally close, the order of adding them to the hivemind is used')
        opinion.auto_complete = 'CLOSEST'
        for option_hash in opinion.ranking():
            print(HivemindOption(multihash=option_hash).value, option_hash)
        assert opinion.ranking() == [INTEGER_OPTION3_HASH, INTEGER_OPTION2_HASH, INTEGER_OPTION4_HASH, INTEGER_OPTION1_HASH, INTEGER_OPTION5_HASH]

        print('\nAuto_completing using opinion as CLOSEST value with preference for higher values if equally close')
        opinion.auto_complete = 'CLOSEST_HIGH'
        for option_hash in opinion.ranking():
            print(HivemindOption(multihash=option_hash).value, option_hash)
        assert opinion.ranking() == [INTEGER_OPTION3_HASH, INTEGER_OPTION4_HASH, INTEGER_OPTION2_HASH, INTEGER_OPTION1_HASH, INTEGER_OPTION5_HASH]

        print('\nAuto_completing using opinion as CLOSEST value with preference for lower values if equally close')
        opinion.auto_complete = 'CLOSEST_LOW'
        for option_hash in opinion.ranking():
            print(HivemindOption(multihash=option_hash).value, option_hash)
        assert opinion.ranking() == [INTEGER_OPTION3_HASH, INTEGER_OPTION2_HASH, INTEGER_OPTION4_HASH, INTEGER_OPTION5_HASH, INTEGER_OPTION1_HASH]
