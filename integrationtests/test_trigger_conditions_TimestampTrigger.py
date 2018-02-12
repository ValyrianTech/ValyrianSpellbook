#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from integration_test_helpers import spellbook_call


# Change working dir up one level
os.chdir("..")

print 'Starting Spellbook integration test: Timestamp trigger conditions'
print '----------------------------------------------\n'

#########################################################################################################
# Timestamp trigger
#########################################################################################################

print 'Getting the list of configured triggers'
configured_triggers = spellbook_call('get_triggers')

trigger_name = 'test_trigger_conditions_TimestampTrigger'

# Clean up old test action if necessary
if trigger_name in configured_triggers:
    response = spellbook_call('delete_trigger', trigger_name)
    assert response is None

# --------------------------------------------------------------------------------------------------------
trigger_type = 'Timestamp'
timestamp = int(time.time()) + 5  # 5 seconds in the future

response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '-ts=%s' % timestamp)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timestamp'] == timestamp
assert response['triggered'] is False

print 'Checking timestamp trigger, should not activate'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timestamp'] == timestamp
assert response['triggered'] is False

print 'Sleeping 6 seconds...'
time.sleep(6)

print 'Checking timestamp trigger again, should activate now'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timestamp'] == timestamp
assert response['triggered'] is True


