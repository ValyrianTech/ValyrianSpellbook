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

        if args[0] == 'get_transaction':
            transactions = {explorer: self.responses[explorer][0]['transaction'] for explorer in self.responses}
            self.compare_transaction(transactions=transactions)
        elif args[0] == 'get_transactions':
            all_ok = True
            # check each transaction
            for i in range(len(self.responses[self.responses.keys()[0]][0]['transactions'])):
                print '\n------------------------------------------------------------------'
                print 'Transaction %s' % i
                transactions = {explorer: self.responses[explorer][0]['transactions'][i] for explorer in self.responses}
                ok = self.compare_transaction(transactions=transactions)
                if ok is False:
                    all_ok = False

            # check the number of transactions
            n_txs = [len(self.responses[explorer][0]['transactions']) for explorer in self.responses]
            if not all(n_txs[0] == item for item in n_txs):
                print 'different number of transactions by some explorers'
                for explorer in self.responses:
                    print '%s: %' % (explorer, len(self.responses[explorer])[0]['transactions'])

            if all_ok is True:
                print 'All transactions are the same on all explorers'
        elif args[0] == 'get_utxos':
            all_ok = True
            # check each utxo
            for i in range(len(self.responses[self.responses.keys()[0]][0]['utxos'])):
                print '\n------------------------------------------------------------------'
                print 'UTXO %s' % i
                dicts = {explorer: self.responses[explorer][0]['utxos'][i] for explorer in self.responses}
                ok = self.compare_dict_items(dicts=dicts, item_names=['confirmations', 'output_hash', 'output_n', 'value', 'script'])
                if ok is False:
                    all_ok = False

            # check the number of utxos
            n_txs = [len(self.responses[explorer][0]['utxos']) for explorer in self.responses]
            if not all(n_txs[0] == item for item in n_txs):
                print 'different number of utxos by some explorers'
                for explorer in self.responses:
                    print '%s: %' % (explorer, len(self.responses[explorer])[0]['utxos'])

        elif args[0] in ['get_block', 'get_latest_block']:
            print '\n------------------------------------------------------------------'
            print 'Block'
            dicts = {explorer: self.responses[explorer][0]['block'] for explorer in self.responses}
            ok = self.compare_dict_items(dicts=dicts, item_names=['hash', 'height', 'merkleroot', 'time', 'size'])
            if ok is False:
                all_ok = False

        else:
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

    def compare_transaction(self, transactions):
        """
        Compare a transaction as received by each explorer

        :param transactions: a dict containing the transaction as received by each explorer
        """
        all_ok = True
        first_explorer = transactions.keys()[0]

        print '\nComparing transaction'
        dicts = transactions
        ok = self.compare_dict_items(dicts=dicts, item_names=['txid', 'block_height', 'confirmations', 'prime_input_address', 'lock_time'])  # wtxid only given by btc.com
        if ok is False:
            all_ok = False

        n_inputs = len(transactions[first_explorer]['inputs'])
        for i in range(n_inputs):
            print '\nComparing input %s' % i
            dicts = {explorer: transactions[explorer]['inputs'][i] for explorer in transactions}
            ok = self.compare_dict_items(dicts=dicts, item_names=['address', 'value', 'n', 'script'])  # txid is not present in responses from blockchain.info, sequence not given by blocktrail
            if ok is False:
                all_ok = False

        n_outputs = len(transactions[first_explorer]['outputs'])
        for i in range(n_outputs):
            print '\nComparing output %s' % i
            dicts = {explorer: transactions[explorer]['outputs'][i] for explorer in transactions}
            ok = self.compare_dict_items(dicts=dicts, item_names=['address', 'value', 'n', 'script', 'op_return', 'spent'])
            if ok is False:
                all_ok = False

        if all_ok is True:
            print 'transaction is the same on all explorers'

        return all_ok

    def compare_dict_items(self, dicts, item_names):
        all_ok = True
        for item_name in item_names:
            print '\nChecking %s' % item_name
            # check if all items are the same
            items = [dicts[explorer][item_name] for explorer in dicts]
            if not all(items[0] == item for item in items):
                all_ok = False
                for explorer in self.responses:
                    print '%s -> %s: %s' % (explorer, item_name, dicts[explorer][item_name])

        return all_ok

if __name__ == "__main__":
    # Create main parser
    parser = argparse.ArgumentParser(description='Compare explorers command line interface')

    parser.add_argument('args', help='The arguments for the spellbook.py command', nargs='+')

    # Parse the command line arguments
    compare_args = parser.parse_args()

    Comparison(*compare_args.args)
