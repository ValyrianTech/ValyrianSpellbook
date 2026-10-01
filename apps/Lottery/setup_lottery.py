#!/usr/bin/env python
# -*- coding: utf-8 -*-
from helpers.hotwallethelpers import get_address_from_wallet
from helpers.setupscripthelpers import spellbook_call, clean_up_triggers, clean_up_actions
from helpers.triggerhelpers import TriggerType
from helpers.actionhelpers import ActionType

from action.transactiontype import TransactionType
from data.data import latest_block, balance


##########################################################################################################
# Lottery parameters
##########################################################################################################

# Set the account and index from the hot wallet to use
wallet_type = 'BIP44'
bip44_account = 0
bip44_index = 0

lottery_address = get_address_from_wallet(account=bip44_account, index=bip44_index)

# Set the lottery fee
lottery_fee_percentage = 1.0
lottery_fee_address = get_address_from_wallet(account=bip44_account, index=bip44_index+1)

# Set when the lottery picks the winner (offset by the current block_height)
block_height_offset = 10

# Set when the lottery winner is paid, by number of confirmations after the block that picks the winner
# This is to avoid a situation where the block that picks the winner happens to become orphaned.
confirmations = 6

##########################################################################################################

print('Setting up Lottery')
print('----------------------------------------------\n')

print('The address for the lottery is %s' % lottery_address)
balances = balance(address=lottery_address)
print('Current balance: %s' % balances)
if balances['balance']['sent'] > 0:
    print('\nERROR: there have been prior transactions sent from this address, this means not all funds are available for the lottery!')
    print('Only unused addresses (or at least addresses that have not spent any funds yet) should be used for the lottery.')
    exit(1)


latest_block_data = latest_block()
if 'block' not in latest_block_data:
    print('Unable to get latest block')
    exit(1)

current_block_height = latest_block_data['block']['height']
print('\nCurrent block height: %s' % current_block_height)
print('Lottery will pick winner at block height: %s' % (current_block_height + block_height_offset))

# --------------------------------------------------------------------------------------------------------
# Clean up old triggers and actions first
# --------------------------------------------------------------------------------------------------------
clean_up_triggers(trigger_ids=['Lottery'])
clean_up_actions(action_ids=['Lottery-payout'])

# --------------------------------------------------------------------------------------------------------
# Create Actions
# --------------------------------------------------------------------------------------------------------
print('\nCreating Action...')
action_id = 'Lottery-payout'
action_type = ActionType.SENDTRANSACTION
transaction_type = TransactionType.SEND2SINGLE

response = spellbook_call('save_action', action_id,
                          '--type=%s' % action_type,
                          '--wallet_type=%s' % wallet_type,
                          '--bip44_account=%s' % bip44_account,
                          '--bip44_index=%s' % bip44_index,
                          '--fee_percentage=%s' % lottery_fee_percentage,
                          '--fee_address=%s' % lottery_fee_address)
assert response is None

# --------------------------------------------------------------------------------------------------------
# Create Triggers
# --------------------------------------------------------------------------------------------------------
print('\nCreating Trigger...')
trigger_id = 'Lottery'
trigger_type = TriggerType.BLOCK_HEIGHT
block_height = current_block_height + block_height_offset
script = 'Lottery\Lottery.py'

# note: the action for the trigger will be modified by the script because the winning address is not known at this time

response = spellbook_call('save_trigger', trigger_id,
                          '--type=%s' % trigger_type,
                          '--block_height=%s' % block_height,
                          '--confirmations=%s' % confirmations,
                          '--script=%s' % script)
assert response is None
