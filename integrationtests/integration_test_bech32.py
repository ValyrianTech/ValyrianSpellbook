#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from integration_test_helpers import spellbook_call

# Change working dir up one level
os.chdir("..")

print 'Starting Spellbook integration test: bech32'
print '----------------------------------------------\n'


print 'Getting the list of configured explorers'
configured_explorers = spellbook_call('get_explorers')

txid = '48089a814ac571944feb7162cc0145eea4e72742aa51f6f23d470debd838eeb3'
address = 'tb1ql7kvd5w8d0czy7majmxhm2mul99039zvlzrkn0'

testnet_P2WPKH = 'tb1qw508d6qejxtdg4y5r3zarvary0c5xw7kxpjzsx'
testnet_P2WSH = 'tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q0sl5k7'

for explorer in configured_explorers:
    response = spellbook_call('get_prime_input_address', txid, '-e=%s' % explorer)
    if response['prime_input_address'] is None:
        print '%s does NOT support Bech32!' % explorer

for explorer in configured_explorers:
    response = spellbook_call('get_transactions', address, '-e=%s' % explorer)
