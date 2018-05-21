#!/usr/bin/env python
# -*- coding: utf-8 -*-

from integration_test_helpers import spellbook_call

print 'Starting Spellbook integration test: trigger conditions'
print '----------------------------------------------\n'

# -------------------------------------------------------------------------------------------------
print 'Creating Manual trigger'
response = spellbook_call('save_trigger', 'test_conditions_Manual', '-t=Manual', '--reset')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', 'test_conditions_Manual')
assert response['triggered'] is False

print 'Activating Manual trigger'
response = spellbook_call('activate_trigger', 'test_conditions_Manual')
assert response is None

print 'Checking if trigger has been triggered'
response = spellbook_call('get_trigger_config', 'test_conditions_Manual')
assert response['triggered'] is True


# -------------------------------------------------------------------------------------------------
print 'Creating Block_height trigger'

response = spellbook_call('get_latest_block')
latest_block_height = response['block']['height']
assert isinstance(latest_block_height, int) and latest_block_height > 0

print 'set block_height to 1 block in the future and 0 conditions, this should not trigger yet'
response = spellbook_call('save_trigger', 'test_conditions_Block_height', '-t=Block_height', '-b=%d' % (latest_block_height + 1), '-c=0', '--reset')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', 'test_conditions_Block_height')
assert response['triggered'] is False

print 'Check the conditions of the trigger'
response = spellbook_call('check_triggers', 'test_conditions_Block_height')
assert response is None
response = spellbook_call('get_trigger_config', 'test_conditions_Block_height')
assert response['triggered'] is False

print 'set block_height to current block_height and 0 confirmations, this should trigger'
response = spellbook_call('save_trigger', 'test_conditions_Block_height', '-t=Block_height', '-b=%d' % latest_block_height, '-c=0', '--reset')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', 'test_conditions_Block_height')
assert response['triggered'] is False

print 'Check the conditions of the trigger'
response = spellbook_call('check_triggers', 'test_conditions_Block_height')
assert response is None
response = spellbook_call('get_trigger_config', 'test_conditions_Block_height')
assert response['triggered'] is True

print 'set block_height to 3 blocks in the past and 6 confirmations, this should not trigger'
response = spellbook_call('save_trigger', 'test_conditions_Block_height', '-t=Block_height', '-b=%d' % (latest_block_height - 3), '-c=6', '--reset')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', 'test_conditions_Block_height')
assert response['triggered'] is False

print 'Check the conditions of the trigger'
response = spellbook_call('check_triggers', 'test_conditions_Block_height')
assert response is None
response = spellbook_call('get_trigger_config', 'test_conditions_Block_height')
assert response['triggered'] is False

print 'set block_height to 3 blocks in the past and 3 confirmations, this should trigger'
response = spellbook_call('save_trigger', 'test_conditions_Block_height', '-t=Block_height', '-b=%d' % (latest_block_height - 3), '-c=3', '--reset')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', 'test_conditions_Block_height')
assert response['triggered'] is False

print 'Check the conditions of the trigger'
response = spellbook_call('check_triggers', 'test_conditions_Block_height')
assert response is None
response = spellbook_call('get_trigger_config', 'test_conditions_Block_height')
assert response['triggered'] is True

# ----------------------------------------------------------------------------------------------------------------------

print 'Creating Balance trigger'

print 'Setting trigger amount higher than current balance'
response = spellbook_call('save_trigger', '-t=Balance', 'test_conditions_Balance', '--reset', '-a=1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8', '-am=10000')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', 'test_conditions_Balance')
assert response['triggered'] is False

print 'Check the conditions of the trigger'
response = spellbook_call('check_triggers', 'test_conditions_Balance')
assert response is None
response = spellbook_call('get_trigger_config', 'test_conditions_Balance')
assert response['triggered'] is False

print 'Setting trigger amount equal to current balance'
response = spellbook_call('save_trigger', 'test_conditions_Balance', '--reset', '-am=7315')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', 'test_conditions_Balance')
assert response['triggered'] is False

print 'Check the conditions of the trigger'
response = spellbook_call('check_triggers', 'test_conditions_Balance')
assert response is None
response = spellbook_call('get_trigger_config', 'test_conditions_Balance')
assert response['triggered'] is True


# ----------------------------------------------------------------------------------------------------------------------

print 'Creating Received trigger'

print 'Setting trigger amount higher than current total received'
response = spellbook_call('save_trigger', '-t=Received', 'test_conditions_Received', '--reset', '-a=1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8', '-am=1000001')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', 'test_conditions_Received')
assert response['triggered'] is False

print 'Check the conditions of the trigger'
response = spellbook_call('check_triggers', 'test_conditions_Received')
assert response is None
response = spellbook_call('get_trigger_config', 'test_conditions_Received')
assert response['triggered'] is False

print 'Setting trigger amount equal to total received'
response = spellbook_call('save_trigger', 'test_conditions_Received', '--reset', '-am=1000000')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', 'test_conditions_Received')
assert response['triggered'] is False

print 'Check the conditions of the trigger'
response = spellbook_call('check_triggers', 'test_conditions_Received')
assert response is None
response = spellbook_call('get_trigger_config', 'test_conditions_Received')
assert response['triggered'] is True



# ----------------------------------------------------------------------------------------------------------------------

print 'Creating Sent trigger'

print 'Setting trigger amount higher than current total sent'
response = spellbook_call('save_trigger', '-t=Sent', 'test_conditions_Sent', '--reset', '-a=1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8', '-am=1000001')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', 'test_conditions_Sent')
assert response['triggered'] is False

print 'Check the conditions of the trigger'
response = spellbook_call('check_triggers', 'test_conditions_Sent')
assert response is None
response = spellbook_call('get_trigger_config', 'test_conditions_Sent')
assert response['triggered'] is False

print 'Setting trigger amount less than total sent'
response = spellbook_call('save_trigger', 'test_conditions_Sent', '--reset', '-am=900000')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', 'test_conditions_Sent')
assert response['triggered'] is False

print 'Check the conditions of the trigger'
response = spellbook_call('check_triggers', 'test_conditions_Sent')
assert response is None
response = spellbook_call('get_trigger_config', 'test_conditions_Sent')
assert response['triggered'] is True

# ----------------------------------------------------------------------------------------------------------------------

print 'cleaning up...'
response = spellbook_call('delete_trigger', 'test_conditions_Manual')
assert response is None

response = spellbook_call('delete_trigger', 'test_conditions_Block_height')
assert response is None

response = spellbook_call('delete_trigger', 'test_conditions_Balance')
assert response is None

response = spellbook_call('delete_trigger', 'test_conditions_Received')
assert response is None

response = spellbook_call('delete_trigger', 'test_conditions_Sent')
assert response is None