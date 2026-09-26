#!/usr/bin/env python
"""Chain.so block explorer API client."""

import binascii
from time import sleep

import requests

from data.explorer_api import ExplorerAPI
from data.transaction import TX, TxInput, TxOutput
from helpers.conversionhelpers import btc2satoshis
from helpers.loghelpers import LOG


class ChainSoAPI(ExplorerAPI):
    """
    Chain.so block explorer API client.

    Initializes the API client with URL, optional key, and testnet flag.
    """
    def __init__(self, url='', key='', testnet=False):
        super().__init__(url=url, testnet=testnet)
        # Set the network to use in the api calls (mainnet or testnet)
        self.network = 'BTCTEST' if self.testnet else 'BTC'
        self.url = 'https://chain.so/api/v2'

    def get_transactions(self, address):
        """Retrieve all transactions for a given address from the explorer."""
        LOG.warning('DO NOT USE CHAIN.SO TO GET ADDRESS TRANSACTIONS!!!!!!!!!!!!!')
        url = f'{self.url}/address/{self.network}/{address}'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get transactions of address {address} from Chain.so: {ex}')
            return {'error': f'Unable to get transactions of address {address} from Chain.so'}

        if 'data' not in data:
            LOG.error(f'Invalid response data from Chain.so: {data}')
            return {'error': f'Invalid response data from Chain.so: {data}'}

        data = data['data']

        txids = [transaction['txid'] for transaction in data['txs']]
        txs = []

        # I know this is very ugly, but its the only way to get the necessary information from chain.so
        for txid in txids:
            transaction_data = self.get_transaction(txid=txid)
            if 'transaction' in transaction_data:
                txs.append(transaction_data['transaction'])
            sleep(10)  # try to avoid hitting the rate limits probably won't work, extremely slow!!!!!

        return {'transactions': txs}

    def get_block_by_height(self, height):
        """Retrieve a block by its height from the blockchain explorer."""
        url = f'{self.url}/get_block/{self.network}/{height}'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get block {height} from Chain.so: {ex}')
            return {'error': f'Unable to get block {height} from Chain.so'}

        if 'data' not in data:
            LOG.error(f'Invalid response data from Chain.so: {data}')
            return {'error': f'Invalid response data from Chain.so: {data}'}

        data = data['data']

        if all(key in data for key in ('block_no', 'blockhash', 'time', 'merkleroot', 'size')):
            block = {'height': data['block_no'],
                     'hash': data['blockhash'],
                     'time': data['time'],
                     'merkleroot': data['merkleroot'],
                     'size': data['size']}
            return {'block': block}
        else:
            return {'error': f'Received invalid data: {data}'}

    def get_latest_block(self):
        """Retrieve the latest block from the blockchain explorer."""
        url = f'{self.url}/get_info/{self.network}'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get latest block from Chain.so: {ex}')
            return {'error': 'Unable to get latest block from Chain.so'}

        if 'data' not in data:
            LOG.error(f'Invalid response data from Chain.so: {data}')
            return {'error': f'Invalid response data from Chain.so: {data}'}

        data = data['data']

        if 'blocks' in data:
            block_height = data['blocks']
            return self.get_block_by_height(height=block_height)
        else:
            return {'error': 'Unable to get latest block height from Chain.so'}

    def get_utxos(self, address, confirmations=3):
        """Retrieve unspent transaction outputs (UTXOs) for a given address."""
        url = f'{self.url}/get_tx_unspent/{self.network}/{address}'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get transaction of address {address} from Chain.so: {ex}')
            return {'error': f'Unable to get transactions of address {address} from Chain.so'}

        if 'data' not in data:
            LOG.error(f'Invalid response data from Chain.so: {data}')
            return {'error': f'Invalid response data from Chain.so: {data}'}

        data = data['data']

        utxos = []
        for output in data['txs']:
            if all(key in output for key in ('confirmations', 'txid', 'output_no', 'value', 'script_hex')):
                utxo = {'confirmations': output['confirmations'],
                        'output_hash': output['txid'],
                        'output_n': output['output_no'],
                        'value': btc2satoshis(btc=output['value']),
                        'script': output['script_hex']}
                utxos.append(utxo)

        return {'utxos': sorted(utxos, key=lambda k: (k['confirmations'], k['output_hash'], k['output_n']))}

    def get_block_by_hash(self, block_hash):
        """Retrieve a block by its hash from the blockchain explorer."""
        url = f'{self.url}/get_block/{self.network}/{block_hash}'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get block {block_hash} from Chain.so: {ex}')
            return {'error': f'Unable to get block {block_hash} from Chain.so'}

        if 'data' not in data:
            LOG.error(f'Invalid response data from Chain.so: {data}')
            return {'error': f'Invalid response data from Chain.so: {data}'}

        data = data['data']

        if all(key in data for key in ('block_no', 'blockhash', 'time', 'merkleroot', 'size')):
            block = {'height': data['block_no'],
                     'hash': data['blockhash'],
                     'time': data['time'],
                     'merkleroot': data['merkleroot'],
                     'size': data['size']}
            return {'block': block}
        else:
            return {'error': f'Received invalid data: {data}'}

    def get_balance(self, address):
        """Retrieve the balance (final, received, sent) for a given address."""
        url = f'{self.url}/address/{self.network}/{address}'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get balance of address {address} from Chain.so: {ex}')
            return {'error': f'Unable to get balance of address {address} from Chain.so'}

        if 'data' not in data:
            LOG.error(f'Invalid response data from Chain.so: {data}')
            return {'error': f'Invalid response data from Chain.so: {data}'}

        data = data['data']

        final_balance = btc2satoshis(btc=data['balance'])
        received_balance = btc2satoshis(btc=data['received_value'])
        sent_balance = received_balance - final_balance

        balance = {'final': final_balance,
                   'received': received_balance,
                   'sent': sent_balance}

        return {'balance': balance}

    def get_prime_input_address(self, txid):
        """Retrieve the prime input address of a transaction by txid."""
        transaction_data = self.get_transaction(txid=txid)

        if 'transaction' in transaction_data and 'inputs' in transaction_data['transaction']:
            tx_inputs = transaction_data['transaction']['inputs']

            input_addresses = []
            for i in range(len(tx_inputs)):
                input_addresses.append(tx_inputs[i]['address'])

            if len(input_addresses) > 0:
                prime_input_address = min(input_addresses)
                return {'prime_input_address': prime_input_address}

        return {'error': f'Received invalid data: {transaction_data}'}

    def get_transaction(self, txid):
        """Retrieve a single transaction by its txid from the explorer."""
        url = f'{self.url}/get_tx/{self.network}/{txid}'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get transaction {txid} from Chain.so: {ex}')
            return {'error': f'Unable to get transaction {txid} from Chain.so'}

        if 'data' not in data:
            LOG.error(f'Invalid response data from Chain.so: {data}')
            return {'error': f'Invalid response data from Chain.so: {data}'}

        data = data['data']

        tx = TX()
        tx.txid = txid

        block_data = self.get_block_by_hash(block_hash=data['blockhash'])
        if not ('block' in block_data and 'height' in block_data['block']):
            LOG.error('Unable to get block {} to get the block height from chain.so'.format(data['blockhash']))
            return {'error': 'Unable to get block {} to get the block height from chain.so'.format(data['blockhash'])}

        tx.block_height = block_data['block']['height']
        tx.confirmations = data['confirmations']

        for item in data['inputs']:
            tx_input = TxInput()
            tx_input.address = item['address'] if item['address'] != 'coinbase' else None
            tx_input.value = btc2satoshis(btc=item['value']) if item['address'] != 'coinbase' else 0
            tx_input.n = item['from_output']['output_no'] if item['from_output'] is not None else None
            tx_input.txid = item['from_output']['txid'] if item['from_output'] is not None else None
            tx_input.script = item['script']
            tx_input.sequence = None  # Chain.so does not provide the sequence

            tx.inputs.append(tx_input)

        for item in data['outputs']:
            tx_output = TxOutput()
            tx_output.address = item['address'] if item['address'] != 'nonstandard' else None
            tx_output.value = btc2satoshis(btc=item['value'])
            tx_output.n = item['output_no']
            tx_output.spent = None  # Chain.so does not provide information if an output has been spent already or not
            tx_output.script = item['script']
            if item['script'][:10] == 'OP_RETURN ':
                tx_output.op_return = binascii.unhexlify(tx_output.script[10:])

                # Sometimes the unhexed data is encoded in another coded than utf-8 which could cause problems when converting to json later
                try:
                    tx_output.op_return = tx_output.op_return.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        tx_output.op_return = tx_output.op_return.decode('cp1252')
                    except (ValueError, KeyError, TypeError, OSError) as ex:
                        LOG.error(f'Unable to decode OP_RETURN data {tx_output.op_return} in utf-8 or cp1252: {ex}')
                        tx_output.op_return = 'Unable to decode hex data'

            tx.outputs.append(tx_output)

        return {'transaction': tx.json_encodable()}

