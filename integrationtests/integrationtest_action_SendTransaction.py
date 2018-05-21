#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from helpers.BIP44 import set_testnet
from helpers.configurationhelpers import get_use_testnet
from helpers.hotwallethelpers import get_address_from_wallet, get_xpub_key_from_wallet
from integration_test_helpers import spellbook_call

# Change working dir up one level
os.chdir("..")

set_testnet(get_use_testnet())

print 'Starting Spellbook integration test: SendTransaction action'
print '----------------------------------------------\n'

#########################################################################################################
# SendTransaction actions
#########################################################################################################

print 'Getting the list of configured actions'
configured_triggers = spellbook_call('get_actions')

action_name = 'integrationtest_action_SendTransaction'

# Clean up old test action if necessary
if action_name in configured_triggers:
    response = spellbook_call('delete_action', action_name)
    assert response is None

# --------------------------------------------------------------------------------------------------------
fee_address = get_address_from_wallet(0, 3)
fee_percentage = 1.0

wallet_type = 'BIP44'
bip44_account = 1
bip44_index = 0

minimum_amount = 10000000000  # 100 BTC
receiving_address = get_address_from_wallet(0, 4)


op_return_data = 'A test op return message'

print 'Creating test action: SendTransaction'
response = spellbook_call('save_action', action_name, '-t=SendTransaction', '-fa=%s' % fee_address, '-fp=%s' % fee_percentage,
                          '-wt=%s' % wallet_type, '-ba=%s' % bip44_account, '-bi=%s' % bip44_index, '-ma=%s' % minimum_amount, '-ra=%s' % receiving_address,
                          '-or=%s' % op_return_data)
assert response is None

# --------------------------------------------------------------------------------------------------------
print 'Getting the list of configured action_ids'
response = spellbook_call('get_actions')
assert action_name in response

# --------------------------------------------------------------------------------------------------------
print 'Getting the action config of the action we just created'
response = spellbook_call('get_action_config', action_name)
assert response['id'] == action_name
assert response['action_type'] == 'SendTransaction'
assert response['fee_address'] == fee_address
assert response['fee_percentage'] == fee_percentage
assert response['wallet_type'] == wallet_type
assert response['bip44_account'] == bip44_account
assert response['bip44_index'] == bip44_index
assert response['sending_address'] == get_address_from_wallet(bip44_account, bip44_index)
# assert response['amount'] == amount
assert response['minimum_amount'] == minimum_amount
assert response['receiving_address'] == receiving_address
assert response['op_return_data'] == op_return_data

print 'Setting to second address'
bip44_index = 1
response = spellbook_call('save_action', action_name, '-bi=%s' % bip44_index)
assert response is None

response = spellbook_call('get_action_config', action_name)
assert response['bip44_index'] == bip44_index
assert response['sending_address'] == get_address_from_wallet(bip44_account, bip44_index)

print 'Setting back to first address'
bip44_index = 0
response = spellbook_call('save_action', action_name, '-bi=%s' % bip44_index)
assert response is None


registration_address = get_address_from_wallet(0, 3)
registration_block_height = 0
registration_xpub = get_xpub_key_from_wallet(0)
distribution_file = 'sample_distribution.json'


response = spellbook_call('save_action', action_name, '-reg_a=%s' % registration_address, '-reg_b=%s' % registration_block_height, '-reg_x=%s' % registration_xpub, '-d=%s' % distribution_file)
assert response is None
response = spellbook_call('get_action_config', action_name)
assert response['registration_address'] == registration_address
assert response['registration_block_height'] == registration_block_height
assert response['registration_xpub'] == registration_xpub

# --------------------------------------------------------------------------------------------------------
print 'Running the action we just created, should fail because minimum amount is greater than total value of unspent outputs'
response = spellbook_call('run_action', action_name)
assert response is False

print 'Setting minimum amount to less than total value of unspent outputs'
minimum_amount = 3000
response = spellbook_call('save_action', action_name, '-ma=%s' % minimum_amount)
assert response is None


for transaction_type in ['Send2Single', 'Send2Many', 'Send2SIL', 'Send2LBL', 'Send2LRL', 'Send2LSL', 'Send2LAL']:
    # for transaction_type in ['Send2LAL']:
    print 'Setting transaction_type to %s' % transaction_type
    response = spellbook_call('save_action', action_name, '-tt=%s' % transaction_type)
    assert response is None
    response = spellbook_call('get_action_config', action_name)
    assert response['transaction_type'] == transaction_type

    print 'Setting amount to 0 so all available funds should be sent'
    amount = 0
    response = spellbook_call('save_action', action_name,  '-a=%s' % amount)
    assert response is None
    #
    # print 'Running the action we just created, should succeed'
    # response = spellbook_call('run_action', action_name)
    # assert response is True
    #
    print 'Setting a specific amount to send instead of all available funds'
    amount = 3003
    response = spellbook_call('save_action', action_name,  '-a=%s' % amount)
    assert response is None
    #
    # print 'Running the action we just created, should succeed'
    # response = spellbook_call('run_action', action_name)
    # assert response is True

# --------------------------------------------------------------------------------------------------------



