#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from action import Action
from actiontype import ActionType
from transactiontype import TransactionType
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
        total_value_in_inputs = int(sum([utxo['value'] for utxo in tx_inputs]))
        logging.getLogger('Spellbook').info('Total available value in utxos: %d' % total_value_in_inputs)

        if total_value_in_inputs < self.minimum_amount:
            logging.getLogger('Spellbook').error('SendTransaction action aborted: Total value is less than minimum amount: %s' % self.minimum_amount)
            return False

        spellbook_fee = self.calculate_spellbook_fee(total_value_in_inputs)

        if self.amount == 0 and total_value_in_inputs < spellbook_fee:
            logging.getLogger('Spellbook').error('SendTransaction action aborted: Total input value is less than the spellbook fee: %s < %s' % (total_value_in_inputs, spellbook_fee))
            return False
        elif total_value_in_inputs < spellbook_fee + self.amount:
            logging.getLogger('Spellbook').error('SendTransaction action aborted: Total input value is not enough: %s < %s + %s' % (total_value_in_inputs, self.amount, spellbook_fee))
            return False

        sending_amount = total_value_in_inputs - spellbook_fee if self.amount == 0 else self.amount

        if self.transaction_type == TransactionType.SEND2SINGLE:
            receiving_outputs = [TransactionOutput(self.receiving_address, sending_amount)]
        elif self.transaction_type == TransactionType.SEND2MANY:
            receiving_outputs = self.get_receiving_outputs(sending_amount)
        elif self.transaction_type in [TransactionType.SEND2SIL, TransactionType.SEND2LBL, TransactionType.SEND2LRL, TransactionType.SEND2LSL]:
            receiving_outputs = self.get_distribution_outputs(transaction_type=self.transaction_type)
        elif self.transaction_type == TransactionType.SEND2LAL:
            receiving_outputs = self.get_forwarding_outputs()
        else:
            raise NotImplementedError('Unknown transaction type: %s' % self.transaction_type)

        change_output = None
        # There should only be a change output if we are sending a specific amount, when sending all available funds there should never be a change output
        if self.amount != 0:
            total_value_in_outputs = sum([output.value for output in receiving_outputs])
            change_amount = total_value_in_inputs - total_value_in_outputs - spellbook_fee
            change_address = self.change_address if self.change_address is not None else self.sending_address
            change_output = TransactionOutput(change_address, change_amount)

        spellbook_fee_output = None
        if self.fee_address is not None and spellbook_fee > 0:
            spellbook_fee_output = TransactionOutput(self.fee_address, spellbook_fee)

        # Construct temporary transaction outputs so we can calculate the transaction fee
        tx_outputs = self.construct_transaction_outputs(receiving_outputs=receiving_outputs,
                                                        change_output=change_output,
                                                        spellbook_fee_output=spellbook_fee_output)

        # Get the necessary private keys from the hot wallet
        private_keys = self.get_private_key()
        if len(private_keys) == 0:
            return False

        # Make transaction without fee first to get the size
        transaction = make_custom_tx(private_keys=private_keys, tx_inputs=tx_inputs, tx_outputs=tx_outputs, op_return_data=self.op_return_data)

        if transaction is None:
            return False

        # Get the current optimal transaction fee
        optimal_fee = get_optimal_fee()
        optimal_fee = 1
        logging.getLogger('Spellbook').info('Optimal transaction fee is %s sat/b' % optimal_fee)

        # Because the transaction is in hexadecimal, to calculate the size in bytes all we need to do is divide the number of characters by 2
        transaction_size = len(transaction) / 2
        transaction_fee = transaction_size * optimal_fee
        logging.getLogger('Spellbook').info('Transaction size is %s bytes, total transaction fee = %s (%s sat/b)' % (transaction_size, transaction_fee, optimal_fee))

        # if the total available amount needs to be sent, then transaction fee should be equally subtracted from all receiving_outputs
        if self.amount == 0:
            total_sending_value = sum([output.value for output in receiving_outputs])
            if total_sending_value < transaction_fee:
                logging.getLogger('Spellbook').error('Aborting SendTransaction: The total value of the receiving outputs is less than the transaction fee: %s < %s' % (total_sending_value, transaction_fee))
                return False

            fee_share = transaction_fee/len(receiving_outputs)
            for receiving_output in receiving_outputs:
                if receiving_output.value < fee_share:
                    logging.getLogger('Spellbook').error('Aborting SendTransaction: The value of at least one receiving output is not enough to subtract its share of the transaction fee: %s < %s' % (receiving_output.value, fee_share))
                    return False
                else:
                    receiving_output.value -= fee_share

            # Adjust the transaction fee in case dividing the transaction fee has caused some rounding errors
            transaction_fee = fee_share * len(receiving_outputs)

        # if a specific amount needs to be sent, then the transaction fee should be subtracted from the change output
        elif self.amount > 0 and change_output is not None:
            if change_output.value < transaction_fee:
                logging.getLogger('Spellbook').error('Aborting SendTransaction: The value of the change output is less than the transaction fee: %s < %s' % (change_output.value, transaction_fee))
                return False
            else:
                change_output.value -= transaction_fee

        # Construct the transaction outputs again now that the transaction fee has been subtracted
        tx_outputs = self.construct_transaction_outputs(receiving_outputs=receiving_outputs,
                                                        change_output=change_output,
                                                        spellbook_fee_output=spellbook_fee_output)

        logging.getLogger('Spellbook').info('Creating new transaction:')
        for tx_input in tx_inputs:
            logging.getLogger('Spellbook').info('INPUT: %s -> %s (%s)' % (tx_input['address'], tx_input['value'], tx_input['output']))

        for tx_output in tx_outputs:
            logging.getLogger('Spellbook').info('OUTPUT: %s -> %s' % (tx_output['address'], tx_output['value']))

        if self.op_return_data is not None:
            logging.getLogger('Spellbook').info('OUTPUT: OP_RETURN -> %s' % self.op_return_data)

        # Check if we are not paying to much fees compared to the amount we are sending, anything above 10% is too high
        tx_fee_percentage = transaction_fee/float(total_value_in_inputs)*100
        if tx_fee_percentage > 10:
            logging.getLogger('Spellbook').error('Aborting SendTransaction: The transaction fee is too damn high: %s (%s percent of total input value)' % (transaction_fee, tx_fee_percentage))
            return False
        else:
            logging.getLogger('Spellbook').info('TRANSACTION FEE: %s (%s percent of total input value)' % (transaction_fee, tx_fee_percentage))

        # Now make the real transaction including the transaction fee
        transaction = make_custom_tx(private_keys=private_keys, tx_inputs=tx_inputs, tx_outputs=tx_outputs, op_return_data=self.op_return_data, tx_fee=transaction_fee)

        # explicitly delete local variable private_keys for security reasons as soon as possible
        del private_keys

        if transaction is None:
            return False

        logging.getLogger('Spellbook').info('Raw transaction: %s' % transaction)

        # Broadcast the transaction to the network
        # send_transaction # Todo: broadcast transaction
        return True

    def get_private_key(self):
        """
        Get the private key of the sending address from the hot wallet

        :return: a dict containing the private key of the sending address
        """
        private_keys = {}
        hot_wallet = get_hot_wallet()

        if self.wallet_type == 'Single':
            if self.sending_address in hot_wallet:
                private_keys[self.sending_address] = hot_wallet[self.sending_address]
            else:
                logging.getLogger('Spellbook').error('Private key for address %s not found in hot wallet!' % self.sending_address)

            # explicitly delete local variable hot_wallet for security reasons as soon as possible
            del hot_wallet

        elif self.wallet_type == 'BIP44':
            xpriv_key = get_xpriv_key(mnemonic=' '.join(hot_wallet['mnemonic']), passphrase=hot_wallet['passphrase'], account=self.bip44_account)
            # explicitly delete local variable hot_wallet for security reasons as soon as possible
            del hot_wallet
            private_keys.update(get_private_key(xpriv_key, self.bip44_index))
        else:
            # explicitly delete local variable hot_wallet for security reasons as soon as possible
            del hot_wallet
            raise NotImplementedError('Unknown wallet type: %s' % self.wallet_type)

        return private_keys

    def calculate_spellbook_fee(self, total_value_in_inputs):
        """
        Calculate the spellbook fee if necessary, this fee should not be confused with the transaction fee
        This fee is an optional percentage-based fee the spellbook will subtract from the value and send to a special fee address
        If the fee is below the specified minimum fee, then the minimum fee is used

        :param total_value_in_inputs: The total value in the transaction inputs (in satoshis)
        :return: The spellbook fee in satoshis
        """
        spellbook_fee = 0
        if self.fee_percentage > 0 and self.fee_address is not None:
            fee_base = total_value_in_inputs if self.amount == 0 else self.amount
            spellbook_fee = int(fee_base * self.fee_percentage/100.0)

            if spellbook_fee < self.fee_minimum_amount:
                spellbook_fee = self.fee_minimum_amount

            logging.getLogger('Spellbook').info('Spellbook fee: %s' % spellbook_fee)

        return spellbook_fee

    @staticmethod
    def construct_transaction_inputs(sending_address):
        """
        Retrieve the available utxos of the sending address and construct a list of dict object containing the necessary information for the inputs of a transaction
        All available utxos will be used even if a subset would be enough, this is to avoid a scenario where the transaction fee would cause another utxo to be needed
        which would increase the transaction fee which could cause another utxo to be needed .... and so on

        The benefit of this is that it will result in automatic consolidation of utxos, in the long run this is preferred otherwise you will end up with many small
        utxos that might cost more in fees than they are worth

        :param sending_address: The address that will be sending the transaction
        :return: A list of dicts containing the following keys for each utxo: 'address', 'value', 'output' and 'confirmations'
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
                      'output': '%s:%s' % (utxo['output_hash'], utxo['output_n']),  # output needs to be formatted as txid:i
                      'confirmations': utxo['confirmations']} for utxo in unspent_outputs]

        return tx_inputs

    @staticmethod
    def construct_transaction_outputs(receiving_outputs=None, change_output=None, spellbook_fee_output=None):
        """
        Construct a list of dicts containing the necessary information for the outputs of the transaction

        :param receiving_outputs: A list of TransactionOutput objects for each receiving output
        :param change_output: A TransactionOutput object for the change (optional)
        :param spellbook_fee_output: A TransactionOutput object for the spellbook fee (optional)
        :return: A list of dicts, each containing the 'address' and 'value'
        """
        if receiving_outputs is None:
            receiving_outputs = []

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

    def get_receiving_outputs(self, sending_amount):
        """
        Calculate the transaction outputs based on shares in a given distribution and the sending amount
        Important: the total of the output values must be the same as the sending_amount,
                   sometimes rounding errors can occur because of the distribution, if this happens
                   then the first output gets the remaining amount

        :param sending_amount: The total amount to send in satoshis (integer)
        :return: A list of TransactionOutputs
        """
        total_shares = float(sum([shares for address, shares in self.distribution]))
        receiving_outputs = []
        remaining_amount = sending_amount
        for address, shares in self.distribution:
            receiving_value = int((shares/total_shares)*sending_amount)
            remaining_amount -= receiving_value
            receiving_outputs.append(TransactionOutput(address, receiving_value))

        # If rounding errors are causing a few satoshis remaining, the first output gets them
        if remaining_amount > 0:
            receiving_outputs[0].value += remaining_amount

        return receiving_outputs

    def get_distribution_outputs(self, transaction_type):
        return []

    def get_forwarding_outputs(self):
        return []


class TransactionOutput(object):
    def __init__(self, address, amount):
        self.address = address
        self.value = amount
