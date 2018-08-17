#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from datetime import datetime
import calendar
from time import sleep

from helpers.loghelpers import LOG
from data.transaction import TX, TxInput, TxOutput
from data.explorer_api import ExplorerAPI


class BlocktrailComAPI(ExplorerAPI):
    def __init__(self, url='', key='', testnet=False):
        super(BlocktrailComAPI, self).__init__(key=key, testnet=testnet)

        # Set the url of the api depending on testnet or mainnet
        self.url = 'https://api.blocktrail.com/v1/tBTC' if self.testnet is True else 'https://api.blocktrail.com/v1/BTC'

    def get_latest_block(self):
        url = '{api_url}/block/latest?api_key={api_key}'.format(api_url=self.url, api_key=self.key)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get latest block from Blocktrail.com: %s' % ex)
            return {'error': 'Unable to get latest block from Blocktrail.com'}

        if all(key in data for key in ('height', 'hash')):
            return self.get_block_by_hash(data['hash'])
        else:
            return {'error': 'Received invalid data: %s' % data}

    def get_block_by_height(self, height):
        url = '{api_url}/block/{height}?api_key={api_key}'.format(api_url=self.url, height=height, api_key=self.key)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get block %s from Blocktrail.com: %s' % (height, ex))
            return {'error': 'Unable to get block %s from Blocktrail.com' % height}

        if all(key in data for key in ('height', 'hash', 'block_time', 'merkleroot', 'byte_size')):
            block = {'height': data['height'],
                     'hash': data['hash'],
                     'time': calendar.timegm(datetime.strptime(data['block_time'], "%Y-%m-%dT%H:%M:%S+0000").utctimetuple()),
                     'merkleroot': data['merkleroot'],
                     'size': data['byte_size']}

            return {'block': block}
        else:
            return {'error': 'Received invalid data: %s' % data}

    def get_block_by_hash(self, block_hash):
        url = '{api_url}/block/{hash}?api_key={api_key}'.format(api_url=self.url, hash=block_hash, api_key=self.key)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get block %s from Blocktrail.com: %s' % (block_hash, ex))
            return {'error': 'Unable to get block %s from Blocktrail.com' % block_hash}

        if all(key in data for key in ('height', 'hash', 'block_time', 'merkleroot', 'byte_size')):
            block = {'height': data['height'],
                     'hash': data['hash'],
                     'time': calendar.timegm(datetime.strptime(data['block_time'], "%Y-%m-%dT%H:%M:%S+0000").utctimetuple()),
                     'merkleroot': data['merkleroot'],
                     'size': data['byte_size']}

            return {'block': block}
        else:
            return {'error': 'Received invalid data: %s' % data}

    def get_transactions(self, address):
        limit = 200  # max 200 for Blocktrail.com
        n_tx = None
        transactions = []
        page = 1

        while n_tx is None or len(transactions) < n_tx:
            url = '{api_url}/address/{address}/transactions?api_key={api_key}&limit={limit}&page={page}&sort_dir=asc'.format(api_url=self.url, address=address, api_key=self.key, limit=limit, page=page)
            try:
                LOG.info('GET %s' % url)
                r = requests.get(url)
                data = r.json()
            except Exception as ex:
                LOG.error('Unable to get transactions of address %s from Blocktrail.com: %s' % (address, ex))
                return {'error': 'Unable to get transactions of address %s block from Blocktrail.com' % address}

            if all(key in data for key in ('total', 'data')):
                n_tx = data['total']
                transactions += data['data']
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

            for item in transaction['inputs']:
                tx_input = TxInput()
                tx_input.address = item['address']
                tx_input.value = item['value']
                tx_input.txid = item['output_hash']
                tx_input.n = item['output_index']
                tx_input.script = item['script_signature']
                tx_input.sequence = None  # Blocktrail does not provide the sequence of a transaction input when requesting all transactions of an address

                tx.inputs.append(tx_input)

            for item in transaction['outputs']:
                tx_output = TxOutput()
                tx_output.address = item['address']
                tx_output.value = item['value']
                tx_output.n = item['index']
                tx_output.spent = False if item['spent_hash'] is None else True
                tx_output.script = item['script_hex']

                if item['script_hex'][:2] == '6a':
                    tx_output.op_return = tx.decode_op_return(item['script_hex'])

                tx.outputs.append(tx_output)

            # Only append confirmed transactions
            if tx.block_height is not None:
                txs.append(tx.to_dict(address))
            else:
                # subtract 1 from total txs because it is unconfirmed
                n_tx -= 1

        if n_tx != len(txs):
            # Blocktrail seems to have some issues not returning the correct total number of transactions, yet all transactions are present???
            LOG.warning('Blocktrail.com: Not all transactions are retrieved! expected {expected} but only got {received}'.format(expected=n_tx, received=len(txs)))
            return {'transactions': txs}
        else:
            return {'transactions': txs}

    def get_balance(self, address):
        url = '{api_url}/address/{address}?api_key={api_key}'.format(api_url=self.url, address=address, api_key=self.key)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get balance of address %s from Blocktrail.com: %s' % (address, ex))
            return {'error': 'Unable to get balance of address %s from Blocktrail.com' % address}

        if all(key in data for key in ('balance', 'received', 'sent')):
            balance = {'final': data['balance'],
                       'received': data['received'],
                       'sent': data['sent']}
            return {'balance': balance}
        else:
            return {'error': 'Received invalid data: %s' % data}

    def get_transaction(self, txid):
        url = '{api_url}/transaction/{txid}?api_key={api_key}'.format(api_url=self.url, txid=txid, api_key=self.key)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get transaction %s from Blocktrail.com: %s' % (txid, ex))
            return {'error': 'Unable to get transaction %s from Blocktrail.com' % txid}

        tx = TX()
        tx.txid = txid
        tx.block_height = data['block_height'] if 'block_height' in data else None

        for item in data['inputs']:
            tx_input = TxInput()
            tx_input.address = item['address']
            tx_input.value = item['value']
            tx_input.txid = item['output_hash']
            tx_input.n = item['output_index']
            tx_input.script = item['script_signature']
            tx_input.sequence = item['sequence']

            tx.inputs.append(tx_input)

        for item in data['outputs']:
            tx_output = TxOutput()
            tx_output.address = item['address']
            tx_output.value = item['value']
            tx_output.n = item['index']
            tx_output.spent = False if item['spent_hash'] is None else True
            tx_output.script = item['script_hex']
            if item['script_hex'][:2] == '6a':
                tx_output.op_return = tx.decode_op_return(item['script_hex'])

            tx.outputs.append(tx_output)

        tx.confirmations = data['confirmations'] if 'confirmations' in data else None

        return {'transaction': tx.json_encodable()}

    def get_prime_input_address(self, txid):
        url = '{api_url}/transaction/{txid}?api_key={api_key}'.format(api_url=self.url, txid=txid, api_key=self.key)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get prime input address from transaction %s from Blocktrail.com: %s' % (txid, ex))
            return {'error': 'Unable to get prime input address from transaction %s from Blocktrail.com' % txid}

        if 'inputs' in data:
            tx_inputs = data['inputs']

            input_addresses = []
            for i in range(0, len(tx_inputs)):
                input_addresses.append(tx_inputs[i]['address'])

            if len(input_addresses) > 0:
                prime_input_address = sorted(input_addresses)[0]
                return {'prime_input_address': prime_input_address}

        return {'error': 'Received invalid data: %s' % data}

    def get_utxos(self, address, confirmations=3):
        limit = 200  # max 200 for Blocktrail.com
        n_outputs = None
        unspent_outputs = []
        page = 1

        while n_outputs is None or len(unspent_outputs) < n_outputs:
            url = '{api_url}/address/{address}/unspent-outputs?api_key={api_key}&limit={limit}&page={page}&sort_dir=asc'.format(api_url=self.url, address=address, api_key=self.key, limit=limit, page=page)
            try:
                LOG.info('GET %s' % url)
                r = requests.get(url)
                data = r.json()
            except Exception as ex:
                LOG.error('Unable to get utxos of address %s from Blocktrail.com: %s' % (address, ex))
                return {'error': 'Unable to get utxos of address %s block from Blocktrail.com' % address}

            if all(key in data for key in ('total', 'data')):
                n_outputs = data['total']
                unspent_outputs += data['data']
                page += 1
            else:
                return {'error': 'Received invalid data: %s' % data}

            if len(unspent_outputs) < n_outputs:
                sleep(1)

        if n_outputs != len(unspent_outputs):
            return {'error': 'Not all unspent outputs are retrieved! expected {expected} but only got {received}'.format(
                    expected=n_outputs, received=len(unspent_outputs))}

        utxos = []
        for output in unspent_outputs:
            if all(key in output for key in ('confirmations', 'hash', 'index', 'value', 'script_hex')):
                utxo = {'confirmations': output['confirmations'],
                        'output_hash': output['hash'],
                        'output_n': output['index'],
                        'value': output['value'],
                        'script': output['script_hex']}

                if utxo['confirmations'] >= confirmations:
                    utxos.append(utxo)

        return {'utxos': sorted(utxos, key=lambda k: (k['confirmations'], k['output_hash'], k['output_n']))}

    def get_recommended_fee(self):
        """
        Get the recommended fee per KB

        :return: a dict containing 'optimal', 'high_priority', 'low_priority' and 'min_relay_fee'
        """
        url = '{api_url}/fee-per-kb?api_key={api_key}'.format(api_url=self.url, api_key=self.key)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get optimal fee per kb from Blocktrail.com: %s' % ex)
            return {'error': 'Unable to get optimal fee per kb from Blocktrail.com'}

        return data

    @staticmethod
    def push_tx(tx):
        # Must do import here to avoid circular import
        from data.data import get_explorer_api

        LOG.warning('Blocktrail.com api does not support broadcasting transactions, using Blockchain.info instead!')
        blockchain_info_api = get_explorer_api('blockchain.info')
        return blockchain_info_api.push_tx(tx)
