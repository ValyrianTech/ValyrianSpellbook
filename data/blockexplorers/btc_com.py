#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from datetime import datetime
import calendar
from time import sleep

from helpers.loghelpers import LOG
from data.transaction import TX, TxInput, TxOutput
from data.explorer_api import ExplorerAPI


class BTCComAPI(ExplorerAPI):
    def __init__(self, url='', key='', testnet=False):
        super(BTCComAPI, self).__init__(key=key, testnet=testnet)

        # Set the url of the api depending on testnet or mainnet
        self.url = 'https://tchain.api.btc.com/v3' if self.testnet is True else 'https://chain.api.btc.com/v3'

    def get_latest_block(self):
        url = '{api_url}/block/latest'.format(api_url=self.url)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get latest block from BTC.com: %s' % ex)
            return {'error': 'Unable to get latest block from BTC.com'}
        data = data['data'] if data['data'] is not None else {}

        if all(key in data for key in ('height', 'hash', 'timestamp', 'mrkl_root', 'size')):
            block = {'height': data['height'],
                     'hash': data['hash'],
                     'time': data['timestamp'],
                     'merkleroot': data['mrkl_root'],
                     'size': data['size']}

            return {'block': block}
        else:
            return {'error': 'Received invalid data: %s' % data}

    def get_block_by_height(self, height):
        url = '{api_url}/block/{height}'.format(api_url=self.url, height=height)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get block %s from Blocktrail.com: %s' % (height, ex))
            return {'error': 'Unable to get block %s from Blocktrail.com' % height}
        data = data['data'] if data['data'] is not None else {}

        if all(key in data for key in ('height', 'hash', 'timestamp', 'mrkl_root', 'size')):
            block = {'height': data['height'],
                     'hash': data['hash'],
                     'time': data['timestamp'],
                     'merkleroot': data['mrkl_root'],
                     'size': data['size']}

            return {'block': block}
        else:
            return {'error': 'Received invalid data: %s' % data}

    def get_block_by_hash(self, block_hash):
        url = '{api_url}/block/{hash}'.format(api_url=self.url, hash=block_hash)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get block %s from Blocktrail.com: %s' % (block_hash, ex))
            return {'error': 'Unable to get block %s from Blocktrail.com' % block_hash}
        data = data['data'] if data['data'] is not None else {}

        if all(key in data for key in ('height', 'hash', 'timestamp', 'mrkl_root', 'size')):
            block = {'height': data['height'],
                     'hash': data['hash'],
                     'time': data['timestamp'],
                     'merkleroot': data['mrkl_root'],
                     'size': data['size']}

            return {'block': block}
        else:
            return {'error': 'Received invalid data: %s' % data}

    def get_transactions(self, address):
        pagesize = 50  # max 50 for BTC.com
        n_tx = None
        transactions = []
        page = 1

        while n_tx is None or len(transactions) < n_tx:
            url = '{api_url}/address/{address}/tx?page={page}&pagesize={pagesize}&verbose=3'.format(api_url=self.url, address=address, page=page, pagesize=pagesize)
            try:
                LOG.info('GET %s' % url)
                r = requests.get(url)
                data = r.json()
            except Exception as ex:
                LOG.error('Unable to get transactions of address %s from BTC.com: %s' % (address, ex))
                return {'error': 'Unable to get transactions of address %s from BTC.com' % address}

            data = data['data'] if data['data'] is not None else {}

            if all(key in data for key in ('total_count', 'list')):
                n_tx = data['total_count']
                transactions += data['list']
                page += 1
            else:
                return {'error': 'Received invalid data: %s' % data}

            if len(transactions) < n_tx:
                sleep(1)

        txs = []
        for transaction in transactions:
            tx = TX()
            tx.txid = transaction['hash']
            tx.block_height = transaction['block_height']
            tx.confirmations = transaction['confirmations']
            tx.wtxid = transaction['witness_hash']
            tx.lock_time = transaction['lock_time']

            for item in transaction['inputs']:
                tx_input = TxInput()
                tx_input.address = item['prev_addresses'][0] if len(item['prev_addresses']) > 0 else None
                tx_input.value = item['prev_value']
                tx_input.txid = item['prev_tx_hash']
                tx_input.n = item['prev_position'] if item['prev_position'] != -1 else None
                tx_input.script = item['script_hex']
                tx_input.sequence = item['sequence']

                tx.inputs.append(tx_input)

            for i, item in enumerate(transaction['outputs']):
                tx_output = TxOutput()
                tx_output.address = item['addresses'][0] if len(item['addresses']) > 0 else None
                tx_output.value = item['value']
                tx_output.n = i
                tx_output.spent = False if item['spent_by_tx'] is None else True
                tx_output.script = item['script_hex']

                if item['script_hex'][:2] == '6a':
                    tx_output.op_return = tx.decode_op_return(item['script_hex'])

                tx.outputs.append(tx_output)

            # Only append confirmed transactions
            if tx.block_height != -1:
                txs.append(tx.to_dict(address))
            else:
                # subtract 1 from total txs because it is unconfirmed
                n_tx -= 1

        if n_tx != len(txs):
            return {'error': 'BTC.com: Not all transactions are retrieved! expected {expected} but only got {received}'.format(expected=n_tx, received=len(txs))}
        else:
            return {'transactions': txs}

    def get_balance(self, address):
        url = '{api_url}/address/{address}'.format(api_url=self.url, address=address)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get balance of address %s from Blocktrail.com: %s' % (address, ex))
            return {'error': 'Unable to get balance of address %s from Blocktrail.com' % address}

        data = data['data'] if data['data'] is not None else {}

        if all(key in data for key in ('balance', 'received', 'sent')):
            balance = {'final': data['balance'] - data['unconfirmed_received'] + data['unconfirmed_sent'],
                       'received': data['received'] - data['unconfirmed_received'],
                       'sent': data['sent'] - data['unconfirmed_sent']}
            return {'balance': balance}
        else:
            return {'error': 'Received invalid data: %s' % data}

    def get_transaction(self, txid):
        url = '{api_url}/tx/{txid}?verbose=3'.format(api_url=self.url, txid=txid)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get transaction %s from BTC.com: %s' % (txid, ex))
            return {'error': 'Unable to get transaction %s from BTC.com' % txid}

        data = data['data'] if data['data'] is not None else {}

        # todo check key names , test by setting testnet wrong on explorers
        tx = TX()
        tx.txid = txid
        tx.wtxid = data['witness_hash']
        tx.lock_time = data['lock_time']
        tx.block_height = data['block_height'] if 'block_height' in data and data['block_height'] != -1 else None
        tx.confirmations = data['confirmations'] if 'confirmations' in data else None

        for item in data['inputs']:
            tx_input = TxInput()
            tx_input.address = item['prev_addresses'][0] if len(item['prev_addresses']) > 0 else None
            tx_input.value = item['prev_value']
            tx_input.txid = item['prev_tx_hash']
            tx_input.n = item['prev_position'] if item['prev_position'] != -1 else None
            tx_input.script = item['script_hex']
            tx_input.sequence = item['sequence']

            tx.inputs.append(tx_input)

        for i, item in enumerate(data['outputs']):
            tx_output = TxOutput()
            tx_output.address = item['addresses'][0] if len(item['addresses']) > 0 else None
            tx_output.value = item['value']
            tx_output.n = i
            tx_output.spent = False if item['spent_by_tx'] is None else True
            tx_output.script = item['script_hex']

            if item['script_hex'][:2] == '6a':
                tx_output.op_return = tx.decode_op_return(item['script_hex'])

            tx.outputs.append(tx_output)

        return {'transaction': tx.json_encodable()}

    def get_prime_input_address(self, txid):

        transaction_data = self.get_transaction(txid=txid)

        if 'transaction' in transaction_data and 'inputs' in transaction_data['transaction']:
            tx_inputs = transaction_data['transaction']['inputs']

            input_addresses = []
            for i in range(0, len(tx_inputs)):
                input_addresses.append(tx_inputs[i]['address'])

            if len(input_addresses) > 0:
                prime_input_address = sorted(input_addresses)[0]
                return {'prime_input_address': prime_input_address}

        return {'error': 'Received invalid data: %s' % transaction_data}

    def get_utxos(self, address, confirmations=3):
        pagesize = 50  # max 200 for BTC.com
        n_outputs = None
        unspent_outputs = []
        page = 1

        while n_outputs is None or len(unspent_outputs) < n_outputs:
            url = '{api_url}/address/{address}/unspent?page={page}&pagesize={pagesize}&verbose=3'.format(api_url=self.url, address=address, page=page, pagesize=pagesize)
            try:
                LOG.info('GET %s' % url)
                r = requests.get(url)
                data = r.json()
            except Exception as ex:
                LOG.error('Unable to get utxos of address %s from BTC.com: %s' % (address, ex))
                return {'error': 'Unable to get utxos of address %s block from BTC.com' % address}

            data = data['data'] if data['data'] is not None else {}

            if all(key in data for key in ('total_count', 'list')):
                n_outputs = data['total_count']
                unspent_outputs += data['list']
                page += 1
            else:
                return {'error': 'Received invalid data: %s' % data}

            # Sometimes the 'total_count' value from btc.com is just wrong!
            if not data['list']:
                n_outputs = len(unspent_outputs)

            if len(unspent_outputs) < n_outputs:
                sleep(1)

        if n_outputs != len(unspent_outputs):
            return {'error': 'Not all unspent outputs are retrieved! expected {expected} but only got {received}'.format(
                    expected=n_outputs, received=len(unspent_outputs))}

        utxos = []
        for output in unspent_outputs:
            if all(key in output for key in ('confirmations', 'tx_hash', 'tx_output_n', 'value')):
                utxo = {'confirmations': output['confirmations'],
                        'output_hash': output['tx_hash'],
                        'output_n': output['tx_output_n'],
                        'value': output['value'],
                        'script': None}

                if utxo['confirmations'] >= confirmations:
                    utxos.append(utxo)

        return {'utxos': sorted(utxos, key=lambda k: (k['confirmations'], k['output_hash'], k['output_n']))}

    @staticmethod
    def push_tx(tx):
        # Must do import here to avoid circular import
        from data.data import get_explorer_api

        LOG.warning('BTC.com api does not support broadcasting transactions, using Blockchain.info instead!')
        blockchain_info_api = get_explorer_api('blockchain.info')
        return blockchain_info_api.push_tx(tx)
