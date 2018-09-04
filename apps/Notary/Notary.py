#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time

from trigger.triggertype import TriggerType
from action.actiontype import ActionType
from action.sendtransactionaction import TransactionType
from helpers.actionhelpers import get_action
from helpers.triggerhelpers import get_trigger
from helpers.hotwallethelpers import get_address_from_wallet
from helpers.loghelpers import LOG
from spellbookscripts.spellbookscript import SpellbookScript
from validators.validators import valid_op_return


##########################################################################################################
# Notary parameters
##########################################################################################################

# Set the account in the hot wallet to use for the Notary service
# Transactions with the OP_RETURN data will always be sent to the first address in the account
# For each request the next address in the account will be used to receive payment
WALLET_TYPE = 'BIP44'
BIP44_ACCOUNT = 0

# Set the cost fo the Notary service in Satoshis
NOTARY_COST = 100000

# Set a timeout in seconds for a request to self-destruct
REQUEST_TIMEOUT = 60 * 60 * 24  # set timeout to 1 day in the future

##########################################################################################################


class Notary(SpellbookScript):

    def run(self, *args, **kwargs):
        LOG.info('Running Spellbook Script: %s' % os.path.splitext(os.path.basename(__file__))[0])

        if 'message' not in self.json:
            LOG.error('key "message" not found in http POST request')
            return

        message = self.json['message']

        if not valid_op_return(message=message):
            LOG.error('Can not create Notary request: message is not valid to put in a OP_RETURN output: %s' % message)
            return

        # Use the number of times the trigger has been triggered as a identifier for the request and as the index of the address in the hot wallet
        request_id = self.triggered + 1

        # Get the address to receive payment
        request_address = get_address_from_wallet(account=BIP44_ACCOUNT, index=request_id)

        # Create a new action to send a custom transaction with the OP_RETURN data
        action_id = 'Notary-send-tx_%s' % request_id
        action = get_action(action_id=action_id, action_type=ActionType.SENDTRANSACTION)
        action.transaction_type = TransactionType.SEND2SINGLE
        action.wallet_type = WALLET_TYPE
        action.bip44_account = BIP44_ACCOUNT
        action.bip44_index = request_id
        action.receiving_address = get_address_from_wallet(account=BIP44_ACCOUNT, index=0)  # always use the first address in the account to receive the transactions
        action.op_return_data = message
        action.save()

        # Create a new trigger that activates when payment is received
        invoice_paid_trigger_id = 'Notary-payment_%s' % request_id
        trigger = get_trigger(trigger_id=invoice_paid_trigger_id, trigger_type=TriggerType.BALANCE)
        trigger.address = request_address
        trigger.amount = NOTARY_COST
        trigger.actions = [action_id]
        trigger.status = 'Active'
        trigger.self_destruct = int(time.time()) + REQUEST_TIMEOUT
        trigger.destruct_actions = True
        trigger.save()

        self.http_response = {'request_id': request_id,
                              'address': request_address,
                              'value': NOTARY_COST,
                              'timeout': int(time.time()) + REQUEST_TIMEOUT}

    def cleanup(self):
        pass
