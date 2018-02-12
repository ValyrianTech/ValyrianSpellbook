#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from integration_test_helpers import spellbook_call


# Change working dir up one level
os.chdir("..")

print 'Starting Spellbook integration test: Recurring trigger conditions'
print '----------------------------------------------\n'

#########################################################################################################
# Recurring trigger
#########################################################################################################

print 'Getting the list of configured triggers'
configured_triggers = spellbook_call('get_triggers')

trigger_name = 'test_trigger_conditions_RecurringTrigger'

# Clean up old test action if necessary
if trigger_name in configured_triggers:
    response = spellbook_call('delete_trigger', trigger_name)
    assert response is None

# --------------------------------------------------------------------------------------------------------
trigger_type = 'Recurring'
begin_time = int(time.time()) + 10  # 10 seconds in the future
end_time = int(time.time()) + 60  # 60 seconds in the future
interval = 10

response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '-bt=%s' % begin_time, '-et=%s' % end_time, '-i=%s' % interval)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['begin_time'] == begin_time
assert response['end_time'] == end_time
assert response['interval'] == interval
assert response['next_activation'] == begin_time
assert response['triggered'] is False

print 'Checking recurring trigger, should not activate because begin time has not been reached'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['begin_time'] == begin_time
assert response['next_activation'] == begin_time
assert response['triggered'] is False

print 'Sleeping 5 seconds...'
time.sleep(5)

while int(time.time()) < end_time - (interval/2):
    print 'Checking recurring trigger each second'
    response = spellbook_call('check_triggers', trigger_name)
    assert response is None

    response = spellbook_call('get_trigger_config', trigger_name)
    assert response['trigger_type'] == trigger_type
    assert response['triggered'] is False

    time.sleep(1)


print 'Sleeping until end time has passed'
time.sleep(interval)

print 'Checking recurring trigger again, triggered should be true'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['triggered'] is True