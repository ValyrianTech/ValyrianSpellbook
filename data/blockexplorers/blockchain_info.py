#!/usr/bin/env python
"""Blockchain.info block explorer API client."""
from time import sleep

import requests

from data.explorer_api import ExplorerAPI
from data.transaction import TX, TxInput, TxOutput
from helpers.loghelpers import LOG


class BlockchainInfoAPI(ExplorerAPI):
    """
    Blockchain.info block explorer API client.

    Initializes the API client with URL, optional key, and testnet flag.
    """
    def __init__(self, url='', key='', testnet=False):
        super().__init__(url=url, testnet=testnet)
        # Set the url of the api depending on testnet or mainnet
        self.url = 'https://testnet.blockchain.info' if self.testnet is True else 'https://blockchain.info'

    def get_latest_block(self):
        """Retrieve the latest block from the blockchain explorer."""
        latest_block = {}
        url = f'{self.url}/latestblock'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get latest block from Blockchain.info: {ex}')
            return {'error': 'Unable to get latest block from Blockchain.info'}

        if all(key in data for key in ('height', 'hash', 'time')):
            latest_block['height'] = data['height']
            latest_block['hash'] = data['hash']
            latest_block['time'] = data['time']

            url = '{api_url}/rawblock/{hash}'.format(api_url=self.url, hash=latest_block['hash'])
            try:
                LOG.info(f'GET {url}')
                r = requests.get(url)
                data = r.json()
            except ValueError:
                LOG.error('Blockchain.info returned invalid json data: %s', r.text)
                return {'error': 'Unable to get block {} from Blockchain.info'.format(latest_block['height'])}

            except (KeyError, TypeError, OSError) as ex:
                LOG.error('Unable to get block {} from Blockchain.info: {}'.format(latest_block['height'], ex))
                return {'error': 'Unable to get block {} from Blockchain.info'.format(latest_block['height'])}

            if all(key in data for key in ('mrkl_root', 'size')):
                latest_block['merkleroot'] = data['mrkl_root']
                latest_block['size'] = data['size']

            return {'block': latest_block}
        else:
            return {'error': f'Received invalid data: {data}'}

    def get_block_by_hash(self, block_hash):
        """Retrieve a block by its hash from the blockchain explorer."""
        url = f'{self.url}/rawblock/{block_hash}'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get block {block_hash} from Blockchain.info: {ex}')
            return {'error': f'Unable to get block {block_hash} from Blockchain.info'}

        if all(key in data for key in ('height', 'hash', 'time', 'mrkl_root', 'size')):
            block = {'height': data['height'],
                     'hash': data['hash'],
                     'time': data['time'],
                     'merkleroot': data['mrkl_root'],
                     'size': data['size']}
            return {'block': block}
        else:
            return {'error': f'Received invalid data: {data}'}

    def get_block_by_height(self, height):
        """Retrieve a block by its height from the blockchain explorer."""
        url = f'{self.url}/block-height/{height}?format=json'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get block {height} from Blockchain.info: {ex}')
            return {'error': f'Unable to get block {height} from Blockchain.info'}

        if 'blocks' in data:
            blocks = data['blocks']
            for i in range(len(blocks)):
                if blocks[i]['main_chain'] is True and blocks[i]['height'] == height:
                    block = {'height': blocks[i]['height'],
                             'hash': blocks[i]['hash'],
                             'time': blocks[i]['time'],
                             'merkleroot': blocks[i]['mrkl_root'],
                             'size': blocks[i]['size']}
                    return {'block': block}

        return {'error': f'Received invalid data: {data}'}

    def get_transactions(self, address):
        """Retrieve all transactions for a given address from the explorer."""
        limit = 50  # max number of tx given by blockchain.info is 50
        n_tx = None
        transactions = []
        latest_block_height = self.get_latest_block_height()
        if latest_block_height is None:
            return {'error': 'Unable to get latest block height'}

        i = 0
        while n_tx is None or len(transactions) < n_tx:
            url = f'{self.url}/address/{address}?format=json&limit={limit}&offset={limit * i}'
            try:
                LOG.info(f'GET {url}')
                r = requests.get(url)
                data = r.json()
            except (ValueError, KeyError, TypeError, OSError) as ex:
                LOG.error(f'Unable to get transactions of address {address} from {url}: {ex}')
                return {'error': f'Unable to get transactions of address {address} from {url}'}

            if all(key in data for key in ('n_tx', 'txs')):
                n_tx = data['n_tx']
                transactions += data['txs']
                i += 1
            else:
                return {'error': f'Received Invalid data: {data}'}

            if len(transactions) < n_tx:
                sleep(1)

        txs = []
        for transaction in transactions:
            tx = TX()
            tx.txid = transaction['hash']
            tx.lock_time = transaction['lock_time']
            tx.block_height = transaction.get('block_height', None)
            tx.confirmations = (latest_block_height - tx.block_height) + 1 if 'block_height' in transaction else 0

            for item in transaction['inputs']:
                tx_input = TxInput()
                tx_input.address = item['prev_out']['addr'] if 'prev_out' in item else None
                tx_input.value = item['prev_out']['value'] if 'prev_out' in item else 0
                tx_input.txid = ''  # Blockchain.info does not provide the txid of a tx input only their own tx_index, can be resolved for example via https://testnet.blockchain.info/tx-index/197277768?format=json but this would require too many http requests!!!
                tx_input.n = item['prev_out']['n'] if 'prev_out' in item else None
                tx_input.script = item['script']
                tx_input.sequence = item['sequence']

                tx.inputs.append(tx_input)

            for item in transaction['out']:
                tx_output = TxOutput()
                tx_output.address = item.get('addr', None)
                tx_output.value = item['value']
                tx_output.n = item['n']
                tx_output.spent = item['spent']
                tx_output.script = item['script']
                if item['script'][:2] == '6a':
                    tx_output.op_return = tx.decode_op_return(item['script'])

                tx.outputs.append(tx_output)

            # Only append confirmed transactions
            if tx.block_height is not None:
                txs.insert(0, tx.to_dict(address))
            else:
                # subtract 1 from total txs because it is unconfirmed
                n_tx -= 1

        if n_tx != len(txs):
            return {'error': f'Not all transactions are retrieved! expected {n_tx} but only got {len(txs)}'}
        else:
            return {'transactions': txs}

    def get_balance(self, address):
        """Retrieve the balance (final, received, sent) for a given address."""
        url = f'{self.url}/q/addressbalance/{address}?confirmations=1'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            final_balance = int(r.text)
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get balance of address {address} from Blockchain.info: {ex}')
            return {'error': f'Unable to get balance of address {address} from Blockchain.info'}

        url = f'{self.url}/q/getreceivedbyaddress/{address}?confirmations=1'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            received_balance = int(r.text)
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get balance of address {address} from Blockchain.info: {ex}')
            return {'error': f'Unable to get balance of address {address} from Blockchain.info'}

        url = f'{self.url}/q/getsentbyaddress/{address}?confirmations=1'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            sent_balance = int(r.text)
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get balance of address {address} from Blockchain.info: {ex}')
            return {'error': f'Unable to get balance of address {address} from Blockchain.info'}

        balance = {'final': final_balance,
                   'received': received_balance,
                   'sent': sent_balance}
        return {'balance': balance}

    def get_transaction(self, txid):
        """Retrieve a single transaction by its txid from the explorer."""
        url = f'{self.url}/rawtx/{txid}'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get tx {txid} from Blockchain.info: {ex}')
            return {'error': f'Unable to get tx {txid} from Blockchain.info'}

        tx = TX()
        tx.txid = txid
        tx.lock_time = data['lock_time']
        tx.block_height = data.get('block_height', None)
        tx.confirmations = self.get_latest_block_height() - tx.block_height + 1 if tx.block_height is not None else 0

        for item in data['inputs']:
            tx_input = TxInput()
            tx_input.address = item['prev_out']['addr'] if 'prev_out' in item else None
            tx_input.value = item['prev_out']['value'] if 'prev_out' in item else 0
            tx_input.n = item['prev_out']['n'] if 'prev_out' in item else None
            tx_input.txid = ''  # Blockchain.info does not provide the txid of a tx input only their own tx_index, can be resolved for example via https://testnet.blockchain.info/tx-index/197277768?format=json but this would require too many http requests!!!
            tx_input.script = item['script']
            tx_input.sequence = item['sequence']

            tx.inputs.append(tx_input)

        for item in data['out']:
            tx_output = TxOutput()
            tx_output.address = item.get('addr', None)
            tx_output.value = item['value']
            tx_output.n = item['n']
            tx_output.spent = item['spent']
            tx_output.script = item['script']
            if item['script'][:2] == '6a':
                tx_output.op_return = tx.decode_op_return(item['script'])

            tx.outputs.append(tx_output)

        return {'transaction': tx.json_encodable()}

    def get_prime_input_address(self, txid):
        """Retrieve the prime input address of a transaction by txid."""
        url = f'{self.url}/rawtx/{txid}'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get prime input address of tx {txid} from Blockchain.info: {ex}')
            return {'error': f'Unable to get prime input address of tx {txid} from Blockchain.info'}

        if 'inputs' in data:
            tx_inputs = data['inputs']

            input_addresses = []
            for i in range(len(tx_inputs)):
                if 'prev_out' in tx_inputs[i]:  # Coinbase transactions don't have a input address
                    input_addresses.append(tx_inputs[i]['prev_out']['addr'])

            if len(input_addresses) > 0:
                prime_input_address = min(input_addresses)
                return {'prime_input_address': prime_input_address}
            else:
                # transaction was a coinbase transaction, so there are no input addresses
                return {'prime_input_address': None}

        return {'error': f'Received invalid data: {data}'}

    def get_utxos(self, address, confirmations=3):
        """Retrieve unspent transaction outputs (UTXOs) for a given address."""
        limit = 1000  # max number of utxo given by blockchain.info is 1000, there is no 'offset' parameter available
        url = f'{self.url}/unspent?active={address}&limit={limit}&confirmations={confirmations}'
        try:
            LOG.info(f'GET {url}')
            r = requests.get(url)
            if r.text == 'No free outputs to spend':
                return {'utxos': []}

            data = r.json()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to get utxos of address {address} from {url}: {ex}')
            return {'error': f'Unable to get utxos of address {address} from {url}'}

        if 'unspent_outputs' in data:
            unspent_outputs = data['unspent_outputs']
        else:
            return {'error': f'Received Invalid data: {data}'}

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

    def push_tx(self, tx):
        """Broadcast a signed raw transaction to the blockchain network."""
        url = f'{self.url}/pushtx'
        LOG.info(f'POST {url}')
        try:
            r = requests.post(url, data={'tx': tx})
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to push tx via Blockchain.info: {ex}')
            return {'error': f'Unable to push tx Blockchain.info: {ex}'}

        data = r.text.strip()
        if r.status_code == 200 and data == 'Transaction Submitted':
            return {'success': True}
        else:
            LOG.error(f'Unable to push tx via Blockchain.info: {data}')
            return {'error': f'Unable to push tx Blockchain.info: {data}'}
