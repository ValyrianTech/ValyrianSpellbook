#!/usr/bin/env python
# -*- coding: utf-8 -*-
from helpers.setupscripthelpers import spellbook_call, clean_up_triggers


print 'Starting Spellbook integration test: Manual trigger conditions'
print '----------------------------------------------\n'

# Clean up triggers if necessary
clean_up_triggers(trigger_ids=['test_trigger_conditions_ManualTrigger'])


#########################################################################################################
# Manual trigger
#########################################################################################################
trigger_name = 'test_trigger_conditions_ManualTrigger'
trigger_type = 'Manual'

# -------------------------------------------------------------------------------------------------

print 'Creating Manual trigger'
response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '-st=Active')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 0
assert response['trigger_type'] == trigger_type

print 'Activating Manual trigger'
response = spellbook_call('activate_trigger', trigger_name)
assert response is None

print 'Checking if trigger has been triggered'
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 1
