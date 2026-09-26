#!/usr/bin/env python
from bips.bip32 import set_chain_mode
from helpers.hotwallethelpers import get_address_from_wallet
from helpers.setupscripthelpers import clean_up_actions, spellbook_call

# make sure testnet is always on for this integrationtest
set_chain_mode(mainnet=False)

print('Starting Spellbook integration test: SendTransaction action')
print('----------------------------------------------\n')

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


print('Creating test action: SendTransaction')
response = spellbook_call('save_action', action_name, '-t=SendTransaction', f'-fa={fee_address}', f'-fp={fee_percentage}',
                          f'-wt={wallet_type}', f'-ba={bip44_account}', f'-bi={bip44_index}', f'-ma={minimum_amount}', f'-ra={receiving_address}',
                          f'-or={op_return_data}')
assert response is None

# response = spellbook_call('run_action', action_name)
# assert response is True
