#!/usr/bin/env python
# -*- coding: utf-8 -*-
from helpers.setupscripthelpers import spellbook_call, clean_up_actions


print('Starting Spellbook integration test: Webhook actions')
print('----------------------------------------------\n')

# Clean up actions if necessary
clean_up_actions(action_ids=['integrationtest_action_Webhook'])

#########################################################################################################
# Webhook actions
#########################################################################################################
action_name = 'integrationtest_action_Webhook'
webhook = 'http://www.google.com'

# --------------------------------------------------------------------------------------------------------

print('Creating test action: Webhook')
response = spellbook_call('save_action', '-t=Webhook', action_name, '-w=%s' % webhook)
assert response is None

# --------------------------------------------------------------------------------------------------------
print('Getting the list of configured action_ids')
response = spellbook_call('get_actions')
assert action_name in response

# --------------------------------------------------------------------------------------------------------
print('Getting the action config of the action we just created')
response = spellbook_call('get_action_config', action_name)
assert response['id'] == action_name
assert response['action_type'] == 'Webhook'
assert response['webhook'] == webhook

# --------------------------------------------------------------------------------------------------------
print('Running the action we just created')
response = spellbook_call('run_action', action_name)
assert response is True

# --------------------------------------------------------------------------------------------------------
webhook = 'http://www.erzraezrozoerijfosqjdfiosqijioefoe.com'
response = spellbook_call('save_action', '-t=Webhook', action_name, '-w=%s' % webhook)
assert response is None

response = spellbook_call('get_action_config', action_name)
assert response['id'] == action_name
assert response['action_type'] == 'Webhook'
assert response['webhook'] == webhook

print('Running the action with a bad url')
response = spellbook_call('run_action', action_name)
assert response is False
