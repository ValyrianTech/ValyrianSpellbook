#!/usr/bin/env python
from helpers.setupscripthelpers import spellbook_call

print('Starting Spellbook integration test: data')
print('----------------------------------------------\n')

# --------------------------------------------------------------------------------------------------------
print('Getting latest block from Blockchain.info')
blockchain_info = spellbook_call('get_latest_block', '-e=blockchain.info')

print('Getting latest block from BTC.com')
btc_com = spellbook_call('get_latest_block', '-e=btc.com')

print('Getting latest block from Blockstream.info')
blockstream_info = spellbook_call('get_latest_block', '-e=blockstream.info')

if not (blockchain_info['block']['time'] == btc_com['block']['time'] == blockstream_info['block']['time']):
    print('Not all times are the same!')
    print('Blockchain.info:   {}'.format(blockchain_info['block']['time']))
    print('BTC.com:    {}'.format(btc_com['block']['time']))
    print('Blockstream.info: {}'.format(blockstream_info['block']['time']))


# --------------------------------------------------------------------------------------------------------
# block_height = 488470  # Note: blockchain.info reports wrong for this block! it says an orphaned block is on the main chain when this is requested via the api (not via the website)
block_height = 488471
print(f'Getting block {block_height} from Blockchain.info')
blockchain_info = spellbook_call('get_block', block_height, '-e=blockchain.info')

print(f'Getting block {block_height} from BTC.com')
btc_com = spellbook_call('get_block', block_height, '-e=btc.com')

print(f'Getting block {block_height} from Blockstream.info')
blockstream_info = spellbook_call('get_block', block_height, '-e=blockstream.info')

assert blockchain_info['block']['hash'] == btc_com['block']['hash'] == blockstream_info['block']['hash']
assert blockchain_info['block']['height'] == btc_com['block']['height'] == blockstream_info['block']['height']
assert blockchain_info['block']['time'] == btc_com['block']['time'] == blockstream_info['block']['time']

block_hash = blockchain_info['block']['hash']

# --------------------------------------------------------------------------------------------------------
print(f'Getting block {block_hash} from Blockchain.info')
blockchain_info = spellbook_call('get_block', block_hash, '-e=blockchain.info')

print(f'Getting block {block_hash} from BTC.com')
btc_com = spellbook_call('get_block', block_hash, '-e=btc.com')

print(f'Getting block {block_hash} from Blockstream.info')
blockstream_info = spellbook_call('get_block', block_hash, '-e=blockstream.info')

assert blockchain_info['block']['hash'] == btc_com['block']['hash'] == blockstream_info['block']['hash']
assert blockchain_info['block']['height'] == btc_com['block']['height'] == blockstream_info['block']['height']
assert blockchain_info['block']['time'] == btc_com['block']['time'] == blockstream_info['block']['time']


# --------------------------------------------------------------------------------------------------------
address = '122Z63d9uRgYaAugxawaB79o12fRNYwFc8'  # address that received coinbase transactions
print(f'Getting transactions of address {address} from Blockchain.info')
blockchain_info = spellbook_call('get_transactions', address, '-e=blockchain.info')

print(f'Getting transactions of address {address} from BTC.com')
btc_com = spellbook_call('get_transactions', address, '-e=btc.com')

print(f'Getting transactions of address {address} from Blockstream.info')
blockstream_info = spellbook_call('get_transactions', address, '-e=blockstream.info')

assert len(blockchain_info['transactions']) == len(btc_com['transactions']) == len(blockstream_info['transactions'])

txid = blockchain_info['transactions'][0]['txid']
# --------------------------------------------------------------------------------------------------------

print(f'Getting prime input address of tx {txid} from Blockchain.info')
blockchain_info = spellbook_call('get_prime_input_address', txid, '-e=blockchain.info')

print(f'Getting prime input address of tx {txid} from BTC.com')
btc_com = spellbook_call('get_prime_input_address', txid, '-e=btc.com')

print(f'Getting prime input address of tx {txid} from Blockstream.info')
blockstream_info = spellbook_call('get_prime_input_address', txid, '-e=blockstream.info')

assert blockchain_info['prime_input_address'] == btc_com['prime_input_address'] == blockstream_info['prime_input_address']


# --------------------------------------------------------------------------------------------------------
print(f'Getting balance of address {address} from Blockchain.info')
blockchain_info = spellbook_call('get_balance', address, '-e=blockchain.info')

print(f'Getting balance of address {address} from BTC.com')
btc_com = spellbook_call('get_balance', address, '-e=btc.com')

print(f'Getting balance of address {address} from Blockstream.info')
blockstream_info = spellbook_call('get_balance', address, '-e=blockstream.info')

assert blockchain_info['balance']['final'] == btc_com['balance']['final'] == blockstream_info['balance']['final']
assert blockchain_info['balance']['received'] == btc_com['balance']['received'] == blockstream_info['balance']['received']
assert blockchain_info['balance']['sent'] == btc_com['balance']['sent'] == blockstream_info['balance']['sent']


# --------------------------------------------------------------------------------------------------------
address = '1BitcoinEaterAddressDontSendf59kuE'  # BitcoinEaterAddress, all outputs will always be unspent
print(f'Getting utxos of address {address} from Blockchain.info')
blockchain_info = spellbook_call('get_utxos', address, '-e=blockchain.info')

print(f'Getting utxos of address {address} from BTC.com')
btc_com = spellbook_call('get_utxos', address, '-e=btc.com')

print(f'Getting utxos of address {address} from Blockstream.info')
blockstream_info = spellbook_call('get_utxos', address, '-e=blockstream.info')

assert len(blockchain_info['utxos']) == len(btc_com['utxos']) == len(blockstream_info['utxos'])
