#!/usr/bin/env python
# -*- coding: utf-8 -*-
from helpers.setupscripthelpers import spellbook_call
from helpers.BIP44 import set_testnet
from helpers.configurationhelpers import get_use_testnet
from helpers.hotwallethelpers import get_address_from_wallet

set_testnet(get_use_testnet())

print 'Starting Spellbook integration test: data'
print '----------------------------------------------\n'

# --------------------------------------------------------------------------------------------------------
print 'Getting latest block from Blockchain.info'
blockchain_info = spellbook_call('get_latest_block', '-e=blockchain.info')

print 'Getting latest block from Blocktrail.com'
blocktrail_com = spellbook_call('get_latest_block', '-e=blocktrail.com')

print 'Getting latest block from Blockexplorer.com'
blockexplorer_com = spellbook_call('get_latest_block', '-e=blockexplorer.com')

if not (blockchain_info['block']['time'] == blocktrail_com['block']['time'] == blockexplorer_com['block']['time']):
    print 'Not all times are the same!'
    print 'Blockchain.info:   %s' % blockchain_info['block']['time']
    print 'Blocktrail.com:    %s' % blocktrail_com['block']['time']
    print 'Blockexplorer.com: %s' % blockexplorer_com['block']['time']


# --------------------------------------------------------------------------------------------------------
block_height = 488470
print 'Getting block %s from Blockchain.info' % block_height
blockchain_info = spellbook_call('get_block', block_height, '-e=blockchain.info')

print 'Getting block %s from Blocktrail.com' % block_height
blocktrail_com = spellbook_call('get_block', block_height, '-e=blocktrail.com')

print 'Getting block %s from Blockexplorer.com' % block_height
blockexplorer_com = spellbook_call('get_block', block_height, '-e=blockexplorer.com')

assert blockchain_info['block']['hash'] == blocktrail_com['block']['hash'] == blockexplorer_com['block']['hash']
assert blockchain_info['block']['height'] == blocktrail_com['block']['height'] == blockexplorer_com['block']['height']
assert blockchain_info['block']['time'] == blocktrail_com['block']['time'] == blockexplorer_com['block']['time']

block_hash = blockchain_info['block']['hash']

# --------------------------------------------------------------------------------------------------------
print 'Getting block %s from Blockchain.info' % block_hash
blockchain_info = spellbook_call('get_block', block_hash, '-e=blockchain.info')

print 'Getting block %s from Blocktrail.com' % block_hash
blocktrail_com = spellbook_call('get_block', block_hash, '-e=blocktrail.com')

print 'Getting block %s from Blockexplorer.com' % block_hash
blockexplorer_com = spellbook_call('get_block', block_hash, '-e=blockexplorer.com')

assert blockchain_info['block']['hash'] == blocktrail_com['block']['hash'] == blockexplorer_com['block']['hash']
assert blockchain_info['block']['height'] == blocktrail_com['block']['height'] == blockexplorer_com['block']['height']
assert blockchain_info['block']['time'] == blocktrail_com['block']['time'] == blockexplorer_com['block']['time']


# --------------------------------------------------------------------------------------------------------
address = get_address_from_wallet(1, 0)  # use the first address of the second account in the hot wallet
print 'Getting transactions of address %s from Blockchain.info' % address
blockchain_info = spellbook_call('get_transactions', address, '-e=blockchain.info')

print 'Getting transactions of address %s from Blocktrail.com' % address
blocktrail_com = spellbook_call('get_transactions', address, '-e=blocktrail.com')

print 'Getting transactions of address %s from Blockexplorer.com' % address
blockexplorer_com = spellbook_call('get_transactions', address, '-e=blockexplorer.com')

assert len(blockchain_info['transactions']) == len(blocktrail_com['transactions']) == len(blockexplorer_com['transactions'])

txid = blockchain_info['transactions'][0]['txid']
# --------------------------------------------------------------------------------------------------------

print 'Getting prime input address of tx %s from Blockchain.info' % txid
blockchain_info = spellbook_call('get_prime_input_address', txid, '-e=blockchain.info')

print 'Getting prime input address of tx %s from Blocktrail.com' % txid
blocktrail_com = spellbook_call('get_prime_input_address', txid, '-e=blocktrail.com')

print 'Getting prime input address of tx %s from Blockexplorer.com' % txid
blockexplorer_com = spellbook_call('get_prime_input_address', txid, '-e=blockexplorer.com')

assert blockchain_info['prime_input_address'] == blocktrail_com['prime_input_address'] == blockexplorer_com['prime_input_address']


# --------------------------------------------------------------------------------------------------------
print 'Getting balance of address %s from Blockchain.info' % address
blockchain_info = spellbook_call('get_balance', address, '-e=blockchain.info')

print 'Getting balance of address %s from Blocktrail.com' % address
blocktrail_com = spellbook_call('get_balance', address, '-e=blocktrail.com')

print 'Getting balance of address %s from Blockexplorer.com' % address
blockexplorer_com = spellbook_call('get_balance', address, '-e=blockexplorer.com')

assert blockchain_info['balance']['final'] == blocktrail_com['balance']['final'] == blockexplorer_com['balance']['final']
assert blockchain_info['balance']['received'] == blocktrail_com['balance']['received'] == blockexplorer_com['balance']['received']
assert blockchain_info['balance']['sent'] == blocktrail_com['balance']['sent'] == blockexplorer_com['balance']['sent']
assert blockchain_info['balance']['n_tx'] == blocktrail_com['balance']['n_tx'] == blockexplorer_com['balance']['n_tx']


# --------------------------------------------------------------------------------------------------------
print 'Getting utxos of address %s from Blockchain.info' % address
blockchain_info = spellbook_call('get_utxos', address, '-e=blockchain.info')

print 'Getting utxos of address %s from Blocktrail.com' % address
blocktrail_com = spellbook_call('get_utxos', address, '-e=blocktrail.com')

print 'Getting utxos of address %s from Blockexplorer.com' % address
blockexplorer_com = spellbook_call('get_utxos', address, '-e=blockexplorer.com')

assert len(blockchain_info['utxos']) == len(blocktrail_com['utxos']) == len(blockexplorer_com['utxos'])
