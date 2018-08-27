#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import simplejson

from helpers.ipfshelpers import IPFS_API
from helpers.BIP44 import set_testnet
from helpers.configurationhelpers import get_use_testnet
from helpers.hotwallethelpers import get_address_from_wallet, get_private_key_from_wallet
from helpers.setupscripthelpers import spellbook_call
from sign_message import sign_message

set_testnet(get_use_testnet())

print 'Starting Spellbook integration test: SignedMessage trigger conditions'
print '----------------------------------------------\n'

#########################################################################################################
# SignedMessage trigger
#########################################################################################################

print 'Getting the list of configured triggers'
configured_triggers = spellbook_call('get_triggers')

trigger_name = 'test_trigger_conditions_SignedMessageTrigger'

# Clean up old test action if necessary
if trigger_name in configured_triggers:
    response = spellbook_call('delete_trigger', trigger_name)
    assert response is None

# --------------------------------------------------------------------------------------------------------
trigger_type = 'SignedMessage'


response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['triggered'] == 0
assert response['multi'] is False

print 'Checking SignedMessage trigger, should not activate'
response = spellbook_call('check_triggers', trigger_name)
assert response is None

account = 0
index = 0

address = get_address_from_wallet(account=account, index=index)
private_key = get_private_key_from_wallet(account=account, index=index)[address]
message = 'test message'

signature = sign_message(address=address, message=message, private_key=private_key)

print 'Sending a signed message'
response = spellbook_call('send_signed_message', trigger_name, address, message, signature)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['triggered'] > 0

print 'Sending a signed message again'
response = spellbook_call('send_signed_message', trigger_name, address, message, signature)
assert response is None

wrong_address = get_address_from_wallet(account=account, index=index+1)
response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '--reset', '-a=%s' % wrong_address)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['address'] == wrong_address
assert response['triggered'] == 0

print 'Sending a signed message again, but should not activate because the trigger is configured to only receive messages from another address'
response = spellbook_call('send_signed_message', trigger_name, address, message, signature)
assert 'error' in response

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['triggered'] == 0

print 'Resetting trigger and configuring it for the correct address'
response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '--reset', '-a=%s' % address)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['address'] == address
assert response['triggered'] == 0

print 'Sending a signed message'
response = spellbook_call('send_signed_message', trigger_name, address, message, signature)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['triggered'] > 0


# --------------------------------------------------------------------------------------------------------
print 'setting trigger and configuring it for any address and allow it to activate multiple times'
script = 'Template.py'
response = spellbook_call('save_trigger', trigger_name, '-t=%s' % trigger_type, '--reset', '-a=%s' % '', '--multi', '-sc=%s' % script)
assert response is None

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['address'] is None
assert response['triggered'] == 0
assert response['multi'] is True
assert response['script'] == script

print 'Sending a signed message first time'
response = spellbook_call('send_signed_message', trigger_name, address, message, signature)
assert response == {'status': 'success'}

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['triggered'] == 1

print 'Sending a signed message second time'
response = spellbook_call('send_signed_message', trigger_name, address, message, signature)
assert response == {'status': 'success'}

response = spellbook_call('get_trigger_config', trigger_name)
assert response['trigger_type'] == trigger_type
assert response['triggered'] == 2


# --------------------------------------------------------------------------------------------------------
print 'Sending IPFS hash as message'

multihash = IPFS_API.add_json({'address': address})

message = '/ipfs/%s' % multihash
signature = sign_message(address=address, message=message, private_key=private_key)

response = spellbook_call('send_signed_message', trigger_name, address, message, signature)
assert response == {'status': 'success'}

# --------------------------------------------------------------------------------------------------------
print 'Sending JSON data as message'
data = {'address': address}

filename = os.path.abspath('sample_json_data.json')

with open(filename, 'w') as output_file:
    message = simplejson.dumps(data, sort_keys=True, indent=None)
    output_file.write(message)

signature = sign_message(address=address, message=message, private_key=private_key)

response = spellbook_call('send_signed_message', trigger_name, address, filename, signature)
assert response == {'status': 'success'}
