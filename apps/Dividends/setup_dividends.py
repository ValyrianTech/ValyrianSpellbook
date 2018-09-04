#!/usr/bin/env python
# -*- coding: utf-8 -*-
from helpers.hotwallethelpers import get_address_from_wallet
from helpers.setupscripthelpers import spellbook_call, clean_up_triggers, clean_up_actions
from helpers.triggerhelpers import TriggerType
from helpers.actionhelpers import ActionType
from action.transactiontype import TransactionType


##########################################################################################################
# Dividends parameters
##########################################################################################################

# Set the account and index from the hot wallet to use
wallet_type = 'BIP44'
bip44_account = 0
bip44_index_investors = 0
bip44_index_dividends = 1
bip44_index_fee = 2

# Set the address where investors must send their investment to so they can receive a dividend in the future
investors_address = get_address_from_wallet(account=bip44_account, index=bip44_index_investors)

# If you want to lock the investors' shares at a specific moment in time, uncomment the next line and also in the action
# investors_block_height = 500000

# Set the address to receive funds which will be distributed amongst the investors as dividends
dividends_address = get_address_from_wallet(account=bip44_account, index=bip44_index_dividends)

# Set the required amount the dividends address needs to receive before sending dividends
# if a transaction with a lower value than this is received, nothing will happen until another transaction is received that makes the total above this value
amount = 10000

# Set the dividends fee, in this case we will charge a 1 percent fee each time dividends are given out
dividends_fee_percentage = 1.0
dividends_fee_address = get_address_from_wallet(account=bip44_account, index=bip44_index_fee)

##########################################################################################################

print 'Setting up Dividends'
print '----------------------------------------------\n'

print 'The address for the dividends is %s' % dividends_address

# --------------------------------------------------------------------------------------------------------
# Clean up old triggers and actions first
# --------------------------------------------------------------------------------------------------------
clean_up_triggers(trigger_ids=['Dividends'])
clean_up_actions(action_ids=['Dividends'])

# --------------------------------------------------------------------------------------------------------
# Create Actions
# --------------------------------------------------------------------------------------------------------
print '\nCreating Action...'
action_id = 'Dividends'
action_type = ActionType.SENDTRANSACTION
transaction_type = TransactionType.SEND2SIL

# no need to set the amount, all funds in the address will be sent

response = spellbook_call('save_action', action_id,
                          '--type=%s' % action_type,
                          '--transaction_type=%s' % transaction_type,
                          '--wallet_type=%s' % wallet_type,
                          '--bip44_account=%s' % bip44_account,
                          '--bip44_index=%s' % bip44_index_dividends,
                          '--minimum_amount=%s' % amount,  # additional check to make sure enough funds are available in the address before sending transaction
                          '--registration_address=%s' % investors_address,
                          # '--registration_block_height=%s' % investors_block_height,         #uncomment if you want to lock the investors shares at a specific moment
                          '--fee_percentage=%s' % dividends_fee_percentage,
                          '--fee_address=%s' % dividends_fee_address,
                          )
assert response is None

# --------------------------------------------------------------------------------------------------------
# Create Triggers
# --------------------------------------------------------------------------------------------------------
print '\nCreating Trigger...'
trigger_id = 'Dividends'
trigger_type = TriggerType.BALANCE

response = spellbook_call('save_trigger', trigger_id,
                          '--type=%s' % trigger_type,
                          '--address=%s' % dividends_address,
                          '--amount=%s' % amount,
                          '--actions=%s' % action_id,
                          '--multi')
assert response is None
