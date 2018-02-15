#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from BIP44.BIP44 import set_testnet
from helpers.configurationhelpers import get_use_testnet
from hot_wallet_helpers import get_address_from_wallet
from integration_test_helpers import spellbook_call

# Change working dir up one level
os.chdir("..")

set_testnet(get_use_testnet())
# make sure testnet is always on for this integrationtest
set_testnet(True)

print 'Starting Spellbook integration test: SendTransaction action'
print '----------------------------------------------\n'

#########################################################################################################
# SendTransaction actions
#########################################################################################################

print 'Getting the list of configured actions'
configured_triggers = spellbook_call('get_actions')

action_name = 'integrationtest_action_SendTransaction_REAL'

# Clean up old test action if necessary
if action_name in configured_triggers:
    response = spellbook_call('delete_action', action_name)
    assert response is None

# --------------------------------------------------------------------------------------------------------
fee_address = get_address_from_wallet(0, 3)
fee_percentage = 1.0

wallet_type = 'BIP44'
bip44_account = 0
bip44_index = 3

minimum_amount = 100000  # 100 BTC
receiving_address = get_address_from_wallet(0, 6)


op_return_data = 'A test op return message'

print 'Creating test action: SendTransaction'
response = spellbook_call('save_action', action_name, '-t=SendTransaction', '-fa=%s' % fee_address, '-fp=%s' % fee_percentage,
                          '-wt=%s' % wallet_type, '-ba=%s' % bip44_account, '-bi=%s' % bip44_index, '-ma=%s' % minimum_amount, '-ra=%s' % receiving_address,
                          '-or=%s' % op_return_data)
assert response is None

response = spellbook_call('run_action', action_name)
assert response is True
