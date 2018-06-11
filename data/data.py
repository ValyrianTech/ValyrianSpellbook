#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os

from blockexplorers.blockchain_info import BlockchainInfoAPI
from blockexplorers.blocktrail_com import BlocktrailComAPI
from blockexplorers.insight import InsightAPI
from explorer import Explorer, ExplorerType
from helpers.jsonhelpers import save_to_json_file, load_from_json_file
from validators.validators import valid_address

EXPLORERS_JSON_FILE = 'json/private/explorers.json'
EXPLORER = None


def initialize_explorers_file():
    """
    Initialize the explorers.json file with the default explorer
    """
    default_explorer = Explorer()
    default_explorer.explorer_type = ExplorerType.BLOCKCHAIN_INFO
    default_explorer.url = 'https://blockchain.info'
    default_explorer.priority = 1

    data = {'blockchain.info': default_explorer.json_encodable()}
    save_to_json_file(EXPLORERS_JSON_FILE, data)


def get_explorers():
    """
    Get the list of explorer_ids sorted by priority

    :return: A list of explorer_ids sorted by priority
    """
    # Check if the explorers.json file exists and initialize it if necessary
    if not os.path.isfile(EXPLORERS_JSON_FILE):
        initialize_explorers_file()

    explorers = load_from_json_file(EXPLORERS_JSON_FILE)

    if explorers is not None and isinstance(explorers, dict):
        # Only return the explorer_ids sorted by priority
        return [explorer[0] for explorer in sorted(explorers.items(), key=lambda x:x[1]['priority'])]


def get_explorer_config(explorer_id):
    """
    Get the configuration of an explorer

    :param explorer_id: id of the explorer
    :return: a dict containing the configuration of the explorer
    """
    explorers = load_from_json_file(EXPLORERS_JSON_FILE)

    if explorer_id in explorers:
        return explorers[explorer_id]


def save_explorer(explorer_id, explorer_config):
    """
    Save or update an explorer config in the explorers.json file

    :param explorer_id: The id of the explorer
    :param explorer_config: A dict containing the configuration for the explorer
    """
    explorers = load_from_json_file(EXPLORERS_JSON_FILE)

    explorer = Explorer()
    if 'type' in explorer_config:
        explorer.explorer_type = explorer_config['type']
    if 'url' in explorer_config:
        explorer.url = explorer_config['url']
    if 'priority' in explorer_config:
        explorer.priority = int(explorer_config['priority'])
    if 'api_key' in explorer_config:
        explorer.api_key = explorer_config['api_key']
    if 'testnet' in explorer_config:
        explorer.testnet = explorer_config['testnet']

    explorers[explorer_id] = explorer.json_encodable()
    save_to_json_file(EXPLORERS_JSON_FILE, explorers)


def delete_explorer(explorer_id):
    """
    Delete an explorer

    :param explorer_id: The id of the explorer
    """
    explorers = load_from_json_file(EXPLORERS_JSON_FILE)

    if explorer_id in explorers:
        del explorers[explorer_id]
        save_to_json_file(EXPLORERS_JSON_FILE, explorers)


def get_explorer_api(name):
    """
    Get the correct explorer API object

    :param name: The name of the explorer
    :return: An ExplorerAPI object
    """
    explorers = load_from_json_file(EXPLORERS_JSON_FILE)

    if name in explorers:
        explorer = explorers[name]
        if explorer['type'] == ExplorerType.BLOCKCHAIN_INFO:
            return BlockchainInfoAPI(testnet=explorer['testnet'])
        elif explorer['type'] == ExplorerType.INSIGHT:
            return InsightAPI(url=explorer['url'], testnet=explorer['testnet'])
        elif explorer['type'] == ExplorerType.BLOCKTRAIL_COM:
            return BlocktrailComAPI(key=explorer['api_key'], testnet=explorer['testnet'])
        else:
            raise NotImplementedError('Unknown explorer API: %s' % name)


