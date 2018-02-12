#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from integration_test_helpers import spellbook_call


# Change working dir up one level
os.chdir("..")

print 'Starting Spellbook integration test: BlockHeight trigger conditions'
print '----------------------------------------------\n'

#########################################################################################################
# Blockheight trigger
#########################################################################################################

print 'Getting the list of configured triggers'
configured_triggers = spellbook_call('get_triggers')

trigger_name = 'test_trigger_conditions_BlockHeightTrigger'

# Clean up old test action if necessary
if trigger_name in configured_triggers:
    response = spellbook_call('delete_trigger', trigger_name)
    assert response is None

# --------------------------------------------------------------------------------------------------------
trigger_type = 'Block_height'
# -------------------------------------------------------------------------------------------------
print 'Creating Block_height trigger'

response = spellbook_call('get_latest_block')
latest_block_height = response['block']['height']
assert isinstance(latest_block_height, int) and latest_block_height > 0

print 'set block_height to 1 block in the future and 0 conditions, this should not trigger yet'
response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '-b=%d' % (latest_block_height + 1), '-c=0', '--reset')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] is False
assert response['trigger_type'] == trigger_type

print 'Check the conditions of the trigger'
response = spellbook_call('check_triggers', trigger_name)
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] is False

print 'set block_height to current block_height and 0 confirmations, this should trigger'
response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '-b=%d' % latest_block_height, '-c=0', '--reset')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] is False

print 'Check the conditions of the trigger'
response = spellbook_call('check_triggers', trigger_name)
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] is True

print 'set block_height to 3 blocks in the past and 6 confirmations, this should not trigger'
response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '-b=%d' % (latest_block_height - 3), '-c=6', '--reset')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] is False

print 'Check the conditions of the trigger'
response = spellbook_call('check_triggers', trigger_name)
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] is False

print 'set block_height to 3 blocks in the past and 3 confirmations, this should trigger'
response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '-b=%d' % (latest_block_height - 3), '-c=3', '--reset')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] is False

print 'Check the conditions of the trigger'
response = spellbook_call('check_triggers', trigger_name)
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] is True
