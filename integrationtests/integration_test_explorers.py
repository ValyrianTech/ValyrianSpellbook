#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from helpers.setupscripthelpers import spellbook_call

PROGRAM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


print 'Starting Spellbook integration test: explorers'
print '----------------------------------------------\n'

# --------------------------------------------------------------------------------------------------------
print 'Getting the list of configured explorers'
configured_explorers = spellbook_call('get_explorers')

if configured_explorers:
    print '--> Explorers found at beginning of test, deleting them before continuing'
    for explorer_id in configured_explorers:
        print '----> Get explorer config %s' % explorer_id
        response = spellbook_call('get_explorer_config', explorer_id)
        print '----> Deleting explorer %s' % explorer_id
        response = spellbook_call('delete_explorer', explorer_id)
        assert response is None

    print '\nGetting the list of configured explorers, should be empty'
    response = spellbook_call('get_explorers')
    assert isinstance(response, list)
    assert len(response) == 0

print '--------------------------------------------------------------------------------------------------------'
print 'Saving Blockchain.info'
response = spellbook_call('save_explorer', 'blockchain.info', 'Blockchain.info', 10)
assert response is None

response = spellbook_call('get_explorer_config', 'blockchain.info')
assert response['priority'] == 10
assert response['url'] is None
assert response['api_key'] == ''
assert response['type'] == 'Blockchain.info'

print '--------------------------------------------------------------------------------------------------------'
print 'Saving BTC.com'
response = spellbook_call('save_explorer', 'btc.com', 'BTC.com', 2)
assert response is None

response = spellbook_call('get_explorer_config', 'btc.com')
assert response['priority'] == 2
assert response['url'] is None
assert response['api_key'] == ''
assert response['type'] == 'BTC.com'

print '--------------------------------------------------------------------------------------------------------'
print 'Saving blockexplorer.com'
response = spellbook_call('save_explorer', 'blockexplorer.com', 'Insight', 3, '--url=%s' % "https://blockexplorer.com/api")
assert response is None

response = spellbook_call('get_explorer_config', 'blockexplorer.com')
assert response['priority'] == 3
assert response['url'] == "https://blockexplorer.com/api"
assert response['api_key'] == ''
assert response['type'] == 'Insight'

print '--------------------------------------------------------------------------------------------------------'
print 'Saving blocktrail.com'
blocktrail_key = ''
try:
    blocktrail_key_file = os.path.join(PROGRAM_DIR, "blocktrail_key.txt")
    with open(blocktrail_key_file, 'r') as input_file:
        blocktrail_key = input_file.readline()
except Exception as ex:
    print 'Unable to get the blocktrail key: %s' % ex
    exit(1)

response = spellbook_call('save_explorer', 'blocktrail.com', 'Blocktrail.com', 4, '--blocktrail_key=%s' % blocktrail_key)
assert response is None

response = spellbook_call('get_explorer_config', 'blocktrail.com')
assert response['priority'] == 4
assert response['url']is None
assert response['api_key'] == blocktrail_key
assert response['type'] == 'Blocktrail.com'

print '--------------------------------------------------------------------------------------------------------'
print 'Getting the list of configured explorers'
response = spellbook_call('get_explorers')
assert response == ['btc.com', 'blockexplorer.com', 'blocktrail.com', 'blockchain.info']

print '--------------------------------------------------------------------------------------------------------'
print 'Updating Blockchain.info with priority 1'
response = spellbook_call('save_explorer', 'blockchain.info', 'Blockchain.info', 1)
assert response is None

response = spellbook_call('get_explorers')
assert response == ['blockchain.info', 'btc.com', 'blockexplorer.com', 'blocktrail.com']