def query(query_type, param=None):
    """
    Do a query
    If an explorer is unavailable, the next explorer in the list will be tried


    :param query_type: The type of query
    :param param:  The parameters for the query
    :return: The response of the query
    """
    global EXPLORER

    if param is None:
        param = []

    # Get the list of explorers ordered by priority unless a specific explorer is specified
    explorers = get_explorers() if EXPLORER is None else [EXPLORER]

    message = ''
    for i in range(0, len(explorers)):
        explorer_api = get_explorer_api(explorers[i])
        if explorer_api:
            if query_type == 'block':
                data = explorer_api.get_block(param[0])
            elif query_type == 'block_by_height':
                data = explorer_api.get_block_by_height(param[0])
            elif query_type == 'block_by_hash':
                data = explorer_api.get_block_by_hash(param[0])
            elif query_type == 'latest_block':
                data = explorer_api.get_latest_block()
            elif query_type == 'transaction':
                data = explorer_api.get_transaction(param[0])
            elif query_type == 'prime_input_address':
                data = explorer_api.get_prime_input_address(param[0])
            elif query_type == 'balance':
                data = explorer_api.get_balance(param[0])
            elif query_type == 'transactions':
                data = explorer_api.get_transactions(param[0])
            elif query_type == 'utxos':
                data = explorer_api.get_utxos(*param)
            elif query_type == 'push_tx':
                data = explorer_api.push_tx(param[0])
            else:
                raise NotImplementedError('Unknown query type: %s' % query_type)

            if 'error' in data:
                message = '{explorer} failed to provide data for query: {query_type}'.format(explorer=explorers[i], query_type=query_type)
                if param != '':
                    message += ' param: ' + str(param)
                message += ' error: %s' % data['error']
                logging.getLogger('Spellbook').error(message)
            else:
                response = data
                EXPLORER = explorers[i]
                return response

    if len(explorers) == 1:
        return {'error': message}
    else:
        return {'error': 'Failed to retrieve data from all explorers'}


def block(height_or_hash):
    """
    Get a block by height or hash

    :param height_or_hash: A block height or a block hash
    :return: A dict containing info about the block
    """
    return query('block', [height_or_hash])


def block_by_height(height):
    """
    Get a block by height

    :param height: A block height
    :return: A dict containing info about the block
    """
    return query('block_by_height', [height])


def block_by_hash(block_hash):
    """
    Get a block by hash

    :param block_hash: A block hash
    :return: A dict containing info about the block
    """
    return query('block_by_hash', [block_hash])


def latest_block():
    """
    Get the latest block

    :return: A dict containing info about the latest block
    """
    return query('latest_block', None)

def transaction(txid):
    """
    Get a transaction

    :param txid: A transaction id
    :return: A dict containing info about the transaction
    """
    return query('transaction', [txid])


def prime_input_address(txid):
    """
    Get the prime input address of a transaction
    This is the input address that comes first alphabetically

    :param txid: A transaction id
    :return: A dict containing info about the prime input address
    """
    return query('prime_input_address', [txid])


def transactions(address):
    """
    Get the transactions of an address

    :param address: The address
    :return: A dict containing info about the transactions of the address
    """
    response = {'success': 0}
    if valid_address(address):
        response = query('transactions', [address])
    else:
        response['error'] = 'Invalid address'

    if 'transactions' in response:
        response['transactions'] = sorted(response['transactions'], key=lambda k: (k['block_height'], k['txid']))

    return response


def balance(address):
    """
    Get the balance of an address
    Will return 3 types of balances: final balance, total received and total sent

    :param address: The address
    :return: A dict containing info about the balance of the address
    """
    return query('balance', [address])


def utxos(address, confirmations):
    """
    Get the utxos of an address that have at least x confirmations

    :param address: The address
    :param confirmations: The number of required confirmations
    :return: A dict containing info about the utxos of the address
    """
    return query('utxos', [address, confirmations])


def push_tx(tx):
    """
    Push a raw transaction to the network

    :param tx: A raw transaction
    :return: A dict containing 'success' or 'error'
    """
    return query('push_tx', [tx])


def set_explorer(explorer_id):
    """
    Set a specific explorer to use in a global variable

    :param explorer_id: The id of the explorer
    """
    global EXPLORER
    EXPLORER = explorer_id


def clear_explorer():
    """
    Clear the global variable EXPLORER
    """
    global EXPLORER
    EXPLORER = None


def get_last_explorer():
    """
    Get the last used explorer

    :return: The id of the last used explorer
    """
    global EXPLORER
    return EXPLORER

