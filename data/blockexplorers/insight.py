#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests

from data.transaction import TX
from data.explorer_api import ExplorerAPI


class InsightAPI(ExplorerAPI):

    def get_latest_block(self):
        url = self.url + '/status?q=getLastBlockHash'
        try:
            logging.getLogger('Spellbook').info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            logging.getLogger('Spellbook').error('Unable to get latest blockhash from %s: %s' % (self.url, ex))
            return {'error': 'Unable to get latest blockhash from %s' % self.url}

        if 'lastblockhash' in data:
            return self.get_block_by_hash(data['lastblockhash'])
        else:
            return {'error': 'Received invalid data: %s' % data}

    def get_block_by_hash(self, block_hash):
        url = self.url + '/block/' + block_hash
        try:
            logging.getLogger('Spellbook').info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            logging.getLogger('Spellbook').error('Unable to get block %s from %s: %s' % (block_hash, self.url, ex))
            return {'error': 'Unable to get block %s from %s' % (block_hash, self.url)}

        block = {}
        if all(key in data for key in ('height', 'hash', 'time', 'merkleroot', 'size')):
            block['height'] = data['height']
            block['hash'] = data['hash']
            block['time'] = data['time']
            block['merkleroot'] = data['merkleroot']
            block['size'] = data['size']
            return {'block': block}
        else:
            return {'error': 'Received invalid data: %s' % data}

    def get_block_by_height(self, height):
        url = self.url + '/block-index/' + str(height)
        try:
            logging.getLogger('Spellbook').info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            logging.getLogger('Spellbook').error('Unable to get hash of block at height %s from %s: %s' % (height, self.url, ex))
            return {'error': 'Unable to get hash of block at height %s from %s' % (height, self.url)}

        if 'blockHash' in data:
            return self.get_block_by_hash(data['blockHash'])
        else:
            return {'error': 'Received invalid data: %s' % data}

    def get_transactions(self, address):
        limit = 10  # number of tx given by insight is 10
        n_tx = None
        transactions = []

        latest_block_height = self.get_latest_block_height()
        if latest_block_height is None:
            return {'error': 'Unable to get latest block height'}

        i = 0
        while n_tx is None or len(transactions) < n_tx:
            url = self.url + '/addrs/' + address + '/txs?from=' + str(limit*i) + '&to=' + str(limit*(i+1))
            try:
                logging.getLogger('Spellbook').info('GET %s' % url)
                r = requests.get(url)
                data = r.json()
            except Exception as ex:
                logging.getLogger('Spellbook').error('Unable to get transactions of address %s from %s: %s' % (address, url, ex))
                return {'error': 'Unable to get transactions of address %s from %s' % (address, url)}

            if all(key in data for key in ('totalItems', 'items')):
                n_tx = data['totalItems']
                transactions += data['items']
                i += 1
            else:
                return {'error': 'Received Invalid data: %s' % data}

        txs = []
        for transaction in transactions:
            tx = TX()
            tx.txid = transaction['txid']
            tx.confirmations = transaction['confirmations']
            tx.block_height = latest_block_height - tx.confirmations + 1 if transaction['confirmations'] >= 1 else None

            for tx_input in transaction['vin']:
                tx_in = {'address': tx_input['addr'],
                         'value': tx_input['valueSat']}
                tx.inputs.append(tx_in)

            for out in transaction['vout']:
                tx_out = {
                    'address': out['scriptPubKey']['addresses'][0] if 'addresses' in out['scriptPubKey'] else None,
                    'value': int(int(out['value'][:-9]) * 1e8 + int(out['value'][-8:])),
                    'spent': True if 'spentTxId' in out and out['spentTxId'] is not None else False}

                if out['scriptPubKey']['hex'][:2] == '6a':
                    tx_out['op_return'] = tx.decode_op_return(out['scriptPubKey']['hex'])

                tx.outputs.append(tx_out)

            txs.insert(0, tx.to_dict(address))

        if n_tx != len(txs):
            return {'error': 'Not all transactions are retrieved! expected {expected} but only got {received}'.format(
                    expected=n_tx, received=len(txs))}
        else:
            return {'transactions': txs}

    def get_balance(self, address):
        # Insight calculates the total received and total sent wrong (doesn't exclude change to the same address),
        # so we need to get the transactions and calculate the final balance ourselves
        data = self.get_transactions(address)
        if 'transactions' in data:
            txs = data['transactions']
            final_balance = 0
            received = 0

            for tx in txs:
                for output in tx['outputs']:
                    if output['address'] == address and output['spent'] is False:
                        final_balance += output['value']

                if tx['receiving'] is True and tx['confirmations'] > 0:
                    received += tx['receivedValue']

            balance = {'final': final_balance,
                       'received': received,
                       'sent': received - final_balance,
                       'n_tx': len(txs)}

            return {'balance': balance}
        else:
            return {'error': 'Received invalid data: %s' % data}

    def get_prime_input_address(self, txid):
        url = self.url + '/tx/' + str(txid)
        try:
            logging.getLogger('Spellbook').info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            logging.getLogger('Spellbook').error('Unable to get prime input address of transaction %s from %s: %s' % (txid, self.url, ex))
            return {'error': 'Unable to get prime input address of transaction %s from %s' % (txid, self.url)}

        if 'vin' in data:
            tx_inputs = data['vin']

            input_addresses = []
            for i in range(0, len(tx_inputs)):
                input_addresses.append(tx_inputs[i]['addr'])

            if len(input_addresses) > 0:
                prime_input_address = sorted(input_addresses)[0]
                return {'prime_input_address': prime_input_address}

        return {'error': 'Received invalid data: %s' % data}

    def get_utxos(self, address, confirmations=3):
        url = self.url + '/addrs/' + address + '/utxo?noCache=1'
        try:
            logging.getLogger('Spellbook').info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            logging.getLogger('Spellbook').error('Unable to get utxos of address %s from %s: %s' % (address, url, ex))
            return {'error': 'Unable to get utxos of address %s from %s' % (address, url)}

        utxos = []
        for output in data:
            if all(key in output for key in ('confirmations', 'txid', 'vout', 'satoshis', 'scriptPubKey')):
                utxo = {'confirmations': output['confirmations'],
                        'output_hash': output['txid'],
                        'output_n': output['vout'],
                        'value': output['satoshis'],
                        'script': output['scriptPubKey']}

                if utxo['confirmations'] >= confirmations:
                    utxos.append(utxo)

        return {'utxos': sorted(utxos, key=lambda k: (k['confirmations'], k['output_hash'], k['output_n']))}

    def push_tx(self, tx):
        url = '{api_url}/tx/send'.format(api_url=self.url)
        logging.getLogger('Spellbook').info('POST %s' % url)
        try:
            r = requests.post(url, data=dict(rawtx=tx))
        except Exception as ex:
            logging.getLogger('Spellbook').error('Unable to push tx via %s: %s' % (self.url, ex))
            return {'error': 'Unable to push tx via %s: %s' % (self.url, ex)}

        try:
            data = r.json()
        except ValueError:
            data = r.text

        if r.status_code == 200 and isinstance(data, dict) and 'txid' in data:
            return {'success': True}
        else:
            logging.getLogger('Spellbook').error('Unable to push tx via %s: %s' % (self.url, data))
            return {'error': 'Unable to push tx via %s: %s' % (self.url, data)}
