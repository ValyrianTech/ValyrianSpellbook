#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import pybitcointools
from pybitcointools.transaction import *


def make_custom_tx(private_keys, tx_inputs, tx_outputs, tx_fee=0, op_return_data=''):
    """
    Construct a custom transaction

    :param private_keys: a dict containing a key for each required address with the corresponding private key
    :param tx_inputs: a list of dicts containing the following keys: 'address', 'value', 'output' and 'confirmations'
                   output should be formatted as 'txid:i'
    :param tx_outputs: a list of dicts containing the keys 'address' and 'value'
    :param tx_fee: The total transaction fee in satoshis (The fee must be equal to the difference of the inputs and the outputs, this is an extra safety precaution)
    :param op_return_data: an optional message to add as an OP_RETURN output (max 80 chars)
    :return: A raw transaction
    """
    # Check if the transaction fee is valid
    if not isinstance(tx_fee, int) or tx_fee < 0:
        logging.getLogger('Spellbook').error('Invalid transaction fee: %d satoshis' % tx_fee)
        return

    # Check if the supplied fee is equal to the difference between the total input value and total output value
    total_input_value = sum([tx_input['value'] for tx_input in tx_inputs])
    total_output_value = sum([tx_output['value'] for tx_output in tx_outputs])

    if tx_fee != total_input_value - total_output_value:
        logging.getLogger('Spellbook').error('Transaction fee does not match the difference between the total input value and the total output value!')
        return

    # Check if all required private keys have been supplied
    all_keys_present = all([tx_input['address'] in private_keys for tx_input in tx_inputs])
    if not all_keys_present:
        logging.getLogger('Spellbook').error("At least 1 private key is missing.")
        return

    # Check if all inputs have at least 1 confirmation
    all_inputs_confirmed = all([tx_input['confirmations'] > 0 for tx_input in tx_inputs])
    if not all_inputs_confirmed:
        logging.getLogger('Spellbook').error("At least 1 input is unconfirmed.")
        return

    # Check if an OP_RETURN message needs to be added and if it is valid
    if op_return_data != '' and len(op_return_data) > 80:
        logging.getLogger('Spellbook').error('OP_RETURN data is longer than 80 characters')
        return

    # All is good, make the transaction
    tx = pybitcointools.mktx(tx_inputs, tx_outputs)

    # Add OP_RETURN message if necessary
    if op_return_data != '':
        tx = add_op_return(op_return_data, tx)

    # Now sign each transaction input with the private key
    for i in range(0, len(tx_inputs)):
        tx = pybitcointools.sign(tx, i, str(private_keys[tx_inputs[i]['address']]))

    return tx


def send_tx(tx):
    success = False
    response = {}
    try:
        # retval = pybitcointools.blockr_pushtx(tx)
        retval = {'status': 'success'}
        logging.info("TX broadcast succeeded, Blockr response: %s" % str(retval))
        response = json.loads(retval)
    except Exception as e:
        logging.error("TX broadcast failed: %s" % str(e))

    if 'status' in response and response['status'] == 'success':
        success = True

    return success


# extra functions for op_return from a fork of pybitcointools
# https://github.com/wizardofozzie/pybitcointools


def num_to_op_push(x):
    x = int(x)
    if 0 <= x <= 75:
        pc = ''
        num = encode(x, 256, 1)
    elif x < 0xff:
        pc = from_int_to_byte(0x4c)
        num = encode(x, 256, 1)
    elif x < 0xffff:
        pc = from_int_to_byte(0x4d)
        num = encode(x, 256, 2)[::-1]
    elif x < 0xffffffff:
        pc = from_int_to_byte(0x4e)
        num = encode(x, 256, 4)[::-1]
    else:
        raise ValueError("0xffffffff > value >= 0")
    return pc + num


def wrap_script(hexdata):
    if re.match('^[0-9a-fA-F]*$', hexdata):
        return binascii.hexlify(wrap_script(binascii.unhexlify(hexdata)))
    return num_to_op_push(len(hexdata)) + hexdata


def add_op_return(msg, tx_hex=None):
    """Makes OP_RETURN script from msg, embeds in Tx hex"""
    hex_data = binascii.hexlify(b'\x6a' + wrap_script(msg))

    if tx_hex is None:
        return hex_data
    else:
        if not re.match("^[0-9a-fA-F]*$", tx_hex):
            return binascii.unhexlify(add_op_return(msg, binascii.hexlify(tx_hex)))
        elif isinstance(tx_hex, dict):
            txo = tx_hex
            outs = txo.get('outs')
        else:
            outs = deserialize(tx_hex).get('outs')

        txo = deserialize(tx_hex)
        assert (len(outs) > 0) and sum(multiaccess(outs, 'value')) > 0 \
            and not any([o for o in outs if o.get("script")[:2] == '6a']), \
            "Tx limited to *1* OP_RETURN, and only whilst the other outputs send funds"
        txo['outs'].append({'script': hex_data, 'value': 0})
        return serialize(txo)