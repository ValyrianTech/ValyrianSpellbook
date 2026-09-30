#!/usr/bin/env python
"""Blockstream.info block explorer API client."""
from time import sleep

import requests

from data.explorer_api import ExplorerAPI
from data.transaction import TX, TxInput, TxOutput
from helpers.loghelpers import LOG


class BlockstreamAPI(ExplorerAPI):
    """
    Blockstream.info block explorer API client.

    Initializes the API client with URL, optional key, and testnet flag.
    """
    def __init__(self, url='', key='', testnet=False):
        super().__init__(url=url, testnet=testnet)
        # Set the url of the api depending on testnet or mainnet
        self.url = 'https://blockstream.info/testnet/api' if self.testnet is True else 'https://blockstream.info/api'

    def get_latest_block(self):
        """Retrieve the latest block from the blockchain explorer."""
        url = self.url + '/blocks/tip/hash'
        LOG.info(f'GET {url}')
        try:
            r = requests.get(url)
            block_hash = r.text
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get latest block_hash from Blockstream.info: {ex}')
            return {'error': 'Unable to get latest block_hash from Blockstream.info'}

        return self.get_block_by_hash(block_hash=block_hash)

    def get_block_by_hash(self, block_hash):
        """Retrieve a block by its hash from the blockchain explorer."""
        url = self.url + f'/block/{block_hash}'
        LOG.info(f'GET {url}')
        try:
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get block {block_hash} from Blockstream.info: {ex}')
            return {'error': f'Unable to get block {block_hash} from Blockstream.info'}

        if all(key in data for key in ('height', 'id', 'timestamp', 'merkle_root', 'size')):
            block = {'height': data['height'],
                     'hash': data['id'],
                     'time': data['timestamp'],
                     'merkleroot': data['merkle_root'],
                     'size': data['size']}  # Todo weight?
            return {'block': block}
        else:
            return {'error': f'Received invalid data: {data}'}

    def get_block_by_height(self, height):
        """Retrieve a block by its height from the blockchain explorer."""
        url = self.url + f'/block-height/{height}'
        LOG.info(f'GET {url}')
        try:
            r = requests.get(url)
            block_hash = r.text
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get block {height} from Blockstream.info: {ex}')
            return {'error': f'Unable to get block {height} from Blockstream.info'}

        return self.get_block_by_hash(block_hash=block_hash)

    def get_transactions(self, address):
        """Retrieve all transactions for a given address from the explorer."""
        url = self.url + '/blocks/tip/height'
        LOG.info(f'GET {url}')
        try:
            r = requests.get(url)
            latest_block_height = int(r.text)
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get latest block_height from Blockstream.info: {ex}')
            return {'error': 'Unable to get latest block_height from Blockstream.info'}

        url = self.url + f'/address/{address}/txs'
        LOG.info(f'GET {url}')
        try:
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get address transactions for {address} from Blockstream.info: {ex}')
            return {'error': f'Unable to get address transactions for {address} from Blockstream.info'}

        txs = []
        for transaction in data:
            if transaction['status']['confirmed'] is True:
                txs.append(self.parse_transaction(data=transaction, latest_block_height=latest_block_height).to_dict(address=address))

        while len(data) >= 25:
            sleep(0.5)
            last_txid = data[-1]['txid']
            url = self.url + f'/address/{address}/txs/chain/{last_txid}'
            LOG.info(f'GET {url}')
            try:
                r = requests.get(url)
                data = r.json()
            except (ValueError, KeyError, TypeError, OSError) as ex:
                LOG.error(f'Unable to get address transactions for {address} from Blockstream.info: {ex}')
                return {'error': f'Unable to get address transactions for {address} from Blockstream.info'}

            for transaction in data:
                if transaction['status']['confirmed'] is True:
                    txs.append(self.parse_transaction(data=transaction, latest_block_height=latest_block_height).to_dict(address=address))

        LOG.info(f'Retrieved {len(txs)} transactions')
        return {'transactions': txs}

    def get_balance(self, address):
        """Retrieve the balance (final, received, sent) for a given address."""
        url = self.url + f'/address/{address}'
        LOG.info(f'GET {url}')
        try:
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get address info for {address} from Blockstream.info: {ex}')
            return {'error': f'Unable to get address info for {address} from Blockstream.info'}

        sent_balance = data['chain_stats']['spent_txo_sum']  # Todo fix the sent and received balance because blockstream reports this wrong (also counts when change is sent back to the address itself)
        received_balance = data['chain_stats']['funded_txo_sum']
        final_balance = received_balance - sent_balance

        balance = {'final': final_balance,
                   'received': received_balance,
                   'sent': sent_balance}
        return {'balance': balance}

    def get_transaction(self, txid):
        """Retrieve a single transaction by its txid from the explorer."""
        url = self.url + f'/tx/{txid}'
        LOG.info(f'GET {url}')
        try:
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get transaction {txid} from Blockstream.info: {ex}')
            return {'error': f'Unable to get transaction {txid} from Blockstream.info'}

        tx = self.parse_transaction(data=data)

        return {'transaction': tx.json_encodable()}

    def parse_transaction(self, data, latest_block_height=None):
        """Parse raw transaction data from the explorer into a TX object."""
        if latest_block_height is None:
            url = self.url + '/blocks/tip/height'
            LOG.info(f'GET {url}')
            try:
                r = requests.get(url)
                latest_block_height = int(r.text)
            except (ValueError, KeyError, TypeError, OSError) as ex:
                LOG.error(f'Unable to get latest block_height from Blockstream.info: {ex}')
                return {'error': 'Unable to get latest block_height from Blockstream.info'}

        tx = TX()
        tx.txid = data['txid']
        tx.lock_time = data['locktime']
        tx.block_height = data['status'].get('block_height', None)
        tx.confirmations = latest_block_height - tx.block_height + 1 if tx.block_height is not None else 0

        for item in data['vin']:
            tx_input = TxInput()
            tx_input.address = item['prevout']['scriptpubkey_address'] if item['prevout'] is not None else None
            tx_input.value = item['prevout']['value'] if item['prevout'] is not None else 0
            tx_input.n = item['vout'] if item['is_coinbase'] is False else None
            tx_input.txid = item['txid']
            tx_input.script = item['scriptsig']
            tx_input.sequence = item['sequence']

            tx.inputs.append(tx_input)

        for i, item in enumerate(data['vout']):
            tx_output = TxOutput()
            tx_output.address = item.get('scriptpubkey_address', None)
            tx_output.value = item['value']
            tx_output.n = i
            tx_output.spent = None  # Blockstream does not provide information if a tx output has been spent
            tx_output.script = item['scriptpubkey']
            if item['scriptpubkey'][:2] == '6a':
                tx_output.op_return = tx.decode_op_return(item['scriptpubkey'])

            tx.outputs.append(tx_output)

        return tx

    def get_prime_input_address(self, txid):
        """Retrieve the prime input address of a transaction by txid."""
        transaction_data = self.get_transaction(txid=txid)
        return {'prime_input_address': transaction_data['transaction']['prime_input_address']} if 'prime_input_address' in transaction_data['transaction'] else {'error': f'Received invalid data: {transaction_data}'}

    def get_utxos(self, address, confirmations=3):
        """Retrieve unspent transaction outputs (UTXOs) for a given address."""
        url = self.url + '/blocks/tip/height'
        LOG.info(f'GET {url}')
        try:
            r = requests.get(url)
            latest_block_height = int(r.text)
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get latest block_height from Blockstream.info: {ex}')
            return {'error': 'Unable to get latest block_height from Blockstream.info'}

        url = self.url + f'/address/{address}/utxo'
        LOG.info(f'GET {url}')
        try:
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get address utxos for {address} from Blockstream.info: {ex}')
            return {'error': f'Unable to get utxos info for {address} from Blockstream.info'}

        LOG.info(f'Got {len(data)} utxos')

        utxos = []
        for output in data:
            confirmations = latest_block_height - int(output['status']['block_height']) + 1 if output['status']['confirmed'] is True else 0
            utxo = {'confirmations': confirmations,
                    'output_hash': output['txid'],
                    'output_n': output['vout'],
                    'value': output['value'],
                    'script': None}  # Blockstream.info does not provide the script for utxos

            if utxo['confirmations'] >= confirmations:
                utxos.append(utxo)

        return {'utxos': sorted(utxos, key=lambda k: (k['confirmations'], k['output_hash'], k['output_n']))}

    def push_tx(self, tx):
        """Broadcast a signed raw transaction to the blockchain network."""
        url = self.url + f'/broadcast?tx={tx}'
        LOG.info(f'GET {url}')
        try:
            r = requests.get(url)
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to push tx via Blockstream.info: {ex}')
            return {'error': f'Unable to push tx Blockstream.info: {ex}'}

        data = r.text.strip()
        if r.status_code == 200:
            return {'success': True,
                    'txid': data}
        else:
            LOG.error(f'Unable to push tx via Blockstream.info: {data}')
            return {'error': f'Unable to push tx Blockstream.info: {data}'}
