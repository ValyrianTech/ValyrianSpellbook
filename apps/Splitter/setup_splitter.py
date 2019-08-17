#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from helpers.hotwallethelpers import get_address_from_wallet
from helpers.setupscripthelpers import spellbook_call, clean_up_triggers, clean_up_actions
from helpers.triggerhelpers import TriggerType
from helpers.actionhelpers import ActionType
from helpers.jsonhelpers import save_to_json_file
from validators.validators import valid_distribution

from action.transactiontype import TransactionType


##########################################################################################################
# Splitter parameters
##########################################################################################################

# Set the account and index from the hot wallet to use
wallet_type = 'BIP44'
bip44_account = 0
bip44_index = 0

# Set the address to receive funds
splitter_address = get_address_from_wallet(account=bip44_account, index=bip44_index)

# Set the required amount the splitter address needs to receive before sending a splitter transaction
# if a transaction with a lower value than this is received, nothing will happen until another transaction is received that makes the total above this value
amount = 10000

# Set the splitter fee, uncomment here and in the action if you want to charge a fee for the service
# splitter_fee_percentage = 1.0
# splitter_fee_address = get_address_from_wallet(account=bip44_account, index=bip44_index + 1)

# Set the distribution for the splitter
# This example will distribute the funds in the splitter address over the next 4 addresses in the wallet
# keys must be valid addresses, the values can be any integer, it is handy to make the sum of the values equal to 100 but that is not really necessary
# each address will receive a portion relative to its share and the total of all shares.
# Keep in mind each output value of the transaction must be at least the minimum output value (specified in the configuration file)
distribution = {get_address_from_wallet(account=bip44_account, index=bip44_index + 1): 25,
                get_address_from_wallet(account=bip44_account, index=bip44_index + 2): 30,
                get_address_from_wallet(account=bip44_account, index=bip44_index + 3): 10,
                get_address_from_wallet(account=bip44_account, index=bip44_index + 4): 35}

# Note: If you want to send a specific amount to each address, each value must be the amount in Satoshis and
# the SendTransaction amount must be exactly the sum of all values, if there is any change leftover, the change will go back to the splitter-address
# or to the change-address if one is specified

# total_amount = 100000000  # distribute exactly 1 bitcoin across all recipients
# change_address = get_address_from_wallet(account=bip44_account, index=bip44_index + 5)

# Check to make sure the distribution is valid
assert valid_distribution(distribution=distribution)

# must save the distribution as a json file
distribution_filename = os.path.join('splitter-distribution.json')
save_to_json_file(filename=distribution_filename, data=distribution)


##########################################################################################################

print('Setting up Splitter')
print('----------------------------------------------\n')

print('The address for the splitter is %s' % splitter_address)

# --------------------------------------------------------------------------------------------------------
# Clean up old triggers and actions first
# --------------------------------------------------------------------------------------------------------
clean_up_triggers(trigger_ids=['Splitter'])
clean_up_actions(action_ids=['Splitter'])

# --------------------------------------------------------------------------------------------------------
# Create Actions
# --------------------------------------------------------------------------------------------------------
print('\nCreating Action...')
action_id = 'Splitter'
action_type = ActionType.SENDTRANSACTION
transaction_type = TransactionType.SEND2MANY

# no need to set the amount, all funds in the address will be sent

response = spellbook_call('save_action', action_id,
                          '--type=%s' % action_type,
                          '--transaction_type=%s' % transaction_type,
                          '--wallet_type=%s' % wallet_type,
                          '--bip44_account=%s' % bip44_account,
                          '--bip44_index=%s' % bip44_index,
                          '--minimum_amount=%s' % amount,                                      # additional check to make sure enough funds are available in the address before sending transaction
                          '--distribution=%s' % os.path.abspath(distribution_filename),
                          # '--fee_percentage=%s' % splitter_fee_percentage,                   # uncomment if you want to charge a fee for the service
                          # '--fee_address=%s' % splitter_fee_address,                         # uncomment if you want to charge a fee for the service

                          # '--amount=%s' % total_amount,                                      # uncomment if you want to send a specific amount
                          # '--change_address=%s' % change_address,                            # uncomment if you want to send the change to a specific address

                          )
assert response is None

# --------------------------------------------------------------------------------------------------------
# Create Triggers
# --------------------------------------------------------------------------------------------------------
print('\nCreating Trigger...')
trigger_id = 'Splitter'
trigger_type = TriggerType.BALANCE

response = spellbook_call('save_trigger', trigger_id,
                          '--type=%s' % trigger_type,
                          '--address=%s' % splitter_address,
                          '--amount=%s' % amount,
                          '--actions=%s' % action_id,
                          '--multi')
assert response is None
