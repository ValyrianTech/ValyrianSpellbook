#!/usr/bin/env python
import time

from helpers.hotwallethelpers import get_address_from_wallet
from helpers.setupscripthelpers import clean_up_triggers, spellbook_call

print('Starting Spellbook integration test: triggers')
print('----------------------------------------------\n')

# Clean up triggers if necessary
clean_up_triggers(trigger_ids=['test_trigger_Manual',
                               'test_trigger_Balance',
                               'test_trigger_Received',
                               'test_trigger_Sent',
                               'test_trigger_Block_height',
                               'test_trigger_Timestamp'])

# --------------------------------------------------------------------------------------------------------

trigger_types = ['Manual', 'Balance', 'Received', 'Sent', 'Block_height', 'Timestamp']

for trigger_type in trigger_types:

    print('--------------------------------------------------------------------------------------------------------')
    print(f'Saving trigger of type: {trigger_type}')
    trigger_name = f'test_trigger_{trigger_type}'

    response = spellbook_call('save_trigger', trigger_name, f'-t={trigger_type}')
    assert response is None

    response = spellbook_call('get_trigger_config', trigger_name)
    assert response['trigger_id'] == trigger_name
    assert response['trigger_type'] == trigger_type
    print('--------------------------------------------------------------------------------------------------------')


for trigger_type in trigger_types:

    print('--------------------------------------------------------------------------------------------------------')
    print(f'updating trigger of type: {trigger_type}')
    trigger_name = f'test_trigger_{trigger_type}'
    address = get_address_from_wallet(0, 3)
    amount = 1000000
    block_height = 480000
    timestamp = int(time.time()) + 10  # 10 seconds in the future

    response = spellbook_call('save_trigger', trigger_name, f'-t={trigger_type}', f'-a={address}', f'-b={block_height}', f'-am={amount}', f'-ts={timestamp}')
    assert response is None

    response = spellbook_call('get_trigger_config', trigger_name)
    assert response['trigger_id'] == trigger_name
    assert response['trigger_type'] == trigger_type

    if trigger_type in ['Balance', 'Received', 'Sent']:
        assert response['address'] == address
        assert response['amount'] == amount
    elif trigger_type == 'Block_height':
        assert response['block_height'] == block_height
    elif trigger_type == 'Timestamp':
        assert response['timestamp'] == timestamp
    print('--------------------------------------------------------------------------------------------------------')


print('--------------------------------------------------------------------------------------------------------')
print('Updating trigger test_trigger_Manual')
trigger_name = 'test_trigger_Manual'

description = 'A test description'
response = spellbook_call('save_trigger', trigger_name, f'-d={description}')
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['description'] == description

creator_name = 'Wouter Glorieux'
response = spellbook_call('save_trigger', trigger_name, f'-cn={creator_name}')
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['creator_name'] == creator_name

creator_email = 'someone@example.com'
response = spellbook_call('save_trigger', trigger_name, f'-ce={creator_email}')
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['creator_email'] == creator_email

youtube = 'abcdefghijk'
response = spellbook_call('save_trigger', trigger_name, f'-y={youtube}')
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['youtube'] == youtube

for visibility in ['Private', 'Public']:
    response = spellbook_call('save_trigger', trigger_name, f'-v={visibility}')
    assert response is None
    response = spellbook_call('get_trigger_config', trigger_name)
    assert response['visibility'] == visibility

for status in ['Pending', 'Disabled', 'Active']:
    response = spellbook_call('save_trigger', trigger_name, f'-st={status}')
    assert response is None
    response = spellbook_call('get_trigger_config', trigger_name)
    assert response['status'] == status

# Activating test triggers
for trigger_type in trigger_types:
    print('--------------------------------------------------------------------------------------------------------')
    print(f'activating trigger of type: {trigger_type}')
    trigger_name = f'test_trigger_{trigger_type}'

    response = spellbook_call('get_trigger_config', trigger_name)
    assert response['triggered'] == 0

    response = spellbook_call('activate_trigger', trigger_name)
    if trigger_type == 'Manual':
        assert response is None
        response = spellbook_call('get_trigger_config', trigger_name)
        assert response['triggered'] == 1

        # Reset trigger
        spellbook_call('save_trigger', trigger_name, '--reset')
        response = spellbook_call('get_trigger_config', trigger_name)
        assert response['triggered'] == 0

    else:
        assert 'error' in response
        response = spellbook_call('get_trigger_config', trigger_name)
        assert response['triggered'] == 0
