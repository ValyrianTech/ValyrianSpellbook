#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

# Set a specific seed for the random numbers so results can be easily replicated, comment out next line for random results
# random.seed('qsmldkfslskdjf')

from hivemind.hivemind import HivemindIssue, HivemindOption, HivemindOpinion, HivemindState
from helpers.ipfshelpers import IPFS_API
from helpers.BIP44 import set_testnet
from helpers.configurationhelpers import get_use_testnet
from helpers.hotwallethelpers import get_address_from_wallet
from helpers.hotwallethelpers import get_private_key_from_wallet, find_address_in_wallet
from sign_message import sign_message

set_testnet(get_use_testnet())

print 'Starting Spellbook integration test: hivemind'
print '----------------------------------------------\n'


print '\n\n###############################'
print '#Hivemind issue               #'
print '###############################'

question0 = 'Which number is bigger?'
question1 = 'Which number is smaller?'
description = 'Rank the numbers from high to low'
answer_type = 'String'

print 'question0:', question0
print 'question1:', question1
print 'description:', description
print 'answer_type:', answer_type

print 'Test initialization'
hivemind_issue = HivemindIssue()
assert isinstance(hivemind_issue, HivemindIssue)

print 'Test adding main question'
hivemind_issue.add_question(question=question0)
assert hivemind_issue.questions[0] == question0

print 'Test adding second question'
hivemind_issue.add_question(question=question1)
assert hivemind_issue.questions[1] == question1

print 'Test if an existing question can not be added twice'
hivemind_issue.add_question(question=question0)
assert len(hivemind_issue.questions) == 2

print 'Test only a string or unicode can be added as a question'
hivemind_issue.add_question(question=1)
assert len(hivemind_issue.questions) == 2

print 'Test setting a description'
hivemind_issue.set_description(description=description)
assert hivemind_issue.description == description

print 'Test only a string or unicode can be added as a description'
hivemind_issue.set_description(description=1)
assert hivemind_issue.description == description

print '\nTest all types of answers'
for answer_type in ['String', 'Bool', 'Integer', 'Float', 'Hivemind', 'Image', 'Video', 'Complex', 'Address']:
    print 'Testing answer type:', answer_type
    hivemind_issue.set_answer_type(answer_type=answer_type)
    assert hivemind_issue.answer_type == answer_type

print '\nTest setting tags'
hivemind_issue.set_tags(tags='mycompanyhash')
assert hivemind_issue.tags == 'mycompanyhash'

print 'Test default consensus type is Single'
assert hivemind_issue.consensus_type == 'Single'

print 'Test setting consensus_types'
for consensus_type in [u'Single', u'Ranked']:
    print 'Testing consensus type:', consensus_type
    hivemind_issue.set_consensus_type(consensus_type=consensus_type)
    assert hivemind_issue.consensus_type == consensus_type

print 'Test setting restrictions'
restrictions = {'addresses': [get_address_from_wallet(account=0, index=0), get_address_from_wallet(account=0, index=1)],
                'options_per_address': 10}
hivemind_issue.set_restrictions(restrictions=restrictions)
assert hivemind_issue.restrictions == restrictions


print '\nSet answer type back to String for the rest of the integration test'
answer_type = u'String'
hivemind_issue.set_answer_type(answer_type=answer_type)
assert hivemind_issue.answer_type == answer_type


print '\nTest setting string constraints'
constraints = {'min_length': 2,
               'max_length': 10,
               'regex': '^[a-zA-Z]+'}
hivemind_issue.set_constraints(constraints=constraints)
assert hivemind_issue.constraints == constraints


print 'Test saving hivemind issue'
hivemind_issue_hash = hivemind_issue.save()
print 'Hivemind issue hash:', hivemind_issue_hash

print '\nTest if initializing with a hivemind issue hash results in the correct hivemind issue'
second_hivemind_issue = HivemindIssue(multihash=hivemind_issue_hash)
# note small differences with unicode vs string text are possible but are ok
print hivemind_issue.get()
print second_hivemind_issue.get()
assert hivemind_issue.get() == second_hivemind_issue.get()


print '\n\n###############################'
print '#Hivemind state               #'
print '###############################'


hivemind_state = HivemindState()
hivemind_state.set_hivemind_issue(issue_hash=hivemind_issue_hash)

assert hivemind_state.options == []


print '\n\n###############################'
print '#Hivemind option              #'
print '###############################'

option_hashes = {}
option_values = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten']
for option_value in option_values:
    print 'adding option %s' % option_value
    option = HivemindOption()
    option.set_hivemind_issue(hivemind_issue_hash=hivemind_issue_hash)
    option.answer_type = answer_type
    option.set(value=option_value)
    option_hashes[option_value] = option.save()
    print 'saved with ipfs hash %s' % option.multihash()

    address = get_address_from_wallet(account=0, index=0)
    message = 'IPFS=%s' % option.multihash()
    private_key = get_private_key_from_wallet(account=0, index=0)[address]

    signature = sign_message(address=address, message=message, private_key=private_key)

    hivemind_state.add_option(option_hash=option.multihash(), address=address, signature=signature)
    print ''

print 'All options:'
print hivemind_state.options
assert len(hivemind_state.options) == len(option_values)

print ''
hivemind_state_hash = hivemind_state.save()
print 'Hivemind state hash:', hivemind_state_hash
print hivemind_state.hivemind_issue_hash


print '\n\n###############################'
print '#Hivemind opinion             #'
print '###############################'

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
    print 'saved as %s' % opinion.multihash()
    signature = sign_message(private_key=get_private_key_from_wallet(account=3, index=i+1)[opinionator], message='IPFS=%s' % opinion.multihash(), address=opinionator)
    hivemind_state.add_opinion(opinion_hash=opinion.multihash(), signature=signature, weight=1.0)
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
    print 'saved as %s' % opinion.multihash()
    signature = sign_message(private_key=get_private_key_from_wallet(account=3, index=0)[opinionator], message='IPFS=%s' % opinion.multihash(), address=opinionator)
    hivemind_state.add_opinion(opinion_hash=opinion.multihash(), signature=signature, weight=1.0, question_index=0)
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

