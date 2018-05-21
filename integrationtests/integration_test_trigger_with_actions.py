#!/usr/bin/env python
# -*- coding: utf-8 -*-

from integration_test_helpers import spellbook_call

print 'Starting Spellbook integration test: trigger with actions'
print '----------------------------------------------\n'


print 'Getting the list of configured triggers'
configured_triggers = spellbook_call('get_triggers')

trigger_name = 'test_trigger_with_actions'

# Clean up old test trigger if necessary
if trigger_name in configured_triggers:
    response = spellbook_call('delete_trigger', trigger_name)
    assert response is None


print 'Getting the list of configured actions'
configured_actions = spellbook_call('get_actions')

for action_name in ['test_trigger_action1', 'test_trigger_action2', 'test_trigger_action3', 'test_trigger_action4']:
    # Clean up old test action if necessary
    if action_name in configured_actions:
        response = spellbook_call('delete_action', action_name)
        assert response is None

# --------------------------------------------------------------------------------------------------------
trigger_type = 'Manual'
print 'Saving trigger of type: %s' % trigger_type

response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['id'] == trigger_name
assert response['trigger_type'] == trigger_type
assert response['actions'] == []

# --------------------------------------------------------------------------------------------------------
print 'adding non-existing action to trigger'

response = spellbook_call('save_trigger', trigger_name, '--actions', 'test_trigger_action1', 'test_trigger_action2')
assert response is None

print 'adding test actions'
print 'Creating test action: test_trigger_action1'
action_name = 'test_trigger_action1'
run_command = 'ping 127.0.0.1 > integrationtests/ping_output.txt'

response = spellbook_call('save_action', '-t=Command', action_name, '-c=%s' % run_command)
assert response is None


print 'Creating test action: test_trigger_action2'
action_name = 'test_trigger_action2'
webhook = 'http://www.google.com'

print 'Creating test action: Webhook'
response = spellbook_call('save_action', '-t=Webhook', action_name, '-w=%s' % webhook)
assert response is None

# --------------------------------------------------------------------------------------------------------

response = spellbook_call('save_trigger', trigger_name, '--actions', 'test_trigger_action1', 'test_trigger_action2', 'test_trigger_action3')
assert response is None

print 'Activating trigger, should fail because of unknown action test_trigger_action3'
response = spellbook_call('activate_trigger', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] is False


# --------------------------------------------------------------------------------------------------------
action_name = 'test_trigger_action3'
reveal_text = 'A secret message'
reveal_link = 'http://www.asecretlink.com'

print 'Creating test action: test_trigger_action3'
response = spellbook_call('save_action', '-t=RevealSecret', action_name, '-rt=%s' % reveal_text, '-rl=%s' % reveal_link)
assert response is None

print 'Activating trigger, should fail because of unknown action test_trigger_action3'
response = spellbook_call('activate_trigger', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] is True

# --------------------------------------------------------------------------------------------------------

print 'Resetting trigger'
response = spellbook_call('save_trigger', trigger_name, '--reset')
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] is False

print 'Modifying test action: test_trigger_action2 with a bad webhook so it will fail when run'
action_name = 'test_trigger_action2'
webhook = 'http://www.aerqdsfqeqfdsqsdfqesfsfqqeqfqef.com'

response = spellbook_call('save_action', action_name, '-w=%s' % webhook)
assert response is None

print 'Activating trigger, should fail because of bad webhook in test_trigger_action2'
response = spellbook_call('activate_trigger', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] is False














