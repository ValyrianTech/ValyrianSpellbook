#!/usr/bin/env python
"""Blocktrail.com blockchain explorer API client."""

import calendar
from datetime import datetime
from time import sleep

import requests

from data.explorer_api import ExplorerAPI
from data.transaction import TX, TxInput, TxOutput
from helpers.loghelpers import LOG


class BlocktrailComAPI(ExplorerAPI):
    """
    Blocktrail.com block explorer API client.

    Initializes the API client with URL, optional key, and testnet flag.
    """
    def __init__(self, url='', key='', testnet=False):
        super().__init__(key=key, testnet=testnet)

        # Set the url of the api depending on testnet or mainnet
        self.url = 'https://api.blocktrail.com/v1/tBTC' if self.testnet is True else 'https://api.blocktrail.com/v1/BTC'

    def get_latest_block(self):
        """Retrieve the latest block from the blockchain explorer."""
        url = f'{self.url}/block/latest?api_key={self.key}'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get latest block from Blocktrail.com: {ex}')
            return {'error': 'Unable to get latest block from Blocktrail.com'}

        if all(key in data for key in ('height', 'hash')):
            return self.get_block_by_hash(data['hash'])
        else:
            return {'error': f'Received invalid data: {data}'}

    def get_block_by_height(self, height):
        """Retrieve a block by its height from the blockchain explorer."""
        url = f'{self.url}/block/{height}?api_key={self.key}'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get block {height} from Blocktrail.com: {ex}')
            return {'error': f'Unable to get block {height} from Blocktrail.com'}

        if all(key in data for key in ('height', 'hash', 'block_time', 'merkleroot', 'byte_size')):
            block = {'height': data['height'],
                     'hash': data['hash'],
                     'time': calendar.timegm(datetime.strptime(data['block_time'], "%Y-%m-%dT%H:%M:%S%z").utctimetuple()),
                     'merkleroot': data['merkleroot'],
                     'size': data['byte_size']}

            return {'block': block}
        else:
            return {'error': f'Received invalid data: {data}'}

    def get_block_by_hash(self, block_hash):
        """Retrieve a block by its hash from the blockchain explorer."""
        url = f'{self.url}/block/{block_hash}?api_key={self.key}'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get block {block_hash} from Blocktrail.com: {ex}')
            return {'error': f'Unable to get block {block_hash} from Blocktrail.com'}

        if all(key in data for key in ('height', 'hash', 'block_time', 'merkleroot', 'byte_size')):
            block = {'height': data['height'],
                     'hash': data['hash'],
                     'time': calendar.timegm(datetime.strptime(data['block_time'], "%Y-%m-%dT%H:%M:%S%z").utctimetuple()),
                     'merkleroot': data['merkleroot'],
                     'size': data['byte_size']}

            return {'block': block}
        else:
            return {'error': f'Received invalid data: {data}'}

    def get_transactions(self, address):
        """Retrieve all transactions for a given address from the explorer."""
        limit = 200  # max 200 for Blocktrail.com
        n_tx = None
        transactions = []
        page = 1

        while n_tx is None or len(transactions) < n_tx:
            url = f'{self.url}/address/{address}/transactions?api_key={self.key}&limit={limit}&page={page}&sort_dir=asc'
            try:
                LOG.info(f'GET {url}')
                r = requests.get(url)
                data = r.json()
            except (ValueError, KeyError, TypeError, OSError) as ex:
                LOG.error(f'Unable to get transactions of address {address} from Blocktrail.com: {ex}')
                return {'error': f'Unable to get transactions of address {address} block from Blocktrail.com'}

            if all(key in data for key in ('total', 'data')):
                n_tx = data['total']
                transactions += data['data']
                page += 1
            else:
                return {'error': f'Received invalid data: {data}'}

            if len(transactions) < n_tx:
                sleep(1)

        txs = []
        for transaction in transactions:
            tx = TX()
            tx.txid = transaction['hash']
            tx.block_height = transaction['block_height']
            tx.confirmations = transaction['confirmations']
            tx.lock_time = 0  # Blocktrail does not provide the lock_time

            for item in transaction['inputs']:
                tx_input = TxInput()
                tx_input.address = item['address']
                tx_input.value = item['value'] if item['type'] != 'coinbase' else 0
                tx_input.txid = item['output_hash']
                tx_input.n = item['output_index'] if item['type'] != 'coinbase' else None
                tx_input.script = item['script_signature']
                tx_input.sequence = None  # Blocktrail does not provide the sequence of a transaction input when requesting all transactions of an address

                tx.inputs.append(tx_input)

            for item in transaction['outputs']:
                tx_output = TxOutput()
                tx_output.address = item['address']
                tx_output.value = item['value']
                tx_output.n = item['index']
                tx_output.spent = not item['spent_hash'] is None
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
            LOG.warning(f'Blocktrail.com: Not all transactions are retrieved! expected {n_tx} but only got {len(txs)}')
            return {'transactions': txs}
        else:
            return {'transactions': txs}

    def get_balance(self, address):
        """Retrieve the balance (final, received, sent) for a given address."""
        url = f'{self.url}/address/{address}?api_key={self.key}'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get balance of address {address} from Blocktrail.com: {ex}')
            return {'error': f'Unable to get balance of address {address} from Blocktrail.com'}

        if all(key in data for key in ('balance', 'received', 'sent')):
            balance = {'final': data['balance'],
                       'received': data['received'],
                       'sent': data['sent']}
            return {'balance': balance}
        else:
            return {'error': f'Received invalid data: {data}'}

    def get_transaction(self, txid):
        """Retrieve a single transaction by its txid from the explorer."""
        url = f'{self.url}/transaction/{txid}?api_key={self.key}'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get transaction {txid} from Blocktrail.com: {ex}')
            return {'error': f'Unable to get transaction {txid} from Blocktrail.com'}

        tx = TX()
        tx.txid = txid
        tx.lock_time = 0  # BlockTrail does not provide the lock_time
        tx.block_height = data.get('block_height', None)

        for item in data['inputs']:
            tx_input = TxInput()
            tx_input.address = item['address']
            tx_input.value = item['value'] if item['type'] != 'coinbase' else 0
            tx_input.txid = item['output_hash']
            tx_input.n = item['output_index'] if item['type'] != 'coinbase' else None
            tx_input.script = item['script_signature']
            tx_input.sequence = item['sequence']

            tx.inputs.append(tx_input)

        for item in data['outputs']:
            tx_output = TxOutput()
            tx_output.address = item['address']
            tx_output.value = item['value']
            tx_output.n = item['index']
            tx_output.spent = not item['spent_hash'] is None
            tx_output.script = item['script_hex']
            if item['script_hex'][:2] == '6a':
                tx_output.op_return = tx.decode_op_return(item['script_hex'])

            tx.outputs.append(tx_output)

        tx.confirmations = data.get('confirmations', None)

        return {'transaction': tx.json_encodable()}

    def get_prime_input_address(self, txid):
        """Retrieve the prime input address of a transaction by txid."""
        url = f'{self.url}/transaction/{txid}?api_key={self.key}'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get prime input address from transaction {txid} from Blocktrail.com: {ex}')
            return {'error': f'Unable to get prime input address from transaction {txid} from Blocktrail.com'}

        if 'inputs' in data:
            tx_inputs = data['inputs']

            input_addresses = []
            for i in range(len(tx_inputs)):
                input_addresses.append(tx_inputs[i]['address'])

            if len(input_addresses) > 0:
                prime_input_address = min(input_addresses)
                return {'prime_input_address': prime_input_address}

        return {'error': f'Received invalid data: {data}'}

    def get_utxos(self, address, confirmations=3):
        """Retrieve unspent transaction outputs (UTXOs) for a given address."""
        limit = 200  # max 200 for Blocktrail.com
        n_outputs = None
        unspent_outputs = []
        page = 1

        while n_outputs is None or len(unspent_outputs) < n_outputs:
            url = f'{self.url}/address/{address}/unspent-outputs?api_key={self.key}&limit={limit}&page={page}&sort_dir=asc'
            try:
                LOG.info(f'GET {url}')
                r = requests.get(url)
                data = r.json()
            except (ValueError, KeyError, TypeError, OSError) as ex:
                LOG.error(f'Unable to get utxos of address {address} from Blocktrail.com: {ex}')
                return {'error': f'Unable to get utxos of address {address} block from Blocktrail.com'}

            if all(key in data for key in ('total', 'data')):
                n_outputs = data['total']
                unspent_outputs += data['data']
                page += 1
            else:
                return {'error': f'Received invalid data: {data}'}

            if len(unspent_outputs) < n_outputs:
                sleep(1)

        if n_outputs != len(unspent_outputs):
            return {'error': f'Not all unspent outputs are retrieved! expected {n_outputs} but only got {len(unspent_outputs)}'}

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
        url = f'{self.url}/fee-per-kb?api_key={self.key}'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get optimal fee per kb from Blocktrail.com: {ex}')
            return {'error': 'Unable to get optimal fee per kb from Blocktrail.com'}

        return data

    @staticmethod
    def push_tx(tx):
        """Broadcast a raw transaction via Blockchain.info (Blocktrail does not support broadcasting)."""
        # Must do import here to avoid circular import
        from data.data import get_explorer_api

        LOG.warning('Blocktrail.com api does not support broadcasting transactions, using Blockchain.info instead!')
        blockchain_info_api = get_explorer_api('blockchain.info')
        return blockchain_info_api.push_tx(tx)
