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

from hivemind.hivemind import HivemindQuestion, HivemindOption, HivemindState, HivemindOpinion

hivemind_question = HivemindQuestion()
hivemind_question.set_question(question='What is the Answer to the Ultimate Question of Life, the Universe, and Everything?')
hivemind_question.set_description(description='What is the meaning of life?')
hivemind_question.set_tags(tags="Don't panic!")
hivemind_question.answer_type = 'String'
hivemind_question.set_constraints({'min_length': 2, 'max_length': 10, 'regex': '^[a-zA-Z0-9]+'})
STRING_QUESTION_HASH = hivemind_question.save()

hivemind_option = HivemindOption()
hivemind_option.set_hivemind_question(STRING_QUESTION_HASH)
hivemind_option.set('42')

OPTION1_HASH = hivemind_option.save()

hivemind_option.set('fortytwo')
OPTION2_HASH = hivemind_option.save()

hivemind_state = HivemindState()
hivemind_state.set_hivemind_question(question_hash=STRING_QUESTION_HASH)
hivemind_state.add_option(OPTION1_HASH)
hivemind_state.add_option(OPTION2_HASH)

STATE_HASH = hivemind_state.save()


class TestHivemindOpinion(object):

    def test_initialization(self):
        assert isinstance(HivemindOpinion(), HivemindOpinion)

    def test_hivemind_state_is_set_before_setting_ranked_choice(self):
        opinion = HivemindOpinion()
        with pytest.raises(Exception):
            opinion.set(opinionator='me', ranked_choice=[OPTION1_HASH, OPTION2_HASH])

        opinion.set_hivemind_state(hivemind_state_hash=STATE_HASH)
        opinion.set(opinionator='me', ranked_choice=[OPTION1_HASH, OPTION2_HASH])

    def test_setting_ranked_choice_only_contains_valid_option_hashes(self):
        opinion = HivemindOpinion()
        opinion.set_hivemind_state(hivemind_state_hash=STATE_HASH)
        with pytest.raises(Exception):
            opinion.set(opinionator='me', ranked_choice=[OPTION1_HASH, OPTION2_HASH, 'foo', 'bar'])

        with pytest.raises(Exception):
            opinion.set(opinionator='me', ranked_choice=OPTION1_HASH)  # must be a list of option hashes

    def test_setting_ranked_choice_does_not_contain_duplicate_option_hashes(self):
        opinion = HivemindOpinion()
        opinion.set_hivemind_state(hivemind_state_hash=STATE_HASH)
        with pytest.raises(Exception):
            opinion.set(opinionator='me', ranked_choice=[OPTION1_HASH, OPTION2_HASH, OPTION1_HASH])
