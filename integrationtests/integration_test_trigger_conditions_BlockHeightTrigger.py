#!/usr/bin/env python
# -*- coding: utf-8 -*-
from helpers.setupscripthelpers import spellbook_call, clean_up_triggers


print 'Starting Spellbook integration test: BlockHeight trigger conditions'
print '----------------------------------------------\n'

# Clean up triggers if necessary
clean_up_triggers(trigger_ids=['test_trigger_conditions_BlockHeightTrigger'])

#########################################################################################################
# Blockheight trigger
#########################################################################################################
trigger_name = 'test_trigger_conditions_BlockHeightTrigger'
trigger_type = 'Block_height'

# -------------------------------------------------------------------------------------------------

print 'Creating Block_height trigger'

response = spellbook_call('get_latest_block')
latest_block_height = response['block']['height']
assert isinstance(latest_block_height, int) and latest_block_height > 0

print 'set block_height to 1 block in the future and 0 conditions, this should not trigger yet'
response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '-b=%d' % (latest_block_height + 1), '-c=0', '-st=Active')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 0
assert response['trigger_type'] == trigger_type

print 'Check the conditions of the trigger'
response = spellbook_call('check_triggers', trigger_name)
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 0

print 'set block_height to current block_height and 0 confirmations, this should trigger'
response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '-b=%d' % latest_block_height, '-c=0', '--reset')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 0

print 'Check the conditions of the trigger'
response = spellbook_call('check_triggers', trigger_name)
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 1

print 'set block_height to 3 blocks in the past and 6 confirmations, this should not trigger'
response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '-b=%d' % (latest_block_height - 3), '-c=6', '--reset')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 0

print 'Check the conditions of the trigger'
response = spellbook_call('check_triggers', trigger_name)
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 0

print 'set block_height to 3 blocks in the past and 3 confirmations, this should trigger'
response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '-b=%d' % (latest_block_height - 3), '-c=3', '--reset')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 0

print 'Check the conditions of the trigger'
response = spellbook_call('check_triggers', trigger_name)
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['triggered'] == 1
