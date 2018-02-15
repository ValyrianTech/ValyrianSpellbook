#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from integration_test_helpers import spellbook_call

# Change working dir up one level
os.chdir("..")

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
response = spellbook_call('save_explorer', 'blockchain.info', 'Blockchain.info', 'https://blockchain.info', 10)
assert response is None

response = spellbook_call('get_explorer_config', 'blockchain.info')
assert response['priority'] == 10
assert response['url'] == 'https://blockchain.info'
assert response['api_key'] == ''
assert response['type'] == 'Blockchain.info'

print '--------------------------------------------------------------------------------------------------------'
print 'Saving blockexplorer.com'
response = spellbook_call('save_explorer', 'blockexplorer.com', 'Insight', 'https://blockexplorer.com/api', 2)
assert response is None

response = spellbook_call('get_explorer_config', 'blockexplorer.com')
assert response['priority'] == 2
assert response['url'] == "https://blockexplorer.com/api"
assert response['api_key'] == ''
assert response['type'] == 'Insight'

print '--------------------------------------------------------------------------------------------------------'
print 'Saving blocktrail.com'

with open("blocktrail_key.txt", 'r') as input_file:
    blocktrail_key = input_file.readline()

response = spellbook_call('save_explorer', 'blocktrail.com', 'Blocktrail.com', 'https://api.blocktrail.com/v1', 3, '-b=%s' % blocktrail_key)
assert response is None

response = spellbook_call('get_explorer_config', 'blocktrail.com')
assert response['priority'] == 3
assert response['url'] == "https://api.blocktrail.com/v1"
assert response['api_key'] == blocktrail_key
assert response['type'] == 'Blocktrail.com'

print '--------------------------------------------------------------------------------------------------------'
print 'Getting the list of configured explorers'
response = spellbook_call('get_explorers')
assert response == ['blockexplorer.com', 'blocktrail.com', 'blockchain.info']

print '--------------------------------------------------------------------------------------------------------'
print 'Updating Blockchain.info with priority 1'
response = spellbook_call('save_explorer', 'blockchain.info', 'Blockchain.info', 'https://blockchain.info', 1)
assert response is None

response = spellbook_call('get_explorers')
assert response == ['blockchain.info', 'blockexplorer.com', 'blocktrail.com']