#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

# Set a specific seed for the random numbers so results can be easily replicated, comment out next line for random results
# random.seed('qsmldkfslskdjf')

from hivemind.hivemind import HivemindIssue, HivemindOption, HivemindOpinion, HivemindState
from helpers.BIP44 import set_testnet
from helpers.configurationhelpers import get_use_testnet
from helpers.hotwallethelpers import get_address_from_wallet
from helpers.hotwallethelpers import get_private_key_from_wallet
from sign_message import sign_message

set_testnet(get_use_testnet())

print 'Starting Spellbook integration test: hivemind with restrictions'
print '----------------------------------------------\n'


question = 'Which number is bigger?'
description = 'Rank the numbers from high to low'
option_type = 'String'

print 'question:', question
print 'description:', description
print 'option_type:', option_type

hivemind_issue = HivemindIssue()
assert isinstance(hivemind_issue, HivemindIssue)

hivemind_issue.add_question(question=question)
assert hivemind_issue.questions[0] == question

hivemind_issue.set_description(description=description)
assert hivemind_issue.description == description

hivemind_issue.set_answer_type(answer_type=option_type)
assert hivemind_issue.answer_type == option_type

hivemind_issue.set_tags(tags='mycompanyhash')
assert hivemind_issue.tags == 'mycompanyhash'

restrictions = {'addresses': [get_address_from_wallet(account=0, index=0), get_address_from_wallet(account=0, index=1)],
                'options_per_address': 10}
hivemind_issue.set_restrictions(restrictions=restrictions)


print ''
hivemind_issue_hash = hivemind_issue.save()
print 'Hivemind hash:', hivemind_issue_hash

hivemind_state = HivemindState()
hivemind_state.set_hivemind_issue(issue_hash=hivemind_issue_hash)

assert hivemind_state.options == []

option_hashes = {}
option_values = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten']
for option_value in option_values:
    print 'adding option %s' % option_value
    option = HivemindOption()
    option.set_hivemind_issue(hivemind_issue_hash=hivemind_issue_hash)
    option.answer_type = option_type
    option.set(value=option_value)
    option_hashes[option_value] = option.save()
    print 'saved with ipfs hash %s' % option.multihash()

    address = get_address_from_wallet(account=0, index=0)
    message = '/ipfs/%s' % option.multihash()
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
    signature = sign_message(private_key=get_private_key_from_wallet(account=3, index=i+1)[opinionator], message='/ipfs/%s' % opinion.multihash(), address=opinionator)
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
