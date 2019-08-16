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

print('Sleeping 2 seconds...')
time.sleep(2)

while int(time.time()) < end_time - (interval/2):
    print('Checking recurring trigger each second')
    response = spellbook_call('check_triggers', trigger_name)
    assert response is None

    response = spellbook_call('get_trigger_config', trigger_name)
    assert response['trigger_type'] == trigger_type
    assert response['triggered'] == 0

    time.sleep(1)


print('Sleeping until end time has passed')
time.sleep(interval)

print('Checking recurring trigger again, triggered should be true')
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['triggered'] == 1  # todo check this
