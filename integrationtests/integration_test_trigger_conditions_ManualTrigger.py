#!/usr/bin/env python
# -*- coding: utf-8 -*-
from helpers.setupscripthelpers import spellbook_call


print 'Starting Spellbook integration test: Manual trigger conditions'
print '----------------------------------------------\n'

#########################################################################################################
# Manual trigger
#########################################################################################################

print 'Getting the list of configured triggers'
configured_triggers = spellbook_call('get_triggers')

trigger_name = 'test_trigger_conditions_ManualTrigger'

# Clean up old test action if necessary
if trigger_name in configured_triggers:
    response = spellbook_call('delete_trigger', trigger_name)
    assert response is None

# --------------------------------------------------------------------------------------------------------
trigger_type = 'Manual'
# -------------------------------------------------------------------------------------------------
print 'Creating Manual trigger'
response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '--reset')
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
