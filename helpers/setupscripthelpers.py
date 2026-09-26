#!/usr/bin/env python
"""Helper functions for setup scripts that invoke the Spellbook CLI."""
import os
import sys
from subprocess import PIPE, Popen

import simplejson

from helpers.configurationhelpers import get_python_exe
from helpers.platformhelpers import format_args

PROGRAM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def spellbook_call(*args):
    """Invoke the Spellbook CLI with the given arguments and return the parsed JSON response."""
    args = [str(arg) for arg in args]
    spellbook_args = [get_python_exe(), os.path.join(PROGRAM_DIR, 'spellbook.py')]
    spellbook_args.extend(args)

    print('\nCALL: {}'.format(' '.join(spellbook_args)))
    spellbook = Popen(format_args(spellbook_args), stdout=PIPE, stderr=PIPE, shell=True)
    output, error = spellbook.communicate()
    stripped_output = output.strip().decode()
    print(f'RESPONSE: {stripped_output}\n')

    stripped_error = error.strip()
    if len(stripped_error):
        print('\n------------------BEGIN OF SPELLBOOK ERROR------------------', file=sys.stderr)
        print(stripped_error, file=sys.stderr)
        print('\nCALL: {}'.format(' '.join(spellbook_args)), file=sys.stderr)
        print('------------------END OF SPELLBOOK ERROR------------------\n', file=sys.stderr)

    if len(stripped_output):
        spellbook_response = simplejson.loads(stripped_output)
        return spellbook_response


def bitcoinwand_call(address, message, url):
    """Invoke the BitcoinWand script with address, message, and URL, returning the parsed response."""
    bitcoinwand_args = [get_python_exe(), os.path.join(PROGRAM_DIR, 'bitcoinwand.py'), address, message, url]

    print('\nCALL: {}'.format(' '.join(bitcoinwand_args)))
    bitcoinwand = Popen(format_args(bitcoinwand_args), stdout=PIPE, stderr=PIPE, shell=True)
    output, error = bitcoinwand.communicate()
    stripped_output = output.strip()
    print(f'RESPONSE: {stripped_output}\n')

    stripped_error = error.strip()
    if len(stripped_error):
        print('\n------------------BEGIN OF BITCOINWAND ERROR------------------', file=sys.stderr)
        print(stripped_error, file=sys.stderr)
        print('\nCALL: {}'.format(' '.join(bitcoinwand_args)), file=sys.stderr)
        print('------------------END OF BITCOINWAND ERROR------------------\n', file=sys.stderr)

    if len(stripped_output):
        bitcoinwand_response = simplejson.loads(stripped_output)
        return bitcoinwand_response


def clean_up_triggers(trigger_ids):
    """Delete the specified trigger IDs from the Spellbook if they exist."""
    print(f'Cleaning up triggers: {trigger_ids}')
    print('Getting the list of configured triggers')
    configured_trigger_ids = spellbook_call('get_triggers')

    for trigger_id in trigger_ids:
        if trigger_id in configured_trigger_ids:
            response = spellbook_call('delete_trigger', trigger_id)
            assert response is None


def clean_up_actions(action_ids):
    """Delete the specified action IDs from the Spellbook if they exist."""
    print(f'Cleaning up actions: {action_ids}')
    print('Getting the list of configured actions')
    configured_action_ids = spellbook_call('get_actions')

    for action_id in action_ids:
        if action_id in configured_action_ids:
            response = spellbook_call('delete_action', action_id)
            assert response is None
