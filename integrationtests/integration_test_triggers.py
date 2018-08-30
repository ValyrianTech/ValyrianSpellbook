#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from helpers.BIP44 import set_testnet
from helpers.configurationhelpers import get_use_testnet
from helpers.hotwallethelpers import get_address_from_wallet
from helpers.setupscripthelpers import spellbook_call

set_testnet(get_use_testnet())

print 'Starting Spellbook integration test: triggers'
print '----------------------------------------------\n'

trigger_types = ['Manual', 'Balance', 'Received', 'Sent', 'Block_height', 'Timestamp']

# --------------------------------------------------------------------------------------------------------
print 'Getting the list of configured triggers'
configured_triggers = spellbook_call('get_triggers')

if configured_triggers:
    print '--> Triggers found at beginning of test, deleting them before continuing'
    for trigger_id in configured_triggers:
        print '----> Get trigger config %s' % trigger_id
        response = spellbook_call('get_trigger_config', trigger_id)
        print '----> Deleting trigger %s' % trigger_id
        response = spellbook_call('delete_trigger', trigger_id)

    print '\nGetting the list of configured triggers, should be empty'
    response = spellbook_call('get_triggers')
    assert isinstance(response, list)
    assert len(response) == 0


for trigger_type in trigger_types:

    print '--------------------------------------------------------------------------------------------------------'
    print 'Saving trigger of type: %s' % trigger_type
    trigger_name = 'test_trigger_%s' % trigger_type

    response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type)
    assert response is None

    response = spellbook_call('get_trigger_config', trigger_name)
    assert response['trigger_id'] == trigger_name
    assert response['trigger_type'] == trigger_type
    print '--------------------------------------------------------------------------------------------------------'


for trigger_type in trigger_types:

    print '--------------------------------------------------------------------------------------------------------'
    print 'updating trigger of type: %s' % trigger_type
    trigger_name = 'test_trigger_%s' % trigger_type
    address = get_address_from_wallet(0, 3)
    amount = 1000000
    block_height = 480000
    timestamp = int(time.time()) + 10  # 10 seconds in the future

    response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '-a=%s' % address, '-b=%s' % block_height, '-am=%s' % amount, '-ts=%s' % timestamp)
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
    print '--------------------------------------------------------------------------------------------------------'


print '--------------------------------------------------------------------------------------------------------'
print 'Updating trigger test_trigger_Manual'
trigger_name = 'test_trigger_Manual'

description = 'A test description'
response = spellbook_call('save_trigger', trigger_name, '-d=%s' % description)
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['description'] == description

creator_name = 'Wouter Glorieux'
response = spellbook_call('save_trigger', trigger_name, '-cn=%s' % creator_name)
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['creator_name'] == creator_name

creator_email = 'info@valyrian.tech'
response = spellbook_call('save_trigger', trigger_name, '-ce=%s' % creator_email)
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['creator_email'] == creator_email

youtube = 'abcdefghijk'
response = spellbook_call('save_trigger', trigger_name, '-y=%s' % youtube)
assert response is None
response = spellbook_call('get_trigger_config', trigger_name)
assert response['youtube'] == youtube

for visibility in ['Private', 'Public']:
    response = spellbook_call('save_trigger', trigger_name, '-v=%s' % visibility)
    assert response is None
    response = spellbook_call('get_trigger_config', trigger_name)
    assert response['visibility'] == visibility

for status in ['Pending', 'Disabled', 'Active']:
    response = spellbook_call('save_trigger', trigger_name, '-st=%s' % status)
    assert response is None
    response = spellbook_call('get_trigger_config', trigger_name)
    assert response['status'] == status

# Activating test triggers
for trigger_type in trigger_types:
    print '--------------------------------------------------------------------------------------------------------'
    print 'activating trigger of type: %s' % trigger_type
    trigger_name = 'test_trigger_%s' % trigger_type

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
