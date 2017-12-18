#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import logging
from time import sleep

from data.transaction import TX
from data.explorer_api import ExplorerAPI


API_VERSION = 'v1'


class BlockchainInfoAPI(ExplorerAPI):

    def get_latest_block(self):
        latest_block = {}
        url = 'https://blockchain.info/latestblock'
        try:
            logging.getLogger('Spellbook').info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            logging.getLogger('Spellbook').error('Unable to get latest block from Blockchain.info: %s' % ex)
            return {'error': 'Unable to get latest block from Blockchain.info'}

        if all(key in data for key in ('height', 'hash', 'time')):
            latest_block['height'] = data['height']
            latest_block['hash'] = data['hash']
            latest_block['time'] = data['time']

            url = 'https://blockchain.info/rawblock/' + latest_block['hash']
            try:
                logging.getLogger('Spellbook').info('GET %s' % url)
                r = requests.get(url)
                data = r.json()
            except Exception as ex:
                logging.getLogger('Spellbook').error('Unable to get block %s from Blockchain.info: %s' % (latest_block['height'], ex))
                return {'error': 'Unable to get block %s from Blockchain.info' % latest_block['height']}

            if all(key in data for key in ('mrkl_root', 'size')):
                latest_block['merkleroot'] = data['mrkl_root']
                latest_block['size'] = data['size']

            return {'block': latest_block}
        else:
            return {'error': 'Received invalid data: %s' % data}

    def get_block_by_hash(self, block_hash):
        url = 'https://blockchain.info/rawblock/' + block_hash
        try:
            logging.getLogger('Spellbook').info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            logging.getLogger('Spellbook').error('Unable to get block %s from Blockchain.info: %s' % (block_hash, ex))
            return {'error': 'Unable to get block %s from Blockchain.info' % block_hash}

        if all(key in data for key in ('height', 'hash', 'time', 'mrkl_root', 'size')):
            block = {'height': data['height'],
                     'hash': data['hash'],
                     'time': data['time'],
                     'merkleroot': data['mrkl_root'],
                     'size': data['size']}
            return {'block': block}
        else:
            return {'error': 'Received invalid data: %s' % data}

    def get_block_by_height(self, height):
        url = 'https://blockchain.info/block-height/' + str(height) + '?format=json'
        try:
            logging.getLogger('Spellbook').info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            logging.getLogger('Spellbook').error('Unable to get block %s from Blockchain.info: %s' % (height, ex))
            return {'error': 'Unable to get block %s from Blockchain.info' % height}

        if 'blocks' in data:
            blocks = data['blocks']
            for i in range(0, len(blocks)):
                if blocks[i]['main_chain'] is True and blocks[i]['height'] == height:
                    block = {'height': blocks[i]['height'],
                             'hash': blocks[i]['hash'],
                             'time': blocks[i]['time'],
                             'merkleroot': blocks[i]['mrkl_root'],
                             'size': blocks[i]['size']}
                    return {'block': block}

        return {'error': 'Received invalid data: %s' % data}

    def get_transactions(self, address):
        limit = 50  # max number of tx given by blockchain.info is 50
        n_tx = None
        transactions = []
        latest_block_height = self.get_latest_block_height()
        if latest_block_height is None:
            return {'error': 'Unable to get latest block height'}

        i = 0
        while n_tx is None or len(transactions) < n_tx:
            url = 'https://blockchain.info/address/{address}?format=json&limit={limit}&offset={offset}'.format(address=address, limit=limit, offset=limit * i)
            try:
                logging.getLogger('Spellbook').info('GET %s' % url)
                r = requests.get(url)
                data = r.json()
            except Exception as ex:
                logging.getLogger('Spellbook').error('Unable to get transactions of address %s from %s: %s' % (address, url, ex))
                return {'error': 'Unable to get transactions of address %s from %s' % (address, url)}

            if all(key in data for key in ('n_tx', 'txs')):
                n_tx = data['n_tx']
                transactions += data['txs']
                i += 1
            else:
                return {'error': 'Received Invalid data: %s' % data}

            if len(transactions) < n_tx:
                sleep(1)

        txs = []
        for transaction in transactions:
            tx = TX()
            tx.txid = transaction['hash']
            tx.block_height = transaction['block_height'] if 'block_height' in transaction else None
            tx.confirmations = (latest_block_height - tx.block_height) + 1 if 'block_height' in transaction else 0

            for tx_input in transaction['inputs']:
                tx_in = {'address': tx_input['prev_out']['addr'],
                         'value': tx_input['prev_out']['value']}
                tx.inputs.append(tx_in)

            for out in transaction['out']:
                tx_out = {'address': out['addr'] if 'addr' in out else None,
                          'value': out['value'],
                          'spent': out['spent']}

                if out['script'][:2] == '6a':
                    tx_out['op_return'] = tx.decode_op_return(out['script'])

                tx.outputs.append(tx_out)

            txs.insert(0, tx.to_dict(address))

        if n_tx != len(txs):
            return {'error': 'Not all transactions are retrieved! expected {expected} but only got {received}'.format(expected=n_tx, received=len(txs))}
        else:
            return {'transactions': txs}

    def get_balance(self, address):
        url = 'https://blockchain.info/rawaddr/' + address + '?limit=0'
        try:
            logging.getLogger('Spellbook').info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            logging.getLogger('Spellbook').error('Unable to get balance of address %s from Blockchain.info: %s' % (address, ex))
            return {'error': 'Unable to get balance of address %s from Blockchain.info' % address}

        if all(key in data for key in ('final_balance', 'total_received', 'total_sent', 'n_tx')):
            balance = {'final': data['final_balance'],
                       'received': data['total_received'],
                       'sent': data['total_sent'],
                       'n_tx': data['n_tx']}
            return {'balance': balance}
        else:
            return {'error': 'Received invalid data: %s' % data}

    def get_prime_input_address(self, txid):
        url = 'https://blockchain.info/rawtx/' + str(txid)
        try:
            logging.getLogger('Spellbook').info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            logging.getLogger('Spellbook').error('Unable to get prime input address of tx %s from Blockchain.info: %s' % (txid, ex))
            return {'error': 'Unable to get prime input address of tx %s from Blockchain.info' % txid}

        if 'inputs' in data:
            tx_inputs = data['inputs']

            input_addresses = []
            for i in range(0, len(tx_inputs)):
                input_addresses.append(tx_inputs[i]['prev_out']['addr'])

            if len(input_addresses) > 0:
                prime_input_address = sorted(input_addresses)[0]
                return {'prime_input_address': prime_input_address}
            else:
                # transaction was a coinbase transaction, so there are no input addresses
                return {'prime_input_address': None}

        return {'error': 'Received invalid data: %s' % data}

    def get_utxos(self, address, confirmations=3):
        limit = 1000  # max number of utxo given by blockchain.info is 1000, there is no 'offset' parameter available
        url = 'https://blockchain.info/unspent?active=' + address + '&limit={limit}&confirmations={confirmations}'.format(address=address, limit=limit, confirmations=confirmations)
        try:
            logging.getLogger('Spellbook').info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            logging.getLogger('Spellbook').error('Unable to get utxos of address %s from %s: %s' % (address, url, ex))
            return {'error': 'Unable to get utxos of address %s from %s' % (address, url)}

        if 'unspent_outputs' in data:
            unspent_outputs = data['unspent_outputs']
        else:
            return {'error': 'Received Invalid data: %s' % data}

        utxos = []
        for output in unspent_outputs:
            if all(key in output for key in ('confirmations', 'tx_hash_big_endian', 'tx_output_n', 'value', 'script')):
                utxo = {'confirmations': output['confirmations'],
                        'output_hash': output['tx_hash_big_endian'],
                        'output_n': output['tx_output_n'],
                        'value': output['value'],
                        'script': output['script']}
                utxos.append(utxo)

        return {'utxos': sorted(utxos, key=lambda k: (k['confirmations'], k['output_hash'], k['output_n']))}
