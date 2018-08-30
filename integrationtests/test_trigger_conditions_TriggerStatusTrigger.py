#!/usr/bin/env python
# -*- coding: utf-8 -*-
from helpers.setupscripthelpers import spellbook_call


print 'Starting Spellbook integration test: TriggerStatus trigger conditions'
print '----------------------------------------------\n'

#########################################################################################################
# TriggerStatus trigger
#########################################################################################################

print 'Getting the list of configured triggers'
configured_triggers = spellbook_call('get_triggers')

for trigger_name in ['test_trigger_conditions_TriggerStatusTrigger', 'test_trigger_conditions_TriggerStatusTrigger_A', 'test_trigger_conditions_TriggerStatusTrigger_B']:
    # Clean up old test triggers if necessary
    if trigger_name in configured_triggers:
        response = spellbook_call('delete_trigger', trigger_name)
        assert response is None

print 'Getting the list of configured actions'
configured_actions = spellbook_call('get_actions')

for action_name in ['test_triggerstatus_action']:
    # Clean up old test action if necessary
    if action_name in configured_actions:
        response = spellbook_call('delete_action', action_name)
        assert response is None

# --------------------------------------------------------------------------------------------------------

print 'Creating previous trigger with webhook action'
previous_trigger = 'test_trigger_conditions_TriggerStatusTrigger_A'
previous_trigger_status = 'Succeeded'
previous_trigger_type = 'Manual'


response = spellbook_call('save_trigger', previous_trigger, '-t=%s' % previous_trigger_type, '-st=Active')
assert response is None

action_name = 'test_triggerstatus_action'
webhook = 'http://www.google.com'

response = spellbook_call('save_action', action_name, '-t=Webhook', '-w=%s' % webhook)
assert response is None

response = spellbook_call('save_trigger', previous_trigger, '--actions', 'test_triggerstatus_action')
assert response is None


print 'Creating the test TriggerStatus trigger'
trigger_name = 'test_trigger_conditions_TriggerStatusTrigger'
trigger_type = 'TriggerStatus'

response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '-pt=%s' % previous_trigger, '-pts=%s' % previous_trigger_status, '-st=Active')
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['previous_trigger'] == previous_trigger
assert response['previous_trigger_status'] == previous_trigger_status
assert response['triggered'] == 0

print 'Checking TriggerStatus trigger, should not trigger because the previous trigger has not been activated yet'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 0


# --------------------------------------------------------------------------------------------------------

print 'Activate the previous trigger'
response = spellbook_call('activate_trigger', previous_trigger)
assert response is None

print 'Checking TriggerStatus trigger, should trigger now because previous trigger succeeded'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 1

# --------------------------------------------------------------------------------------------------------

print 'Resetting triggers'

response = spellbook_call('save_trigger', previous_trigger, '--reset')
assert response is None

response = spellbook_call('get_trigger_config', previous_trigger)
assert response['triggered'] == 0
assert response['status'] == 'Active'

response = spellbook_call('save_trigger', trigger_name, '--reset')
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 0
assert response['status'] == 'Active'


print 'Changing webhook action so it will fail the next time'
webhook = 'http://www.qsdfqeqessefeddsdfsfe.com'

response = spellbook_call('save_action', action_name, '-t=Webhook', '-w=%s' % webhook)
assert response is None

# --------------------------------------------------------------------------------------------------------

print 'Activate the previous trigger'
response = spellbook_call('activate_trigger', previous_trigger)
assert response is None

print 'Checking TriggerStatus trigger, should not trigger because previous trigger failed'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 0

# --------------------------------------------------------------------------------------------------------

print 'Changing previous_trigger_status to Failed'
previous_trigger_status = 'Failed'
response = spellbook_call('save_trigger', trigger_name, '-pts=%s' % previous_trigger_status)
assert response is None

print 'Checking TriggerStatus trigger, should trigger because previous trigger failed'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 1
