#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from subprocess import Popen, PIPE
import sys
import platform
import simplejson

PROGRAM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def spellbook_call(*args):
    args = [str(arg) for arg in args]
    spellbook_args = ['%s/spellbook.py' % PROGRAM_DIR]
    spellbook_args.extend(args)

    print '\nCALL: %s' % ' '.join(spellbook_args)
    spellbook = Popen(format_args(spellbook_args), stdout=PIPE, stderr=PIPE, shell=True)
    output, error = spellbook.communicate()
    stripped_output = output.strip()
    print 'RESPONSE: %s\n' % stripped_output

    stripped_error = error.strip()
    if len(stripped_error):
        print >> sys.stderr, '\n------------------BEGIN OF SPELLBOOK ERROR------------------'
        print >> sys.stderr, stripped_error
        print >> sys.stderr, '\nCALL: %s' % ' '.join(spellbook_args)
        print >> sys.stderr, '------------------END OF SPELLBOOK ERROR------------------\n'

    if len(stripped_output):
        spellbook_response = simplejson.loads(stripped_output)
        return spellbook_response


def bitcoinwand_call(address, message, url):
    bitcoinwand_args = ['%s/bitcoinwand.py' % PROGRAM_DIR, address, message, url]

    print '\nCALL: %s' % ' '.join(bitcoinwand_args)
    bitcoinwand = Popen(format_args(bitcoinwand_args), stdout=PIPE, stderr=PIPE, shell=True)
    output, error = bitcoinwand.communicate()
    stripped_output = output.strip()
    print 'RESPONSE: %s\n' % stripped_output

    stripped_error = error.strip()
    if len(stripped_error):
        print >> sys.stderr, '\n------------------BEGIN OF BITCOINWAND ERROR------------------'
        print >> sys.stderr, stripped_error
        print >> sys.stderr, '\nCALL: %s' % ' '.join(bitcoinwand_args)
        print >> sys.stderr, '------------------END OF BITCOINWAND ERROR------------------\n'

    if len(stripped_output):
        bitcoinwand_response = simplejson.loads(stripped_output)
        return bitcoinwand_response


def clean_up_triggers(trigger_ids):
    print 'Cleaning up triggers: %s' % trigger_ids
    print 'Getting the list of configured triggers'
    configured_trigger_ids = spellbook_call('get_triggers')

    for trigger_id in trigger_ids:
        if trigger_id in configured_trigger_ids:
            response = spellbook_call('delete_trigger', trigger_id)
            assert response is None


def clean_up_actions(action_ids):
    print 'Cleaning up actions: %s' % action_ids
    print 'Getting the list of configured actions'
    configured_action_ids = spellbook_call('get_actions')

    for action_id in action_ids:
        if action_id in configured_action_ids:
            response = spellbook_call('delete_action', action_id)
            assert response is None


def format_args(args):
    """
    Format the args to pass to the subprocess
    Linux requires a string with spaces, whereas Windows requires a list

    :param args: A list of arguments
    :return: The arguments as required by the operating system
    """
    return ' '.join(args) if platform.system() == 'Linux' else args
