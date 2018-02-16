#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import operator

from action import Action
from actiontype import ActionType
from data.data import utxos, prime_input_address, push_tx
from helpers.BIP44 import get_xpriv_key, get_private_key, set_testnet
from helpers.configurationhelpers import get_max_tx_fee_percentage, get_use_testnet
from helpers.configurationhelpers import get_minimum_output_value
from helpers.feehelpers import get_optimal_fee
from helpers.hotwallethelpers import get_address_from_wallet
from helpers.hotwallethelpers import get_hot_wallet
from inputs.inputs import get_sil
from linker.linker import get_lbl, get_lrl, get_lsl, get_lal
from transactionfactory import make_custom_tx
from transactiontype import TransactionType
from validators.validators import valid_address, valid_xpub, valid_amount, valid_op_return, valid_block_height
from validators.validators import valid_transaction_type, valid_distribution, valid_percentage


class SendTransactionAction(Action):
    def __init__(self, action_id):
        super(SendTransactionAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.SENDTRANSACTION
        self.fee_address = None
        self.fee_percentage = 0
        self.fee_minimum_amount = 1000
        self.wallet_type = None
        self.sending_address = None
        self.bip44_account = None
        self.bip44_index = None
        self.receiving_address = None
        self.receiving_xpub = None
        self.amount = 0
        self.minimum_amount = None
        self.op_return_data = None
        self.change_address = None
        self.registration_address = None
        self.registration_block_height = None
        self.registration_xpub = None
        self.distribution = None
        self.transaction_type = TransactionType.SEND2SINGLE
        self.minimum_output_value = get_minimum_output_value()
        self.unspent_outputs = None

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['fee_address']               : An address to send the spellbook fee to
                       - config['fee_percentage']            : The percentage to calculate the spellbook fee
                       - config['wallet_type']               : The type of wallet (Single or BIP44)
                       - config['sending_address']           : The address that will be sending the transaction
                       - config['bip44_account']             : An account number of a BIP44 wallet
                       - config['bip44_index']               : An index number of a BIP44 account
                       - config['receiving_address']         : The address to receive the transaction
                       - config['receiving_xpub']            : The xpub key to derive the receiving addresses from
                       - config['amount']                    : The amount to send
                       - config['minimum_amount']            : The minimum amount that needs to be available
                       - config['registration_address']      : An address used for the registration of a SIL, LBL, LRL or LSL
                       - config['registration_block_height'] : An block height used for the registration of a SIL
                       - config['registration_xpub']         : An xpub key used for the registration of a LBL, LRL or LSL
                       - config['distribution']              : A dict containing a distribution (each address should be a key in the dict with the value being the share)
        """
        super(SendTransactionAction, self).configure(**config)
        if 'fee_address' in config and valid_address(config['fee_address']):
            self.fee_address = config['fee_address']

        if 'fee_percentage' in config and valid_percentage(config['fee_percentage']):
            self.fee_percentage = config['fee_percentage']

        if 'wallet_type' in config and config['wallet_type'] in ['Single', 'BIP44']:
            self.wallet_type = config['wallet_type']

        if 'sending_address' in config and valid_address(config['sending_address']):
            self.sending_address = config['sending_address']

        if 'bip44_account' in config:
            self.bip44_account = config['bip44_account']

        if 'bip44_index' in config:
            self.bip44_index = config['bip44_index']

        if 'receiving_address' in config and valid_address(config['receiving_address']):
            self.receiving_address = config['receiving_address']

        if 'receiving_xpub' in config and valid_xpub(config['receiving_xpub']):
            self.receiving_xpub = config['receiving_xpub']

        if 'amount' in config and valid_amount(config['amount']):
            self.amount = config['amount']

        if 'minimum_amount' in config and valid_amount(config['minimum_amount']):
            self.minimum_amount = config['minimum_amount']

        if 'op_return_data' in config and valid_op_return(config['op_return_data']):
            self.op_return_data = config['op_return_data']

        if 'change_address' in config and valid_address(config['change_address']):
            self.receiving_address = config['change_address']

        if 'transaction_type' in config and valid_transaction_type(config['transaction_type']):
            self.transaction_type = config['transaction_type']

        if 'minimum_output_value' in config and valid_amount(config['minimum_output_value']):
            self.minimum_output_value = config['minimum_output_value']

        if 'registration_address' in config and valid_address(config['registration_address']):
            self.registration_address = config['registration_address']

        if 'registration_block_height' in config and valid_block_height(config['registration_block_height']):
            self.registration_block_height = config['registration_block_height']

        if 'registration_xpub' in config and valid_xpub(config['registration_xpub']):
            self.registration_xpub = config['registration_xpub']

        if 'distribution' in config and valid_distribution(config['distribution']):
            self.distribution = config['distribution']

        # fill in the address in case of a BIP44 hot wallet
        if self.wallet_type == 'BIP44':
            # Set BIP44 module to use testnet if necessary, configured in the spellbook.conf file under [Wallet] -> use_testnet
            set_testnet(get_use_testnet())

            self.sending_address = get_address_from_wallet(self.bip44_account, self.bip44_index)

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super(SendTransactionAction, self).json_encodable()
        ret.update({'fee_address': self.fee_address,
                    'fee_percentage': self.fee_percentage,
                    'wallet_type': self.wallet_type,
                    'sending_address': self.sending_address,
                    'bip44_account': self.bip44_account,
                    'bip44_index': self.bip44_index,
                    'receiving_address': self.receiving_address,
                    'receiving_xpub': self.receiving_xpub,
                    'amount': self.amount,
                    'minimum_amount': self.minimum_amount,
                    'op_return_data': self.op_return_data,
                    'change_address': self.change_address,
                    'transaction_type': self.transaction_type,
                    'minimum_output_value': self.minimum_output_value,
                    'registration_address': self.registration_address,
                    'registration_block_height': self.registration_block_height,
                    'registration_xpub': self.registration_xpub,
                    'distribution': self.distribution})
        return ret

    def run(self):
        """
        Run the action

        :return: True upon success, False upon failure
        """
        if self.sending_address is None:
            logging.getLogger('Spellbook').error('Can not activate SendTransaction action: sending address is None!')
            return False

        logging.getLogger('Spellbook').info('Activating SendTransaction action %s' % self.id)

        # Retrieve the available utxos of the sending address and construct a list of TransactionInput objects containing the necessary information for the inputs of a transaction
        # All available utxos will be used even if a subset would be enough, this is to avoid a scenario where the transaction fee would cause another utxo to be needed
        # which would increase the transaction fee which could cause another utxo to be needed .... and so on
        #
        # The benefit of this is that it will result in automatic consolidation of utxos, in the long run this is preferred otherwise you will end up with many small
        # utxos that might cost more in fees than they are worth
        data = utxos(address=self.sending_address, confirmations=1)
        if 'utxos' in data:
            self.unspent_outputs = [TransactionInput(address=self.sending_address,
                                                     value=utxo['value'],
                                                     output_hash=utxo['output_hash'],
                                                     output_n=utxo['output_n'],
                                                     confirmations=utxo['confirmations']) for utxo in data['utxos']]
        else:
            error_msg = data['error'] if 'error' in data else ''
            logging.getLogger('Spellbook').error('Error while retrieving utxos: %s' % error_msg)
            return False

        tx_inputs = self.construct_transaction_inputs()
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
        receiving_outputs = self.get_receiving_outputs(sending_amount)

        if len(receiving_outputs) == 0:
            logging.getLogger('Spellbook').error('SendTransaction action aborted: There are no receiving outputs!')
            return False

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

        self.log_transaction_info(tx_inputs=tx_inputs, tx_outputs=tx_outputs)

        # Do a sanity check on the transaction fee compared to the total value in inputs, abort if the fee is to high
        if not self.is_fee_acceptable(transaction_fee=transaction_fee, total_value_in_inputs=total_value_in_inputs):
            return False

        # Now make the real transaction including the transaction fee
        transaction = make_custom_tx(private_keys=private_keys, tx_inputs=tx_inputs, tx_outputs=tx_outputs, op_return_data=self.op_return_data, tx_fee=transaction_fee)

        # explicitly delete local variable private_keys for security reasons as soon as possible
        del private_keys

        if transaction is None:
            return False

        logging.getLogger('Spellbook').info('Raw transaction: %s' % transaction)

        # Broadcast the transaction to the network
        response = push_tx(tx=transaction)
        if 'success' in response and response['success'] is True:
            return True
        else:
            logging.getLogger('Spellbook').error('Broadcasting tx failed: %s' % response['error'])
            return False

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
            # Set BIP44 module to use testnet if necessary, configured in the spellbook.conf file under [Wallet] -> use_testnet
            set_testnet(get_use_testnet())

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

    def construct_transaction_inputs(self):
        """
        Construct a list of dict object containing the necessary information for the inputs of a transaction

        :return: A list of dicts containing the following keys for each utxo: 'address', 'value', 'output' and 'confirmations'
        """

        if self.unspent_outputs is not None and len(self.unspent_outputs) > 0:
            logging.getLogger('Spellbook').info('Found %s utxos for address %s' % (len(self.unspent_outputs), self.sending_address))
        else:
            logging.getLogger('Spellbook').error('No utxos found for address %s' % self.sending_address)

        # Construct the transaction inputs
        tx_inputs = [{'address': utxo.address,
                      'value': utxo.value,
                      'output': utxo.output,  # output needs to be formatted as txid:i
                      'confirmations': utxo.confirmations} for utxo in self.unspent_outputs]

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

    def get_distribution(self, transaction_type, sending_amount):
        # Todo check if all required parameters are valid

        if transaction_type == 'Send2Single':
            distribution = {self.receiving_address: sending_amount}
        elif transaction_type == 'Send2Many':
            distribution = self.distribution
        elif transaction_type == 'Send2SIL':
            data = get_sil(address=self.registration_address, block_height=self.registration_block_height)
            distribution = {recipient[0]: recipient[1] for recipient in data['SIL']}
        elif transaction_type == 'Send2LBL':
            data = get_lbl(address=self.registration_address, xpub=self.registration_xpub, block_height=self.registration_block_height)
            distribution = {recipient[0]: recipient[1] for recipient in data['LBL']}
        elif transaction_type == 'Send2LRL':
            data = get_lrl(address=self.registration_address, xpub=self.registration_xpub, block_height=self.registration_block_height)
            distribution = {recipient[0]: recipient[1] for recipient in data['LRL']}
        elif transaction_type == 'Send2LSL':
            data = get_lsl(address=self.registration_address, xpub=self.registration_xpub, block_height=self.registration_block_height)
            distribution = {recipient[0]: recipient[1] for recipient in data['LSL']}
        elif transaction_type == 'Send2LAL':
            # The registration address of a LAL must always be the sending address
            data = get_lal(address=self.sending_address, xpub=self.registration_xpub, block_height=self.registration_block_height)
            logging.getLogger('Spellbook').info('LAL: %s' % data['LAL'])
            distribution = {}
            for utxo in self.unspent_outputs:
                prime_input_address_data = prime_input_address(utxo.output_hash)
                prime_input_address_of_utxo = prime_input_address_data['prime_input_address'] if 'prime_input_address' in prime_input_address_data else None
                logging.getLogger('Spellbook').info('Prime input address of %s is %s' % (utxo.output_hash, prime_input_address_of_utxo))

                linked_address = [linked_address for input_address, linked_address in data['LAL'] if input_address == prime_input_address_of_utxo]
                # There should be exactly 1 linked address
                if len(linked_address) == 1:
                    distribution[linked_address[0]] = utxo.value
                else:
                    logging.getLogger('Spellbook').error('Something went wrong with the LAL: found %s linked addresses, should be exactly 1!' % len(linked_address))
                    raise Exception('Something went wrong with the LAL: found %s linked addresses, should be exactly 1!' % len(linked_address))

        else:
            raise NotImplementedError('Unknown transaction type %s' % transaction_type)

        logging.getLogger('Spellbook').info('distribution: %s' % distribution)
        return distribution

    def get_receiving_outputs(self, sending_amount):
        """
        Calculate the transaction outputs based on shares in a given distribution and the sending amount

        Each output value must be greater or equal than the minimum output value, otherwise that output is excluded from the distribution

        Important: the total of the output values must be the same as the sending_amount,
                   sometimes rounding errors can occur because of the distribution, if this happens
                   then the first output gets the remaining amount

        :param sending_amount: The total amount to send in satoshis (integer)
        :return: A list of TransactionOutputs
        """
        distribution = self.get_distribution(transaction_type=self.transaction_type, sending_amount=sending_amount)
        receiving_outputs = []
        remaining_amount = sending_amount

        # Sort the distribution from highest share to lowest share
        sorted_distribution = sorted(distribution.items(), key=operator.itemgetter(1), reverse=True)

        # Now iterate over the sorted distribution starting at the end, so we can safely delete the items with the
        # lowest value until the receiving value is at least the minimum output value
        for i in range(len(sorted_distribution)-1, -1, -1):
            # We need to re-calculate the total shares at each step because an item could have been deleted in the previous step
            total_shares = float(sum([share for address, share in sorted_distribution]))

            address = sorted_distribution[i][0]
            share = sorted_distribution[i][1]/float(total_shares) if total_shares > 0 else 0  # Calculate the share, this must be a float between 0 and 1

            receiving_value = int(share * sending_amount)
            if receiving_value < self.minimum_output_value:
                logging.getLogger('Spellbook').info('Excluding %s from distribution because output value is less than minimum output value: %s < %s' % (address, receiving_value, self.minimum_output_value))
                del sorted_distribution[i]
            else:
                remaining_amount -= receiving_value
                receiving_outputs.append(TransactionOutput(address, receiving_value))
                logging.getLogger('Spellbook').info('receiving output: %s -> %s' % (receiving_value, address))

        # If rounding errors are causing a few satoshis remaining, the first output gets them
        if remaining_amount > 0 and len(receiving_outputs) > 0:
            logging.getLogger('Spellbook').info('Remaining %s Satoshi(s) go to address %s' % (remaining_amount, receiving_outputs[0].address))
            receiving_outputs[0].value += remaining_amount

        return receiving_outputs

    def log_transaction_info(self, tx_inputs, tx_outputs):
        """
        Write information about the transaction in the logs

        :param tx_inputs: The transaction inputs
        :param tx_outputs: The transaction outputs
        """
        if self.amount == 0:
            logging.getLogger('Spellbook').info('New %s transaction: sending ALL available funds' % self.transaction_type)
        else:
            logging.getLogger('Spellbook').info('New %s transaction: sending %s satoshis' % (self.transaction_type, self.amount))

        for tx_input in tx_inputs:
            logging.getLogger('Spellbook').info('INPUT: %s -> %s (%s)' % (tx_input['address'], tx_input['value'], tx_input['output']))

        for tx_output in tx_outputs:
            logging.getLogger('Spellbook').info('OUTPUT: %s -> %s' % (tx_output['address'], tx_output['value']))

        if self.op_return_data is not None:
            logging.getLogger('Spellbook').info('OUTPUT: OP_RETURN -> %s' % self.op_return_data)

    @staticmethod
    def is_fee_acceptable(transaction_fee, total_value_in_inputs):
        """
        Check if we are not paying to much fees compared to the amount we are sending, anything above the max_tx_fee_percentage is too high
        This value is set in the configuration file under the [Transactions] section, 0=no check

        :param transaction_fee: The transaction fee in Satoshis
        :param total_value_in_inputs: The total value in the inputs in Satoshis
        :return: True or False
        """
        tx_fee_percentage = transaction_fee/float(total_value_in_inputs)*100

        if 0 < get_max_tx_fee_percentage() < tx_fee_percentage:
            logging.getLogger('Spellbook').error('Aborting SendTransaction: The transaction fee is too damn high: %s (%s percent of total input value)' % (transaction_fee, tx_fee_percentage))
            return False
        else:
            logging.getLogger('Spellbook').info('TRANSACTION FEE: %s (%s percent of total input value)' % (transaction_fee, tx_fee_percentage))
            return True


class TransactionInput(object):
    def __init__(self, address, value, output_hash, output_n, confirmations):
        self.address = address
        self.value = value
        self.output_hash = output_hash
        self.output_n = output_n
        self.confirmations = confirmations

        self.output = '%s:%s' % (self.output_hash, self.output_n)


class TransactionOutput(object):
    def __init__(self, address, amount):
        self.address = address
        self.value = amount
