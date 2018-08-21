#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import binascii
from helpers.loghelpers import LOG


class TX(object):
    def __init__(self):
        """
        Constructor of a TX object
        """
        self.txid = ''
        self.wtxid = ''  # witness transaction hash
        self.lock_time = 0
        self.inputs = []
        self.outputs = []
        self.block_height = 0
        self.confirmations = 0

    def print_tx(self):
        """
        Print info about the transaction
        """
        print '\nblock ', str(self.block_height), "(" + str(self.confirmations) + " confirmations)", self.txid
        print 'IN:', self.inputs
        print 'OUT:', self.outputs
        print 'primeInput:', self.prime_input_address()

    def prime_input_address(self):
        """
        Get the prime input address of a transaction
        This is the input address that comes first alphabetically

        :return: The prime input address
        """
        addresses = []
        for tx_input in self.inputs:
            addresses.append(tx_input.address)

        return sorted(addresses)[0]

    def received_value(self, address):
        """
        Get the total value an address received in this transaction

        :param address: The address receiving the funds
        :return: The total amount received by the address
        """
        return sum([output.value for output in self.outputs if output.address == address])

    def is_receiving_tx(self, address):
        """
        Is this a receiving transaction for given address?

        :param address: The address
        :return: True if the transaction is a receiving transaction to the address otherwise False
        """
        received = True
        for tx_input in self.inputs:
            if tx_input.address == address:
                received = False

        return received

    def sent_value(self, address):
        """
        Get the total sent value for given address in this transaction

        :param address: The address
        :return: The total amount sent by the address
        """
        value = 0
        for tx_input in self.inputs:
            if tx_input.address == address:
                value += tx_input.value

        change = 0
        for tx_output in self.outputs:
            if tx_output.address == address:
                change += tx_output.value

        return value-change

    def is_sending_tx(self, address):
        """
        Is this a sending transaction for given address?

        :param address: The address
        :return: True if the transaction is a sending transaction to the address otherwise False
        """
        sending = False
        for tx_input in self.inputs:
            if tx_input.address == address:
                sending = True

        return sending

    def to_dict(self, address):
        """
        Convert to a json encodable dict

        :param address: The address
        :return: A dict containing info about the transaction from the pov of the address
        """
        tx_dict = {"txid": self.txid,
                   "wtxid": self.wtxid,
                   "lock_time": self.lock_time,
                   "prime_input_address": self.prime_input_address(),
                   "inputs": [tx_input.json_encodable() for tx_input in self.inputs],
                   "outputs": [tx_output.json_encodable() for tx_output in self.outputs],
                   "block_height": self.block_height,
                   "confirmations": self.confirmations,
                   "receiving": self.is_receiving_tx(address)}

        if tx_dict["receiving"] is True:
            tx_dict["receivedValue"] = self.received_value(address)
        else:
            tx_dict["sentValue"] = self.sent_value(address)

        return tx_dict

    @staticmethod
    def decode_op_return(hex_data):
        """
        Decode OP_RETURN data

        :param hex_data: The data in hex format
        :return: The decoded data
        """
        unhex_data = None
        if hex_data[:2] == '6a':
            if hex_data[2:4] == '4c':
                data = hex_data[6:]
                check_length = hex_data[4:6]
            elif hex_data[2:4] == '4d':
                data = hex_data[8:]
                check_length = hex_data[4:8]
            elif hex_data[2:4] == '4e':
                data = hex_data[10:]
                check_length = hex_data[4:10]
            else:
                data = hex_data[4:]
                check_length = hex_data[2:4]

            unhex_data = binascii.unhexlify(data)

            if len(unhex_data) != int(check_length, 16):
                LOG.error(
                    'OP_RETURN data is not the correct length! {0} -> should be {1}'.format(str(len(unhex_data)),
                                                                                            str(int(check_length,
                                                                                                    16))))
                unhex_data = None

        # Sometimes the unhexed data is encoded in another coded than utf-8 which could cause problems when converting to json later
        try:
            unhex_data = unhex_data.decode('utf-8')
        except UnicodeDecodeError:
            try:
                unhex_data = unhex_data.decode('cp1252')
            except Exception as ex:
                LOG.error('Unable to decode OP_RETURN data %s in utf-8 or cp1252: %s' % (hex_data, ex))
                unhex_data = 'Unable to decode hex data'

        return unhex_data

    def json_encodable(self):
        return {'txid': self.txid,
                'wtxid': self.wtxid,
                'lock_time': self.lock_time,
                'prime_input_address': self.prime_input_address(),
                'inputs': [tx_input.json_encodable() for tx_input in self.inputs],
                'outputs': [tx_output.json_encodable() for tx_output in self.outputs],
                'block_height': self.block_height,
                'confirmations': self.confirmations}


class TxInput(object):
    def __init__(self):
        self.address = None
        self.value = None
        self.txid = None
        self.n = None
        self.script = None
        self.sequence = None

    def json_encodable(self):
        return {'address': self.address,
                'value': self.value,
                'txid': self.txid,
                'n': self.n,
                'script': self.script,
                'sequence': self.sequence}


class TxOutput(object):
    def __init__(self):
        self.address = None
        self.value = None
        self.n = None
        self.script = None
        self.op_return = None
        self.spent = None

    def json_encodable(self):
        return {'address': self.address,
                'value': self.value,
                'n': self.n,
                'script': self.script,
                'spent': self.spent,
                'op_return': self.op_return}
