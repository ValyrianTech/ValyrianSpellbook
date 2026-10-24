#!/usr/bin/env python
"""SoChain (formerly Chain.so) block explorer API v3 client."""

import requests

from data.blockexplorers.explorer_http import DEFAULT_TIMEOUT
from data.explorer_api import ExplorerAPI
from data.transaction import TX, TxInput, TxOutput
from helpers.conversionhelpers import btc2satoshis
from helpers.loghelpers import LOG

# Rows per page when listing an address's transactions (the API allows 1-100)
TRANSACTIONS_PAGE_SIZE = 100

# The API gives unspent outputs ten per page
UTXOS_PAGE_SIZE = 10


class ChainSoAPI(ExplorerAPI):
    """
    SoChain block explorer API v3 client (https://sochain.com/api/v3).

    The API key is optional: without one, lookups work up to SoChain's keyless daily limit.
    Keys are made at https://sochain.com/dashboard and are sent in the API-KEY header.

    SoChain's Bitcoin testnet (BTCTEST) is testnet4, not testnet3, so on testnet every call
    returns an error and the next explorer is used.
    """
    def __init__(self, url='', key='', testnet=False):
        super().__init__(url=url, key=key, testnet=testnet)
        self.network = 'BTC'
        self.url = 'https://sochain.com/api/v3'

    def _get(self, path, params=None):
        """GET an API v3 endpoint: returns {'data': ...} or {'error': ...}."""
        if self.testnet:
            return {'error': 'SoChain does not serve Bitcoin testnet3'}

        url = f'{self.url}/{path}'
        headers = {'API-KEY': self.key} if self.key else None
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url, params=params, headers=headers, timeout=DEFAULT_TIMEOUT)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError, requests.RequestException) as ex:
            LOG.error(f'Unable to get {path} from SoChain: {ex}')
            return {'error': f'Unable to get {path} from SoChain'}

        if not isinstance(data, dict) or data.get('status') != 'success' or not isinstance(data.get('data'), dict):
            LOG.error(f'Invalid response data from SoChain: {data}')
            return {'error': f'Invalid response data from SoChain: {data}'}

        return {'data': data['data']}

    def get_transactions(self, address):
        """Retrieve all confirmed transactions for a given address from the explorer."""
        txids = []
        params = {'unconfirmed': 'exclude', 'page_size': TRANSACTIONS_PAGE_SIZE}
        while True:
            response = self._get(f'transactions/{self.network}/{address}', params=params)
            if 'error' in response:
                return {'error': f'Unable to get transactions of address {address} from SoChain'}

            data = response['data']
            txids.extend(transaction['hash'] for transaction in data.get('transactions', []))

            if not data.get('next_cursor'):
                break
            params = {'cursor': data['next_cursor']}

        txs = []
        for txid in txids:
            tx = self._get_tx(txid=txid)
            if not isinstance(tx, TX):
                return {'error': f'Unable to get transaction {txid} of address {address} from SoChain'}
            txs.append(tx.to_dict(address=address))

        LOG.info(f'Retrieved {len(txs)} transactions')
        return {'transactions': txs}

    def get_block_by_height(self, height):
        """Retrieve a block by its height from the blockchain explorer."""
        return self._get_block(height_or_hash=height)

    def get_block_by_hash(self, block_hash):
        """Retrieve a block by its hash from the blockchain explorer."""
        return self._get_block(height_or_hash=block_hash)

    def _get_block(self, height_or_hash):
        """Retrieve a block by its height or its hash."""
        response = self._get(f'block/{self.network}/{height_or_hash}')
        if 'error' in response:
            return {'error': f'Unable to get block {height_or_hash} from SoChain'}

        data = response['data']

        if all(key in data for key in ('height', 'hash', 'time', 'merkleroot', 'size')):
            block = {'height': data['height'],
                     'hash': data['hash'],
                     'time': data['time'],
                     'merkleroot': data['merkleroot'],
                     'size': data['size']}
            return {'block': block}
        else:
            return {'error': f'Received invalid data: {data}'}

    def _get_latest_block_height(self):
        """Return the newest block's height, or None."""
        response = self._get(f'network_info/{self.network}')
        if 'error' in response:
            return None
        return response['data'].get('block_count')

    def get_latest_block(self):
        """Retrieve the latest block from the blockchain explorer."""
        block_height = self._get_latest_block_height()
        if block_height is None:
            return {'error': 'Unable to get latest block from SoChain'}

        return self.get_block_by_height(height=block_height)

    def get_utxos(self, address, confirmations=3):
        """Retrieve unspent transaction outputs (UTXOs) for a given address."""
        latest_block_height = self._get_latest_block_height()
        if latest_block_height is None:
            return {'error': 'Unable to get latest block height from SoChain'}

        utxos = []
        page = 1
        while True:
            response = self._get(f'unspent_outputs/{self.network}/{address}/{page}')
            if 'error' in response:
                return {'error': f'Unable to get utxos of address {address} from SoChain'}

            outputs = response['data'].get('outputs', [])
            for output in outputs:
                if all(key in output for key in ('hash', 'index', 'value', 'script', 'block')):
                    utxo = {'confirmations': latest_block_height - output['block'] + 1 if output['block'] is not None else 0,
                            'output_hash': output['hash'],
                            'output_n': output['index'],
                            'value': btc2satoshis(btc=output['value']),
                            'script': output['script']}

                    if utxo['confirmations'] >= confirmations:
                        utxos.append(utxo)

            if len(outputs) < UTXOS_PAGE_SIZE:
                break
            page += 1

        return {'utxos': sorted(utxos, key=lambda k: (k['confirmations'], k['output_hash'], k['output_n']))}

    def get_balance(self, address):
        """Retrieve the balance (final, received, sent) for a given address."""
        response = self._get(f'address_summary/{self.network}/{address}')
        if 'error' in response:
            return {'error': f'Unable to get balance of address {address} from SoChain'}

        data = response['data']
        if not all(key in data for key in ('confirmed_balance', 'confirmed_received')):
            return {'error': f'Received invalid data: {data}'}

        final_balance = btc2satoshis(btc=data['confirmed_balance'])
        received_balance = btc2satoshis(btc=data['confirmed_received'])
        sent_balance = received_balance - final_balance

        balance = {'final': final_balance,
                   'received': received_balance,
                   'sent': sent_balance}

        return {'balance': balance}

    def get_prime_input_address(self, txid):
        """Retrieve the prime input address of a transaction by txid."""
        tx = self._get_tx(txid=txid)

        if isinstance(tx, TX):
            input_addresses = [tx_input.address for tx_input in tx.inputs if tx_input.address is not None]
            if len(input_addresses) > 0:
                return {'prime_input_address': min(input_addresses)}

        return {'error': f'Received invalid data: {tx}'}

    def get_transaction(self, txid):
        """Retrieve a single transaction by its txid from the explorer."""
        tx = self._get_tx(txid=txid)
        if not isinstance(tx, TX):
            return tx

        return {'transaction': tx.json_encodable()}

    def _get_tx(self, txid):
        """Return the transaction as a TX object, or a dict with an error."""
        response = self._get(f'transaction/{self.network}/{txid}')
        if 'error' in response:
            return {'error': f'Unable to get transaction {txid} from SoChain'}

        try:
            return self.parse_transaction(data=response['data'])
        except (ValueError, KeyError, TypeError) as ex:
            LOG.error(f'Invalid data for transaction {txid} from SoChain: {ex}')
            return {'error': f'Received invalid data for transaction {txid} from SoChain'}

    @staticmethod
    def parse_transaction(data):
        """Parse an API v3 transaction into a TX object."""
        tx = TX()
        tx.txid = data['hash']
        tx.lock_time = data['locktime']
        tx.block_height = data['block_height']
        tx.confirmations = data['confirmations']

        for item in data['inputs']:
            tx_input = TxInput()
            previous_output = item['previous_output']
            tx_input.address = item['address']
            tx_input.value = btc2satoshis(btc=item['value']) if previous_output is not None else 0
            tx_input.n = previous_output['index'] if previous_output is not None else None
            tx_input.txid = previous_output['hash'] if previous_output is not None else None
            tx_input.script = item['scriptSig']['hex']
            tx_input.sequence = item.get('sequence')

            tx.inputs.append(tx_input)

        for item in data['outputs']:
            tx_output = TxOutput()
            tx_output.address = item['address'] if item['address'] != 'op_return' else None
            tx_output.value = btc2satoshis(btc=item['value'])
            tx_output.n = item['index']
            tx_output.spent = item['spent'] is not None
            tx_output.script = item['script']['hex']
            if tx_output.script[:2] == '6a':
                tx_output.op_return = tx.decode_op_return(tx_output.script)

            tx.outputs.append(tx_output)

        return tx

    def push_tx(self, tx):
        """SoChain's API has no broadcasting, so this returns an error and the next explorer is used."""
        return {'error': 'SoChain does not broadcast transactions'}
