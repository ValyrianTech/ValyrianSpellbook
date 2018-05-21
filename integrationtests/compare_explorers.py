#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import time
import copy
from integration_test_helpers import spellbook_call
from pprint import pprint


KEYNOTFOUNDIN1 = '<KEYNOTFOUNDIN1>'       # KeyNotFound for dictDiff
KEYNOTFOUNDIN2 = '<KEYNOTFOUNDIN2>'       # KeyNotFound for dictDiff


def dict_diff(first, second):
    """ Return a dict of keys that differ with another config object.  If a value is
        not found in one fo the configs, it will be represented by KEYNOTFOUND.
        @param first:   Fist dictionary to diff.
        @param second:  Second dictionary to diff.
        @return diff:   Dict of Key => (first.val, second.val)
    """
    diff = {}
    sd1 = set(first)
    sd2 = set(second)
    # Keys missing in the second dict
    for key in sd1.difference(sd2):
        diff[key] = KEYNOTFOUNDIN2
    # Keys missing in the first dict
    for key in sd2.difference(sd1):
        diff[key] = KEYNOTFOUNDIN1
    # Check for differences
    for key in sd1.intersection(sd2):
        if first[key] != second[key]:
            diff[key] = (first[key], second[key])
    return diff


class Comparison(object):
    def __init__(self, *args):
        self.explorers = spellbook_call('get_explorers')
        self.spellbook_args = list(args)

        self.responses = {}
        for explorer in self.explorers:
            self.responses[explorer] = self.get_response_from_explorer(explorer)

        self.compare_response_times()
        ok = self.compare_response_data()
        if not ok:
            sys.exit(1)

    def get_response_from_explorer(self, explorer):
        start_time = time.time()
        args_with_explorer = self.spellbook_args + ['-e=%s' % explorer]
        return spellbook_call(*args_with_explorer), time.time() - start_time

    def compare_response_times(self):
        print 'Response times:'
        for explorer in self.responses:
            print explorer, ':', self.responses[explorer][1]

    def compare_response_data(self):
        all_ok = True

        print '\nComparing response data:'
        response_data = {explorer: self.responses[explorer][0] for explorer in self.responses}
        keys = [key for key in response_data[self.explorers[0]].keys() if key != 'explorer']

        for i in range(len(self.explorers)):

            for key in keys:

                print ''
                print 'comparing key %s from %s and %s: ' % (key, self.explorers[i], self.explorers[i - 1]),
                first = copy.deepcopy(response_data[self.explorers[i]][key])
                second = copy.deepcopy(response_data[self.explorers[i-1]][key])

                if cmp(first, second) != 0:
                    print 'Not equal!'
                    if isinstance(first, dict) and isinstance(second, dict):
                        print dict_diff(first, second)
                    elif isinstance(first, list) and isinstance(second, list):
                        for j in range(len(first)):
                            if isinstance(first[j], dict) and isinstance(second[j], dict):
                                difference = dict_diff(first[j], second[j])
                                if difference:
                                    print 'transaction is different!!'
                                    print first[j]['txid']
                                    print second[j]['txid']
                                    pprint(difference)

                    all_ok = False

                else:
                    print 'OK'

        return all_ok

if __name__ == "__main__":
    # Create main parser
    parser = argparse.ArgumentParser(description='Compare explorers command line interface')

    parser.add_argument('args', help='The arguments for the spellbook.py command', nargs='+')

    # Parse the command line arguments
    args = parser.parse_args()

    Comparison(*args.args)
