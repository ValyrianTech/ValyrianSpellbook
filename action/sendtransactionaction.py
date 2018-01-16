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
        self.action_type = ActionType.FORWARDER

    def run(self):
        if self.sending_address is None:
            logging.getLogger('Spellbook').error('Can not activate SendTransaction action: sending address is None!')
            return False

        logging.getLogger('Spellbook').info('Activating SendTransaction action %s' % self.id)
        unspent_outputs = utxos(address=self.sending_address, confirmations=1)
        if 'utxos' in unspent_outputs and len(unspent_outputs['utxos']) > 0:
            logging.getLogger('Spellbook').info('utxos found: %s' % unspent_outputs['utxos'])
        else:
            logging.getLogger('Spellbook').error('No utxos found for address %s' % self.sending_address)

        total_value = sum([utxo['value'] for utxo in unspent_outputs['utxos']])
        logging.getLogger('Spellbook').info('Total value: %s' % total_value)

        if total_value < self.minimum_amount:
            logging.getLogger('Spellbook').error('SendTransaction action aborted: Total value is less than minimum amount: %s' % self.minimum_amount)
            return False

        # Calculate the forwarding fee if necessary
        forwarding_fee = 0
        if self.fee_percentage > 0:
            forwarding_fee = int(total_value * self.fee_percentage/100.0)
            logging.getLogger('Spellbook').info('Forwarding fee: %s' % forwarding_fee)

        # Get the current optimal transaction fee
        optimal_fee = get_optimal_fee()
        logging.getLogger('Spellbook').info('Optimal transaction fee is %s sat/b' % optimal_fee)

        # Construct the transaction inputs
        tx_inputs = []
        for utxo in unspent_outputs['utxos']:
            tx_inputs.append({'address': self.sending_address,
                              'value': utxo['value'],
                              'output': '%s:%s' % (utxo['output_hash'], utxo['output_n']),
                              'confirmations': utxo['confirmations']})

        # Construct the transaction outputs
        tx_outputs = [{'address': self.receiving_address, 'value': total_value - forwarding_fee}]
        if self.fee_address and forwarding_fee > 0:
            tx_outputs.append({'address': self.fee_address, 'value': forwarding_fee})

        logging.getLogger('Spellbook').info('Creating new transaction:')
        for tx_input in tx_inputs:
            logging.getLogger('Spellbook').info('INPUT: %s -> %s (%s)' % (tx_input['address'], tx_input['value'], tx_input['output']))

        for tx_output in tx_outputs:
            logging.getLogger('Spellbook').info('OUTPUT: %s -> %s' % (tx_output['address'], tx_output['value']))

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
        transaction = make_custom_tx(private_keys=private_keys, tx_inputs=tx_inputs, tx_outputs=tx_outputs)

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
        transaction = make_custom_tx(private_keys=private_keys, tx_inputs=tx_inputs, tx_outputs=tx_outputs, tx_fee=transaction_fee)
        logging.getLogger('Spellbook').info('Raw transaction: %s' % transaction)

        # Broadcast the transaction to the network
        # send_transaction # Todo: broadcast transaction
        return True

