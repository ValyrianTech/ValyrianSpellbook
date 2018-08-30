#!/usr/bin/env python
# -*- coding: utf-8 -*-
from helpers.setupscripthelpers import spellbook_call, clean_up_actions


print 'Starting Spellbook integration test: RevealSecret actions'
print '----------------------------------------------\n'

# Clean up actions if necessary
clean_up_actions(action_ids=['integrationtest_action_RevealSecret'])

#########################################################################################################
# RevealSecret actions
#########################################################################################################
action_name = 'integrationtest_action_RevealSecret'
reveal_text = 'A secret message'
reveal_link = 'http://www.asecretlink.com'

# --------------------------------------------------------------------------------------------------------

print 'Creating test action: RevealSecret'
response = spellbook_call('save_action', '-t=RevealSecret', action_name, '-rt=%s' % reveal_text, '-rl=%s' % reveal_link)
assert response is None

# --------------------------------------------------------------------------------------------------------
print 'Getting the list of configured action_ids'
response = spellbook_call('get_actions')
assert action_name in response

# --------------------------------------------------------------------------------------------------------
print 'Getting the action config of the action we just created'
response = spellbook_call('get_action_config', action_name)
assert response['id'] == action_name
assert response['action_type'] == 'RevealSecret'
assert response['reveal_text'] == reveal_text
assert response['reveal_link'] == reveal_link

# --------------------------------------------------------------------------------------------------------
print 'Checking if reveal is none because action has not been activated yet'
response = spellbook_call('get_reveal', action_name)
assert response is None

# --------------------------------------------------------------------------------------------------------
print 'Activating the action we just created'
response = spellbook_call('run_action', action_name)
assert response is True

# --------------------------------------------------------------------------------------------------------
print 'Checking if reveal is given because action has been activated'
response = spellbook_call('get_reveal', action_name)
assert response['reveal_text'] == reveal_text
assert response['reveal_link'] == reveal_link
