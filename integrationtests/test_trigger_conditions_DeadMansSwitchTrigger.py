#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from integration_test_helpers import spellbook_call


# Change working dir up one level
os.chdir("..")

print 'Starting Spellbook integration test: DeadMansSwitch trigger conditions'
print '----------------------------------------------\n'

#########################################################################################################
# DeadMansSwitch trigger
#########################################################################################################

print 'Getting the list of configured triggers'
configured_triggers = spellbook_call('get_triggers')

trigger_name = 'test_trigger_conditions_DeadMansSwitchTrigger'

# Clean up old test action if necessary
if trigger_name in configured_triggers:
    response = spellbook_call('delete_trigger', trigger_name)
    assert response is None

# --------------------------------------------------------------------------------------------------------
trigger_type = 'DeadMansSwitch'
timeout = 60  # 60 seconds
warning_email = 'skidzobolder@gmail.com'

response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '-ti=%s' % timeout, '-we=%s' % warning_email)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timeout'] == timeout
assert response['warning_email'] == warning_email
assert response['triggered'] is False

print 'Checking DeadMansSwitch trigger, should not activate'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timeout'] == timeout
assert response['triggered'] is False
assert response['phase'] == 0

print 'Sleeping %s seconds...' % timeout
time.sleep(timeout)

print 'Checking DeadMansSwitch trigger, should not activate because it has not been armed yet'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timeout'] == timeout
assert response['triggered'] is False
assert response['phase'] == 0
assert response['activation_time'] is None


# --------------------------------------------------------------------------------------------------------
print 'Arming DeadMansSwitch'
response = spellbook_call('activate_trigger', trigger_name)
assert response is None
activation_time = int(time.time()) + timeout

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timeout'] == timeout
assert response['phase'] == 1
assert response['activation_time'] == activation_time

# --------------------------------------------------------------------------------------------------------

time.sleep(timeout * 0.5)

print 'First check, phase should now be 2'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timeout'] == timeout
assert response['triggered'] is False
assert response['phase'] == 2

# --------------------------------------------------------------------------------------------------------

time.sleep(timeout * 0.25)

print 'second check, phase should now be 3'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timeout'] == timeout
assert response['triggered'] is False
assert response['phase'] == 3

# --------------------------------------------------------------------------------------------------------

time.sleep(timeout * 0.15)

print 'third check, phase should now be 4'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timeout'] == timeout
assert response['triggered'] is False
assert response['phase'] == 4

# --------------------------------------------------------------------------------------------------------
print 'Fourth check, phase should now be 4, but will not activate yet because activation time has not been reached yet'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timeout'] == timeout
assert response['triggered'] is False
assert response['phase'] == 4

# --------------------------------------------------------------------------------------------------------
print 'Resetting trigger, phase should be back to 1 and activation time pushed back'
response = spellbook_call('save_trigger', trigger_name, '--reset')
assert response is None
new_activation_time = int(time.time()) + timeout

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timeout'] == timeout
assert response['triggered'] is False
assert response['phase'] == 1
assert response['activation_time'] == new_activation_time


# --------------------------------------------------------------------------------------------------------

time.sleep(timeout * 0.5)
print 'First check, phase should now be 2'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timeout'] == timeout
assert response['triggered'] is False
assert response['phase'] == 2

# --------------------------------------------------------------------------------------------------------
time.sleep(timeout * 0.25)
print 'second check, phase should now be 3'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timeout'] == timeout
assert response['triggered'] is False
assert response['phase'] == 3

# --------------------------------------------------------------------------------------------------------
time.sleep(timeout * 0.15)
print 'third check, phase should now be 4'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timeout'] == timeout
assert response['triggered'] is False
assert response['phase'] == 4

# --------------------------------------------------------------------------------------------------------
print 'Fourth check, phase should now be 4, but will not activate yet because activation time has not been reached yet'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timeout'] == timeout
assert response['triggered'] is False
assert response['phase'] == 4


# --------------------------------------------------------------------------------------------------------
print 'Sleeping until activation time has been reached'
time.sleep(timeout * 0.2)

print 'Final check, phase should now be 5, and should activate'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['timeout'] == timeout
assert response['triggered'] is True
assert response['phase'] == 5












