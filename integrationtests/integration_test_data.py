#!/usr/bin/env python
# -*- coding: utf-8 -*-

from integration_test_helpers import spellbook_call


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
print 'Getting block 488470 from Blockchain.info'
blockchain_info = spellbook_call('get_block', 488470, '-e=blockchain.info')

print 'Getting block 488470 from Blocktrail.com'
blocktrail_com = spellbook_call('get_block', 488470, '-e=blocktrail.com')

print 'Getting block 488470 from Blockexplorer.com'
blockexplorer_com = spellbook_call('get_block', 488470, '-e=blockexplorer.com')

assert blockchain_info['block']['hash'] == blocktrail_com['block']['hash'] == blockexplorer_com['block']['hash']
assert blockchain_info['block']['height'] == blocktrail_com['block']['height'] == blockexplorer_com['block']['height']
assert blockchain_info['block']['time'] == blocktrail_com['block']['time'] == blockexplorer_com['block']['time']

# --------------------------------------------------------------------------------------------------------
print 'Getting block 000000000000000000f6af507822a695390bada30cbd0c517c12442effb277af from Blockchain.info'
blockchain_info = spellbook_call('get_block', '000000000000000000f6af507822a695390bada30cbd0c517c12442effb277af', '-e=blockchain.info')

print 'Getting block 000000000000000000f6af507822a695390bada30cbd0c517c12442effb277af from Blocktrail.com'
blocktrail_com = spellbook_call('get_block', '000000000000000000f6af507822a695390bada30cbd0c517c12442effb277af', '-e=blocktrail.com')

print 'Getting block 000000000000000000f6af507822a695390bada30cbd0c517c12442effb277af from Blockexplorer.com'
blockexplorer_com = spellbook_call('get_block', '000000000000000000f6af507822a695390bada30cbd0c517c12442effb277af', '-e=blockexplorer.com')

assert blockchain_info['block']['hash'] == blocktrail_com['block']['hash'] == blockexplorer_com['block']['hash']
assert blockchain_info['block']['height'] == blocktrail_com['block']['height'] == blockexplorer_com['block']['height']
assert blockchain_info['block']['time'] == blocktrail_com['block']['time'] == blockexplorer_com['block']['time']

# --------------------------------------------------------------------------------------------------------
print 'Getting prime input address of tx 39bb5f5d50882227f93b980df15ea676414f0363770a0174a13c8f55c877b598 from Blockchain.info'
blockchain_info = spellbook_call('get_prime_input_address', '39bb5f5d50882227f93b980df15ea676414f0363770a0174a13c8f55c877b598', '-e=blockchain.info')

print 'Getting prime input address of tx 39bb5f5d50882227f93b980df15ea676414f0363770a0174a13c8f55c877b598 from Blocktrail.com'
blocktrail_com = spellbook_call('get_prime_input_address', '39bb5f5d50882227f93b980df15ea676414f0363770a0174a13c8f55c877b598', '-e=blocktrail.com')

print 'Getting prime input address of tx 39bb5f5d50882227f93b980df15ea676414f0363770a0174a13c8f55c877b598 from Blockexplorer.com'
blockexplorer_com = spellbook_call('get_prime_input_address', '39bb5f5d50882227f93b980df15ea676414f0363770a0174a13c8f55c877b598', '-e=blockexplorer.com')

assert blockchain_info['prime_input_address'] == blocktrail_com['prime_input_address'] == blockexplorer_com['prime_input_address']


# --------------------------------------------------------------------------------------------------------
print 'Getting transactions of address 1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y from Blockchain.info'
blockchain_info = spellbook_call('get_transactions', '1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', '-e=blockchain.info')

print 'Getting transactions of address 1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y from Blocktrail.com'
blocktrail_com = spellbook_call('get_transactions', '1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', '-e=blocktrail.com')

print 'Getting transactions of address 1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y from Blockexplorer.com'
blockexplorer_com = spellbook_call('get_transactions', '1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', '-e=blockexplorer.com')

assert len(blockchain_info['transactions']) == len(blocktrail_com['transactions']) == len(blockexplorer_com['transactions'])


# --------------------------------------------------------------------------------------------------------
print 'Getting balance of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 from Blockchain.info'
blockchain_info = spellbook_call('get_balance', '1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8', '-e=blockchain.info')

print 'Getting balance of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 from Blocktrail.com'
blocktrail_com = spellbook_call('get_balance', '1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8', '-e=blocktrail.com')

print 'Getting balance of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 from Blockexplorer.com'
blockexplorer_com = spellbook_call('get_balance', '1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8', '-e=blockexplorer.com')

assert blockchain_info['balance']['final'] == blocktrail_com['balance']['final'] == blockexplorer_com['balance']['final']
assert blockchain_info['balance']['received'] == blocktrail_com['balance']['received'] == blockexplorer_com['balance']['received']
assert blockchain_info['balance']['sent'] == blocktrail_com['balance']['sent'] == blockexplorer_com['balance']['sent']
assert blockchain_info['balance']['n_tx'] == blocktrail_com['balance']['n_tx'] == blockexplorer_com['balance']['n_tx']


# --------------------------------------------------------------------------------------------------------
print 'Getting utxos of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 from Blockchain.info'
blockchain_info = spellbook_call('get_utxos', '1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8', '-e=blockchain.info')

print 'Getting utxos of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 from Blocktrail.com'
blocktrail_com = spellbook_call('get_utxos', '1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8', '-e=blocktrail.com')

print 'Getting utxos of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 from Blockexplorer.com'
blockexplorer_com = spellbook_call('get_utxos', '1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8', '-e=blockexplorer.com')

assert len(blockchain_info['utxos']) == len(blocktrail_com['utxos']) == len(blockexplorer_com['utxos'])
