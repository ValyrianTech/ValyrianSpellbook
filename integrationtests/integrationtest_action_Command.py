#!/usr/bin/env python
# -*- coding: utf-8 -*-
from helpers.setupscripthelpers import spellbook_call, clean_up_actions


print 'Starting Spellbook integration test: Command actions'
print '----------------------------------------------\n'

# Clean up actions if necessary
clean_up_actions(action_ids=['integrationtest_action_Command'])

#########################################################################################################
# Command actions
#########################################################################################################
action_name = 'integrationtest_action_Command'
run_command = 'echo Hello world!'

# --------------------------------------------------------------------------------------------------------

print 'Creating test action: CommandAction'
response = spellbook_call('save_action', '-t=Command', action_name, '-c=%s' % run_command)
assert response is None

# --------------------------------------------------------------------------------------------------------
print 'Getting the list of configured action_ids'
response = spellbook_call('get_actions')
assert action_name in response

# --------------------------------------------------------------------------------------------------------
print 'Getting the action config of the action we just created'
response = spellbook_call('get_action_config', action_name)
assert response['id'] == action_name
assert response['action_type'] == 'Command'
assert response['run_command'] == run_command

# --------------------------------------------------------------------------------------------------------
print 'Running the action we just created'
response = spellbook_call('run_action', action_name)
assert response is True
