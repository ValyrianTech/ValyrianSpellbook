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

        tx_inputs = self.construct_transaction_inputs(self.sending_address)
        total_value = int(sum([utxo['value'] for utxo in tx_inputs]))
        logging.getLogger('Spellbook').info('Total available value in utxos: %d' % total_value)

        if total_value < self.minimum_amount:
            logging.getLogger('Spellbook').error('SendTransaction action aborted: Total value is less than minimum amount: %s' % self.minimum_amount)
            return False

        # Calculate the spellbook fee if necessary, this fee should not be confuse with the transaction fee
        # This fee is an optional percentage-based fee the spellbook will subtract from the value and send to a special fee address
        spellbook_fee = 0
        if self.fee_percentage > 0 and self.fee_address is not None:
            fee_base = self.amount if self.amount is not None else total_value
            spellbook_fee = int(fee_base * self.fee_percentage/100.0)
            logging.getLogger('Spellbook').info('Spellbook fee: %s' % spellbook_fee)

        sending_amount = total_value - spellbook_fee
        change_amount = 0

        if self.amount is not None:
            sending_amount = self.amount
            change_amount = total_value - self.amount - spellbook_fee

        change_address = self.change_address if self.change_address is not None else self.sending_address

        change_output = None
        if change_amount > 0:
            change_output = TransactionOutput(change_address, change_amount)

        receiving_output = TransactionOutput(self.receiving_address, sending_amount)

        spellbook_fee_output = None
        if self.fee_address and spellbook_fee > 0:
            spellbook_fee_output = TransactionOutput(self.fee_address, spellbook_fee)

        tx_outputs = self.construct_transaction_outputs(receiving_outputs=[receiving_output],
                                                        change_output=change_output,
                                                        spellbook_fee_output=spellbook_fee_output)

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
        optimal_fee = 1
        logging.getLogger('Spellbook').info('Optimal transaction fee is %s sat/b' % optimal_fee)

        # Because the transaction is in hexadecimal, to calculate the size in bytes all we need to do is divide the number of characters by 2
        transaction_size = len(transaction) / 2
        transaction_fee = transaction_size * optimal_fee
        logging.getLogger('Spellbook').info('Transaction size is %s bytes, total transaction fee = %s (%s sat/b)' % (transaction_size, transaction_fee, optimal_fee))

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

    @staticmethod
    def construct_transaction_inputs(sending_address):
        """
        Retrieve the available utxos of the sending address and construct a list of dict object containing the necessary information for the inputs of a transaction
        All available utxos will be used even if a subset would be enough, this is to avoid a scenario where the transaction fee would cause another utxo to be needed
        which would increase the transaction fee which could cause another utxo to be needed .... and so on

        The benefit of this is that it will result in automatic consolidation of utxos, in the long run this is preferred otherwise you will end up with many small
        utxos that might cost more in fees than they are worth

        :return: utxos, total_value : a tuple containing the utxos and the total value of those utxos
        """
        unspent_outputs_data = utxos(address=sending_address, confirmations=1)
        unspent_outputs = []
        if 'utxos' in unspent_outputs_data and len(unspent_outputs_data['utxos']) > 0:
            unspent_outputs = unspent_outputs_data['utxos']
            logging.getLogger('Spellbook').info('utxos found: %s' % unspent_outputs)
        else:
            logging.getLogger('Spellbook').error('No utxos found for address %s' % sending_address)

        # Construct the transaction inputs
        tx_inputs = [{'address': sending_address,
                      'value': utxo['value'],
                      'output': '%s:%s' % (utxo['output_hash'], utxo['output_n']),
                      'confirmations': utxo['confirmations']} for utxo in unspent_outputs]

        return tx_inputs

    @staticmethod
    def construct_transaction_outputs(receiving_outputs, change_output=None, spellbook_fee_output=None):
        # Construct the transaction outputs
        tx_outputs = []

        # If there is any change, let it be the first output (once transaction fee is calculated, the fee will be subtracted from the first output)
        if isinstance(change_output, TransactionOutput) and change_output.value > 0:
            tx_outputs.append({'address': change_output.address, 'value': change_output.value})

        # Add each of the receiving outputs
        for receiving_output in receiving_outputs:
            if isinstance(receiving_output, TransactionOutput) and receiving_output.value > 0:
                tx_outputs.append({'address': receiving_output.address, 'value': receiving_output.value})

        # If there is a spellbook fee, add it as the last output
        if isinstance(spellbook_fee_output, TransactionOutput) and spellbook_fee_output.value > 0:
            tx_outputs.append({'address': spellbook_fee_output.address, 'value': spellbook_fee_output.value})

        return tx_outputs


class TransactionOutput(object):
    def __init__(self, address, amount):
        self.address = address
        self.value = amount
