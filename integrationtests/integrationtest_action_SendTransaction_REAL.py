#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bips.BIP32 import set_chain_mode
from helpers.hotwallethelpers import get_address_from_wallet
from helpers.setupscripthelpers import spellbook_call, clean_up_actions

# make sure testnet is always on for this integrationtest
set_chain_mode(mainnet=False)

print 'Starting Spellbook integration test: SendTransaction action'
print '----------------------------------------------\n'

# Clean up actions if necessary
clean_up_actions(action_ids=['integrationtest_action_SendTransaction_REAL'])

#########################################################################################################
# SendTransaction actions
#########################################################################################################
action_name = 'integrationtest_action_SendTransaction_REAL'

wallet_type = 'BIP44'
bip44_account = 0
bip44_index = 0

fee_address = get_address_from_wallet(account=0, index=1)
fee_percentage = 1.0

minimum_amount = 100000  # 100 BTC
receiving_address = get_address_from_wallet(account=0, index=2)

op_return_data = 'A test op return message'

# --------------------------------------------------------------------------------------------------------


print 'Creating test action: SendTransaction'
response = spellbook_call('save_action', action_name, '-t=SendTransaction', '-fa=%s' % fee_address, '-fp=%s' % fee_percentage,
                          '-wt=%s' % wallet_type, '-ba=%s' % bip44_account, '-bi=%s' % bip44_index, '-ma=%s' % minimum_amount, '-ra=%s' % receiving_address,
                          '-or=%s' % op_return_data)
assert response is None

# response = spellbook_call('run_action', action_name)
# assert response is True
