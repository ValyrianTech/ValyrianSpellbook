#!/usr/bin/env python
# -*- coding: utf-8 -*-
from helpers.hotwallethelpers import get_address_from_wallet
from helpers.setupscripthelpers import spellbook_call, clean_up_triggers


print('Starting Spellbook integration test: Sent trigger conditions')
print('----------------------------------------------\n')

# Clean up triggers if necessary
clean_up_triggers(trigger_ids=['test_trigger_conditions_SentTrigger'])

#########################################################################################################
# Sent trigger
#########################################################################################################
trigger_name = 'test_trigger_conditions_SentTrigger'
trigger_type = 'Sent'

# ----------------------------------------------------------------------------------------------------------------------

account = 0
index = 0

address = get_address_from_wallet(account=account, index=index)
balance_data = spellbook_call('get_balance', address)
amount = balance_data['balance']['sent']


print('Creating Received trigger')

print('Setting trigger amount higher than current sent balance')
response = spellbook_call('save_trigger', '-t=%s' % trigger_type, trigger_name, '--reset', '-a=%s' % address, '-am=%s' % (amount + 1))
assert response is None

print('Checking if trigger has not been triggered yet')
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 0
assert response['address'] == address
assert response['amount'] == amount + 1

print('Check the conditions of the trigger')
response = spellbook_call('check_triggers', trigger_name)
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 0

print('Setting trigger amount equal to current sent balance')
response = spellbook_call('save_trigger', trigger_name, '--reset', '-am=%s' % amount)
assert response is None

print('Checking if trigger has not been triggered yet')
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 0
assert response['address'] == address
assert response['amount'] == amount

print('Check the conditions of the trigger')
response = spellbook_call('check_triggers', trigger_name)
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 1
