#!/usr/bin/env python
from helpers.setupscripthelpers import (
    clean_up_actions,
    clean_up_triggers,
    spellbook_call,
)

print('Starting Spellbook integration test: trigger with actions')
print('----------------------------------------------\n')

# Clean up triggers if necessary
clean_up_triggers(trigger_ids=['test_trigger_with_actions'])

# Clean up actions if necessary
clean_up_actions(action_ids=['test_trigger_action1', 'test_trigger_action2', 'test_trigger_action3', 'test_trigger_action4'])

#########################################################################################################
# Trigger with actions
#########################################################################################################
trigger_name = 'test_trigger_with_actions'
trigger_type = 'Manual'

# --------------------------------------------------------------------------------------------------------

print(f'Saving trigger of type: {trigger_type}')

response = spellbook_call('save_trigger', trigger_name, f'-t={trigger_type}')
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_id'] == trigger_name
assert response['trigger_type'] == trigger_type
assert response['actions'] == []

# --------------------------------------------------------------------------------------------------------

print('adding non-existing action to trigger')

response = spellbook_call('save_trigger', trigger_name, '--actions', 'test_trigger_action1', 'test_trigger_action2')
assert response is None

print('adding test actions')
print('Creating test action: test_trigger_action1')
action_name = 'test_trigger_action1'
run_command = 'echo Hello world!'

response = spellbook_call('save_action', '-t=Command', action_name, f'-c={run_command}')
assert response is None


print('Creating test action: test_trigger_action2')
action_name = 'test_trigger_action2'
webhook = 'http://www.google.com'

print('Creating test action: Webhook')
response = spellbook_call('save_action', '-t=Webhook', action_name, f'-w={webhook}')
assert response is None

# --------------------------------------------------------------------------------------------------------

response = spellbook_call('save_trigger', trigger_name, '--actions', 'test_trigger_action1', 'test_trigger_action2', 'test_trigger_action3')
assert response is None

print('Activating trigger, should fail because of unknown action test_trigger_action3')
response = spellbook_call('activate_trigger', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 0


# --------------------------------------------------------------------------------------------------------
action_name = 'test_trigger_action3'
reveal_text = 'A secret message'
reveal_link = 'http://www.asecretlink.com'

print('Creating test action: test_trigger_action3')
response = spellbook_call('save_action', '-t=RevealSecret', action_name, f'-rt={reveal_text}', f'-rl={reveal_link}')
assert response is None

print('Activating trigger, should fail because of unknown action test_trigger_action3')
response = spellbook_call('activate_trigger', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 1

# --------------------------------------------------------------------------------------------------------

print('Resetting trigger')
response = spellbook_call('save_trigger', trigger_name, '--reset')
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 0

print('Modifying test action: test_trigger_action2 with a bad webhook so it will fail when run')
action_name = 'test_trigger_action2'
webhook = 'http://www.aerqdsfqeqfdsqsdfqesfsfqqeqfqef.com'

response = spellbook_call('save_action', action_name, f'-w={webhook}')
assert response is None

print('Activating trigger, should fail because of bad webhook in test_trigger_action2')
response = spellbook_call('activate_trigger', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['status'] == 'Failed'
