#!/usr/bin/env python
# -*- coding: utf-8 -*-
from helpers.setupscripthelpers import spellbook_call, clean_up_actions

print 'Starting Spellbook integration test: SpawnProcess actions'
print '----------------------------------------------\n'

#########################################################################################################
# SpawnProcess actions
#########################################################################################################

print 'Getting the list of configured actions'
configured_triggers = spellbook_call('get_actions')

action_name = 'integrationtest_action_SpawnProcess'

clean_up_actions(action_ids=[action_name])

# --------------------------------------------------------------------------------------------------------
# run_command = 'ping 127.0.0.1 > integrationtests/ping_output.txt'  # pipe output to file
run_command = 'ping 127.0.0.1'
print 'Creating test action: CommandAction'
response = spellbook_call('save_action', '-t=SpawnProcess', action_name, '-c=%s' % run_command)
assert response is None

# --------------------------------------------------------------------------------------------------------
print 'Getting the list of configured action_ids'
response = spellbook_call('get_actions')
assert action_name in response

# --------------------------------------------------------------------------------------------------------
print 'Getting the action config of the action we just created'
response = spellbook_call('get_action_config', action_name)
assert response['id'] == action_name
assert response['action_type'] == 'SpawnProcess'
assert response['run_command'] == run_command

# --------------------------------------------------------------------------------------------------------
print 'Running the action we just created'
response = spellbook_call('run_action', action_name)
assert response is True
