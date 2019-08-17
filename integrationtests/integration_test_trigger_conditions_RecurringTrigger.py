#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from helpers.setupscripthelpers import spellbook_call, clean_up_triggers


print('Starting Spellbook integration test: Recurring trigger conditions')
print('----------------------------------------------\n')

# Clean up triggers if necessary
clean_up_triggers(trigger_ids=['test_trigger_conditions_RecurringTrigger'])

#########################################################################################################
# Recurring trigger
#########################################################################################################
trigger_name = 'test_trigger_conditions_RecurringTrigger'
trigger_type = 'Recurring'
begin_time = int(time.time()) + 10  # 10 seconds in the future
end_time = int(time.time()) + 60  # 60 seconds in the future
interval = 10

# ----------------------------------------------------------------------------------------------------------------------

response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '-bt=%s' % begin_time, '-et=%s' % end_time, '-i=%s' % interval, '-st=Active')
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['begin_time'] == begin_time
assert response['end_time'] == end_time
assert response['interval'] == interval
assert response['next_activation'] == begin_time
assert response['triggered'] == 0

print('Checking recurring trigger, should not activate because begin time has not been reached')
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['begin_time'] == begin_time
assert response['next_activation'] == begin_time
assert response['triggered'] == 0

print('Sleeping until begin time has been reached')
while time.time() < begin_time:
    time.sleep(1)

print('Checking recurring trigger, should activate because begin time has been reached')
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['begin_time'] == begin_time
assert response['next_activation'] == begin_time + 10
assert response['triggered'] == 1

print('Checking recurring trigger again, should not activate because the next activation time has not been reached')
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['begin_time'] == begin_time
assert response['next_activation'] == begin_time + 10
assert response['triggered'] == 1


while int(time.time()) < end_time - 5:
    n_triggered = 1 + (int(time.time()) - begin_time) // interval
    print('Checking recurring trigger every few seconds')
    response = spellbook_call('check_triggers', trigger_name)
    assert response is None

    response = spellbook_call('get_trigger_config', trigger_name)
    assert response['trigger_type'] == trigger_type

    print('Number of times triggered should be %s now' % n_triggered)
    assert response['triggered'] == n_triggered

    time.sleep(3)

    response = spellbook_call('check_triggers', trigger_name)
    assert response is None

    response = spellbook_call('get_trigger_config', trigger_name)
    assert response['trigger_type'] == trigger_type

    print('Number of times triggered should be %s now' % n_triggered)
    assert response['triggered'] == n_triggered

    while time.time() < begin_time + n_triggered*interval:
        time.sleep(0.01)


print('Sleeping until end time has passed')
while time.time() <= end_time:
    time.sleep(1)

print('Checking recurring trigger again, triggered should not have increased since last activation')
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['triggered'] == (end_time - begin_time) // interval == n_triggered
