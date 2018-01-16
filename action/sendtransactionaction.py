#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from action import Action
from actiontype import ActionType
from data.data import utxos, prime_input_address
from feehelpers import get_optimal_fee
from hot_wallet_helpers import get_hot_wallet
from BIP44.BIP44 import get_xpriv_key, get_private_key
from transactionfactory import make_custom_tx


class SendTransactionAction(Action):
    def __init__(self, action_id):
        super(SendTransactionAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.SENDTRANSACTION

    def run(self):
        if self.sending_address is None:
            logging.getLogger('Spellbook').error('Can not activate SendTransaction action: sending address is None!')
            return False

        logging.getLogger('Spellbook').info('Activating SendTransaction action %s' % self.id)

        tx_inputs, total_value = self.select_utxos()

        if total_value < self.minimum_amount:
            logging.getLogger('Spellbook').error('SendTransaction action aborted: Total value is less than minimum amount: %s' % self.minimum_amount)
            return False

        # Calculate the spellbook fee if necessary, this fee should not be confuse with the transaction fee
        # This fee is an optional percentage-based fee the spellbook will subtract from the value and send to a special fee address
        spellbook_fee = 0
        if self.fee_percentage > 0 and self.fee_address is not None:
            spellbook_fee = int(total_value * self.fee_percentage/100.0)
            logging.getLogger('Spellbook').info('Spellbook fee: %s' % spellbook_fee)

        # Construct the transaction outputs
        tx_outputs = [{'address': self.receiving_address, 'value': total_value - spellbook_fee}]
        if self.fee_address and spellbook_fee > 0:
            tx_outputs.append({'address': self.fee_address, 'value': spellbook_fee})

        logging.getLogger('Spellbook').info('Creating new transaction:')
        for tx_input in tx_inputs:
            logging.getLogger('Spellbook').info('INPUT: %s -> %s (%s)' % (tx_input['address'], tx_input['value'], tx_input['output']))

        for tx_output in tx_outputs:
            logging.getLogger('Spellbook').info('OUTPUT: %s -> %s' % (tx_output['address'], tx_output['value']))

        if self.op_return_data is not None:
            logging.getLogger('Spellbook').info('OUTPUT: OP_RETURN -> %s' % self.op_return_data)

        # Get the necessary private keys from the hot wallet
        private_keys = {}
        hot_wallet = get_hot_wallet()

        if self.wallet_type == 'Single':
            if self.sending_address in hot_wallet:
                private_keys[self.sending_address] = hot_wallet[self.sending_address]
                hot_wallet = None
            else:
                logging.getLogger('Spellbook').error('Private key for address %s not found in hot wallet!' % self.sending_address)
                hot_wallet = None
                return False

        elif self.wallet_type == 'BIP44':
            xpriv_key = get_xpriv_key(mnemonic=' '.join(hot_wallet['mnemonic']), passphrase=hot_wallet['passphrase'], account=self.bip44_account)
            hot_wallet = None
            private_keys.update(get_private_key(xpriv_key, self.bip44_index))
        else:
            hot_wallet = None
            raise NotImplementedError('Unknown wallet type: %s' % self.wallet_type)

        # Make transaction without fee first to get the size
        transaction = make_custom_tx(private_keys=private_keys, tx_inputs=tx_inputs, tx_outputs=tx_outputs, op_return_data=self.op_return_data)

        # Get the current optimal transaction fee
        optimal_fee = get_optimal_fee()
        logging.getLogger('Spellbook').info('Optimal transaction fee is %s sat/b' % optimal_fee)

        # Because the transaction is in hexadecimal, to calculate the size in bytes all we need to do is divide the number of characters by 2
        transaction_size = len(transaction) / 2
        transaction_fee = transaction_size * optimal_fee
        logging.getLogger('Spellbook').info('Transaction size is %s bytes, total transaction fee = %s (%s sat/b)' % (transaction_size, transaction_fee, optimal_fee))

        transaction_fee = 1  # tmp fee for debugging TODO remove this

        # Subtract the transaction fee from the first transaction output
        if tx_outputs[0]['value'] <= transaction_fee:
            logging.getLogger('Spellbook').error('Transaction value of is not enough to subtract transaction fee!')
            return False
        else:
            tx_outputs[0]['value'] -= transaction_fee

        # Now make the real transaction including the transaction fee
        transaction = make_custom_tx(private_keys=private_keys, tx_inputs=tx_inputs, tx_outputs=tx_outputs, op_return_data=self.op_return_data, tx_fee=transaction_fee)
        logging.getLogger('Spellbook').info('Raw transaction: %s' % transaction)

        # Broadcast the transaction to the network
        # send_transaction # Todo: broadcast transaction
        return True

    def select_utxos(self, smallest_first=True):
        """
        Retrieve the available utxos of the sending address and select until the total value is greater than the amount needed
        if self.amount is None, then all available utxos are selected


        :param smallest_first: True or False.
                               Prefer to use the smallest utxos first (This does cause the transactions to be larger and thus require a higher transaction fee
                               but this option does automatically consolidate utxos, in the long run this is preferred otherwise you will end up with many small
                               utxos that might cost more in fees than they are worth), default=True
        :return: utxos, selected_value : a tuple containing the selected utxos and the total value of those utxos
        """
        unspent_outputs_data = utxos(address=self.sending_address, confirmations=1)
        unspent_outputs = []
        if 'utxos' in unspent_outputs_data and len(unspent_outputs_data['utxos']) > 0:
            unspent_outputs = unspent_outputs_data['utxos']
            logging.getLogger('Spellbook').info('utxos found: %s' % unspent_outputs)
        else:
            logging.getLogger('Spellbook').error('No utxos found for address %s' % self.sending_address)

        total_value = sum([utxo['value'] for utxo in unspent_outputs])
        logging.getLogger('Spellbook').info('Total available value in utxos: %s' % total_value)

        # Construct the transaction inputs
        tx_inputs = []
        selected_value = 0
        for utxo in sorted(unspent_outputs, key=lambda x: -x['value'], reverse=smallest_first):
            tx_inputs.append({'address': self.sending_address,
                              'value': utxo['value'],
                              'output': '%s:%s' % (utxo['output_hash'], utxo['output_n']),
                              'confirmations': utxo['confirmations']})
            selected_value += utxo['value']
            if self.amount is not None and self.amount <= selected_value:
                break

        return tx_inputs, selected_value

