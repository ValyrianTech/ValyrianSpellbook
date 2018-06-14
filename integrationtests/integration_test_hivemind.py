#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import logging
import random

# Set a specific seed for the random numbers so results can be easily replicated, comment out next line for random results
# random.seed('qsmldkfslskdjf')

# Change working dir up one level
os.chdir("..")

logger = logging.getLogger('Spellbook')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
logger.addHandler(stream_handler)

from hivemind.hivemind import HivemindQuestion, HivemindOption, HivemindOpinion, HivemindState
from helpers.ipfshelpers import IPFS_API
from helpers.BIP44 import set_testnet
from helpers.configurationhelpers import get_use_testnet
from helpers.hotwallethelpers import get_address_from_wallet
from helpers.hotwallethelpers import get_private_key_from_wallet, find_address_in_wallet
from sign_message import sign_message

set_testnet(get_use_testnet())

print 'Starting Spellbook integration test: hivemind'
print '----------------------------------------------\n'


question = 'Which number is bigger?'
description = 'Rank the numbers from high to low'
option_type = 'String'

print 'question:', question
print 'description:', description
print 'option_type:', option_type

hivemind = HivemindQuestion()
assert isinstance(hivemind, HivemindQuestion)

hivemind.add_question(question=question)
assert hivemind.questions[0] == question

hivemind.set_description(description=description)
assert hivemind.description == description

hivemind.set_answer_type(answer_type=option_type)
assert hivemind.answer_type == option_type

hivemind.set_tags(tags='mycompanyhash')
assert hivemind.tags == 'mycompanyhash'

hivemind_id = hivemind.id()
print 'hivemind_id:', hivemind_id
hivemind_id_hash = IPFS_API.add_str(hivemind_id)
print 'hivemind_id_hash:', hivemind_id_hash
print ''

print ''
hivemind_hash = hivemind.save()
print 'Hivemind hash:', hivemind_hash

hivemind_state = HivemindState()
hivemind_state.set_hivemind_question(question_hash=hivemind_hash)

assert hivemind_state.options == []

option_hashes = {}
option_values = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten']
for option_value in option_values:
    print 'adding option %s' % option_value
    option = HivemindOption()
    option.set_hivemind_question(hivemind_question_hash=hivemind_hash)
    option.answer_type = option_type
    option.set(value=option_value)
    option_hashes[option_value] = option.save()
    print 'saved with ipfs hash %s' % option.option_hash

    hivemind_state.add_option(option_hash=option.option_hash)
    print ''

print 'All options:'
print hivemind_state.options
assert len(hivemind_state.options) == len(option_values)

print ''
hivemind_state_hash = hivemind_state.save()
print 'Hivemind state hash:', hivemind_state_hash
print hivemind_state.hivemind_question_hash

n_opinions = 10
for i in range(n_opinions):
    opinionator = get_address_from_wallet(account=3, index=i+1)
    opinion = HivemindOpinion()
    opinion.set_hivemind_state(hivemind_state_hash=hivemind_state_hash)
    ranked_choice = hivemind_state.options
    random.shuffle(ranked_choice)
    opinion.set(opinionator=opinionator, ranked_choice=ranked_choice)
    opinion.save()
    print '%s = %s' % (opinionator, opinion.ranked_choice)
    print 'saved as %s' % opinion.opinion_hash
    signature = sign_message(private_key=get_private_key_from_wallet(account=3, index=i+1)[opinionator], message='IPFS=%s' % opinion.opinion_hash, address=opinionator)
    hivemind_state.add_opinion(opinion_hash=opinion.opinion_hash, signature=signature, weight=1.0)
    print ''

print 'All opinions:'
print hivemind_state.opinions[0]
assert len(hivemind_state.opinions[0]) == n_opinions

print ''

hivemind_state_hash = hivemind_state.save()
print 'Hivemind state hash:', hivemind_state_hash

hivemind_state.calculate_results(question_index=0)
print ''
print hivemind_state.info()

scores = {}

for option_value in option_values:
    option_hash = option_hashes[option_value]
    scores[option_value] = hivemind_state.get_score(option_hash=option_hash, question_index=0)


# Check that adding an opinion with more ranked options is better than fewer ranked options
best_ranked_choice = ['Ten', 'Nine', 'Eight', 'Seven', 'Six', 'Five', 'Four', 'Three', 'Two', 'One']

for n_options in range(len(option_values)):
    print '\n----------------------------------------------'
    my_ranked_choice = best_ranked_choice[:n_options+1]
    print 'my choice: %s ' % my_ranked_choice

    opinionator = get_address_from_wallet(account=3, index=0)
    opinion = HivemindOpinion()
    opinion.set_hivemind_state(hivemind_state_hash=hivemind_state_hash)
    ranked_choice = [option_hashes[option_value] for option_value in my_ranked_choice]

    opinion.set(opinionator=opinionator, ranked_choice=ranked_choice)
    opinion.save()
    print '%s = %s' % (opinionator, opinion.ranked_choice)
    print 'saved as %s' % opinion.opinion_hash
    signature = sign_message(private_key=get_private_key_from_wallet(account=3, index=0)[opinionator], message='IPFS=%s' % opinion.opinion_hash, address=opinionator)
    hivemind_state.add_opinion(opinion_hash=opinion.opinion_hash, signature=signature, weight=1.0, question_index=0)
    print ''

    hivemind_state_hash = hivemind_state.save()
    print 'Hivemind state hash:', hivemind_state_hash

    hivemind_state.calculate_results(question_index=0)
    print hivemind_state.info()

    for option_value in my_ranked_choice:
        new_score = hivemind_state.get_score(option_hash=option_hashes[option_value], question_index=0)

        print 'Checking that option %s has a higher or equal score than previously (old score: %s)' % (option_value, scores[option_value])
        if new_score > scores[option_value]:
            print 'Score has gone UP: %s' % new_score
        elif new_score == scores[option_value]:
            print 'Score stayed EQUAL: %s' % new_score
        else:
            raise Exception('Score has gone DOWN: %s' % new_score)

        scores[option_value] = new_score

    for non_chosen_option in [option_value for option_value in option_values if option_value not in my_ranked_choice]:
        new_score = hivemind_state.get_score(option_hash=option_hashes[non_chosen_option], question_index=0)
        print 'Checking that option %s has a lesser or equal score than previously (old score: %s)' % (non_chosen_option, scores[non_chosen_option])
        if new_score < scores[non_chosen_option]:
            print 'Score has gone DOWN: %s' % new_score
        elif new_score == scores[non_chosen_option]:
            print 'Score stayed EQUAL: %s' % new_score
        else:
            raise Exception('Score has gone UP: %s' % new_score)

        scores[non_chosen_option] = new_score

