#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import time
import deepdiff

from helpers.setupscripthelpers import spellbook_call
from pprint import pprint


EXPLORERS = spellbook_call('get_explorers')


class Comparison(object):
    def __init__(self, *args):
        self.spellbook_args = list(args)

        print '\n\n#####################################################################################################'
        print '# Comparing: %s' % self.spellbook_args
        print '#####################################################################################################'

        self.responses = {}
        for explorer in EXPLORERS:
            self.responses[explorer] = self.get_response_from_explorer(explorer)

        self.compare_response_times()
        self.compare_response_data()
        print '---------------------------------------------------------------------------'

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

        for i in range(len(EXPLORERS)):
            print '\nComparing %s and %s: .... ' % (EXPLORERS[i], EXPLORERS[i-1]),
            differences = deepdiff.DeepDiff(response_data[EXPLORERS[i]], response_data[EXPLORERS[i-1]])

            if len(differences['values_changed'].keys()) > 1 or 'type_changes' in differences:
                print 'NOT OK'
                pprint(differences)
                all_ok = False
            else:
                print 'OK'

        return all_ok

if __name__ == "__main__":
    # Create main parser
    parser = argparse.ArgumentParser(description='Compare explorers command line interface')

    parser.add_argument('args', help='The arguments for the spellbook.py command', nargs='+')

    # Parse the command line arguments
    compare_args = parser.parse_args()

    Comparison(*compare_args.args)
