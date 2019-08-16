#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from helpers.setupscripthelpers import spellbook_call, clean_up_triggers


print('Starting Spellbook integration test: Timestamp trigger conditions')
print('----------------------------------------------\n')

# Clean up triggers if necessary
clean_up_triggers(trigger_ids=['test_trigger_conditions_TimestampTrigger'])

#########################################################################################################
# Timestamp trigger
#########################################################################################################
trigger_name = 'test_trigger_conditions_TimestampTrigger'
trigger_type = 'Timestamp'
timestamp = int(time.time()) + 5  # 5 seconds in the future

# ----------------------------------------------------------------------------------------------------------------------

response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '-ts=%s' % timestamp, '-st=Active')
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timestamp'] == timestamp
assert response['triggered'] == 0

print('Checking timestamp trigger, should not activate')
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timestamp'] == timestamp
assert response['triggered'] == 0

print('Sleeping 6 seconds...')
time.sleep(6)

print('Checking timestamp trigger again, should activate now')
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timestamp'] == timestamp
assert response['triggered'] == 1
