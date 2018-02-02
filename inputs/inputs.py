#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from data import data
from validators.validators import valid_address, valid_op_return, valid_blockprofile_message


def get_sil(address, block_height=0):
    """
    Get the Simplified Inputs List (SIL)

    :param address: The address that received the transactions
    :param block_height: A block height (optional)
    :return: A dictionary containing the SIL and the explorer that provided the data
    """
    if not valid_address(address):
        return {'error': 'Invalid address: ' + address}

    txs_data = data.transactions(address)
    if 'transactions' in txs_data:
        return {'SIL': txs_2_sil(txs_data['transactions'], block_height)}
    else:
        return {'error': 'Unable to retrieve transactions of address %s' % address}


def txs_2_sil(txs, block_height=0):
    """
    Convert transactions received from an explorer to the Simplified Inputs List (SIL)

    :param txs: The transactions as received from one of the explorers
    :param block_height: An optional block height, if given, then the SIL at that moment in time is returned and transaction after this block height are ignored
    :return: An ordered list containing information about each prime input address of the receiving transactions
             Each item contains the following values:
             1) the prime input address of the transaction
             2) the total amount that this prime input address has sent (might be from multiple transactions)
             3) a float between 0 and 1 representing the share of the total received
             4) the block height of the first transaction of the prime input address
    """
    sil = []
    for tx in txs:
        if tx['receiving'] is True and tx['block_height'] is not None and (block_height == 0 or tx['block_height'] <= block_height):
            recurring = False
            for i in range(0, len(sil)):
                if sil[i][0] == tx['prime_input_address']:
                    sil[i][1] += tx['receivedValue']
                    recurring = True

            if not recurring:
                sil.append([tx['prime_input_address'], tx['receivedValue'], 0, tx['block_height']])  # Third value is placeholder for the share

    # Calculate the share of each prime input address
    total = float(sum([tx_input[1] for tx_input in sil]))
    for row in sil:
        row[2] = row[1]/total

    return sil


def get_profile(address, block_height=0):
    """
    Get the profile of an address

    :param address: The address
    :param block_height: A block height (optional)
    :return: A dict containing the profile and the explorer that provided the data
    """
    if not valid_address(address):
        return {'error': 'Invalid address: ' + address}

    txs_data = data.transactions(address)
    if 'transactions' in txs_data:
        return {'profile': txs_to_profile(txs_data['transactions'], address, block_height)}
    else:
        return {'error': 'Unable to retrieve transactions of address %s' % address}


def txs_to_profile(txs, address, block_height=0):
    """
    Converts the transactions of an address to a profile

    :param txs: The transactions as received by an explorer
    :param address: The address that received the transactions
    :param block_height: A block height (optional)
    :return: A dict containing the profile of an address
             The profile dict contains a key for each prime input address that sent a transaction to the address
             that had a OP_RETURN output in the form of a valid profile message (multiple messages separated by "|")

             a valid profile message contains 4 parts:
             from_index@to_index:variable_name=variable_value

             - from_index must be a positive integer and represents the index of one of the outputs of the transaction
                The address of the output it refers to is the 'from_address'
                this value is optional, if it is omitted then the 'from_address' is the receiving address itself

             - to_index must be a positive integer and represents the index of one of the outputs of the transaction
                the address of the output it refers to is the 'to_address'

             - variable_name must be a alphanumerical value (can NOT contain spaces)

             - variable_value must be an alphanumerical value (can also contain spaces)

             Each key in the profile dict contains another dict with following keys:
                - last_update : the block_height of the last transaction with a valid profile op_return message
                - SELF : the address of the profile (optional)
                - each 'from_address' (optional)

                Each of the 'SELF' or 'from_address' keys contains a dictionary with variable_name and its most recent
                variable_value where the 'to_address' is the receiving address

            example profile of 1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y at block height 425030:
            {u'15K68dgEFgUXKcjNghqYrp7StAEjavmBkg': {u'1SansacmMr38bdzGkzruDVajEsZuiZHx9': {'RELATION': 'Sister'},
                                                    'last_update': 425026},
             u'19cEeC36pcAap3ZhdAJnrpsbJ3xjwQyWRB': {'SELF': {'NAME': 'Robb Stark'},
                                                     'last_update': 425030},
             u'1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8': {'last_update': 421857},
             u'1Hm68TYvcqHm63r9vrn56WrfmUws3BrpZw': {'SELF': {'HOUSE': 'Stark'},
                                                     'last_update': 425030}}

    """
    profile = {}
    for tx in txs:
        if tx['block_height'] is not None and (block_height == 0 or tx['block_height'] <= block_height):
            for output in tx['outputs']:
                if 'op_return' in output:
                    prime_input_address = tx['prime_input_address']
                    tx_block_height = tx['block_height']

                    message = output['op_return']
                    if valid_op_return(message) and valid_blockprofile_message(message):
                        profile[prime_input_address] = {'last_update': tx_block_height}
                        for message_part in message.split("|"):
                            from_index, to_index, variable_name, variable_value = re.split('[@:=]+', message_part)

                            from_address = tx['outputs'][int(from_index)]['address'] if from_index else 'SELF'
                            to_address = tx['outputs'][int(to_index)]['address']

                            if to_address == address:
                                if from_address in profile[prime_input_address]:
                                    profile[prime_input_address][from_address][variable_name] = variable_value
                                else:
                                    profile[prime_input_address][from_address] = {variable_name: variable_value}
    return profile


def get_sul(address, confirmations=1):
    if not valid_address(address):
        return {'error': 'Invalid address: ' + address}

    utxos_data = data.utxos(address=address, confirmations=confirmations)
    if 'utxos' in utxos_data:
        sul = utxos_to_sul(utxos_data['utxos'])
        return {'SUL': sul} if 'error' not in sul else {'error': sul['error']}
    else:
        return {'error': 'Unable to retrieve utxos of address %s' % address}


def utxos_to_sul(utxos):
    sul = []

    for utxo in utxos:
        prime_input_address_data = data.prime_input_address(utxo['output_hash'])
        if 'prime_input_address' in prime_input_address_data:
            prime_input_address = prime_input_address_data['prime_input_address']
            recurring = False

            for row in sul:
                if row[0] == prime_input_address:
                    row[1] += utxo['value']
                    recurring = True
                    break

            if not recurring:
                sul.append([prime_input_address, utxo['value'], 0])  # Third value is a placeholder for the share
        else:
            return {'error': 'Unable to retrieve prime input address of txid %s' % utxo['output_hash']}

    # Calculate the share of each prime input address
    total = float(sum([row[1] for row in sul]))
    for row in sul:
        row[2] = row[1]/total if total > 0 else 0

    return sul
