#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE
import sys
import simplejson


def spellbook_call(*args):
    args = [str(arg) for arg in args]
    spellbook_args = ['spellbook.py']
    spellbook_args.extend(args)

    print 'CALL: %s' % ' '.join(spellbook_args)
    spellbook = Popen(spellbook_args, stdout=PIPE, stderr=PIPE, shell=True)
    output, error = spellbook.communicate()
    stripped_output = output.strip()
    print 'RESPONSE: %s' % stripped_output

    stripped_error = error.strip()
    if len(stripped_error):
        print >> sys.stderr, '\n------------------BEGIN OF SPELLBOOK ERROR------------------'
        print >> sys.stderr, stripped_error
        print >> sys.stderr, '------------------END OF SPELLBOOK ERROR------------------\n'

    if len(stripped_output):
        spellbook_response = simplejson.loads(stripped_output)
        return spellbook_response

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

    print '\nGetting the list of configured explorers, should be empty'
    response = spellbook_call('get_explorers')
    assert isinstance(response, list)
    assert len(response) == 0

print '--------------------------------------------------------------------------------------------------------'
print 'Saving Blockchain.info'
response = spellbook_call('save_explorer', 'blockchain.info', 'Blockchain.info', 'https://blockchain.info', 10)
