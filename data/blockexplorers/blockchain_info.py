#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from time import sleep

from helpers.loghelpers import LOG
from data.transaction import TX, TxInput, TxOutput
from data.explorer_api import ExplorerAPI


class BlockchainInfoAPI(ExplorerAPI):
    def __init__(self, url='', key='', testnet=False):
        super(BlockchainInfoAPI, self).__init__(url=url, testnet=testnet)
        # Set the url of the api depending on testnet or mainnet
        self.url = 'https://testnet.blockchain.info' if self.testnet is True else 'https://blockchain.info'

    def get_latest_block(self):
        latest_block = {}
        url = '{api_url}/latestblock'.format(api_url=self.url)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get latest block from Blockchain.info: %s' % ex)
            return {'error': 'Unable to get latest block from Blockchain.info'}

        if all(key in data for key in ('height', 'hash', 'time')):
            latest_block['height'] = data['height']
            latest_block['hash'] = data['hash']
            latest_block['time'] = data['time']

            url = '{api_url}/rawblock/{hash}'.format(api_url=self.url, hash=latest_block['hash'])
            try:
                LOG.info('GET %s' % url)
                r = requests.get(url)
                data = r.json()
            except ValueError:
                LOG.error('Blockchain.info returned invalid json data: %s', r.text)
                return {'error': 'Unable to get block %s from Blockchain.info' % latest_block['height']}

            except Exception as ex:
                LOG.error('Unable to get block %s from Blockchain.info: %s' % (latest_block['height'], ex))
                return {'error': 'Unable to get block %s from Blockchain.info' % latest_block['height']}

            if all(key in data for key in ('mrkl_root', 'size')):
                latest_block['merkleroot'] = data['mrkl_root']
                latest_block['size'] = data['size']

            return {'block': latest_block}
        else:
            return {'error': 'Received invalid data: %s' % data}

    def get_block_by_hash(self, block_hash):
        url = '{api_url}/rawblock/{hash}'.format(api_url=self.url, hash=block_hash)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get block %s from Blockchain.info: %s' % (block_hash, ex))
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
        url = '{api_url}/block-height/{height}?format=json'.format(api_url=self.url, height=height)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get block %s from Blockchain.info: %s' % (height, ex))
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
            url = '{api_url}/address/{address}?format=json&limit={limit}&offset={offset}'.format(api_url=self.url, address=address, limit=limit, offset=limit * i)
            try:
                LOG.info('GET %s' % url)
                r = requests.get(url)
                data = r.json()
            except Exception as ex:
                LOG.error('Unable to get transactions of address %s from %s: %s' % (address, url, ex))
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

            for item in transaction['inputs']:
                tx_input = TxInput()
                tx_input.address = item['prev_out']['addr']
                tx_input.value = item['prev_out']['value']
                tx_input.n = item['prev_out']['n']
                tx_input.script = item['prev_out']['script']

                tx.inputs.append(tx_input)

            for item in transaction['out']:
                tx_output = TxOutput()
                tx_output.address = item['addr']
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
            return {'error': 'Not all transactions are retrieved! expected {expected} but only got {received}'.format(expected=n_tx, received=len(txs))}
        else:
            return {'transactions': txs}

    def get_balance(self, address):
        url = '{api_url}/q/addressbalance/{address}?confirmations=1'.format(api_url=self.url, address=address)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            final_balance = int(r.text)
        except Exception as ex:
            LOG.error('Unable to get balance of address %s from Blockchain.info: %s' % (address, ex))
            return {'error': 'Unable to get balance of address %s from Blockchain.info' % address}

        url = '{api_url}/q/getreceivedbyaddress/{address}?confirmations=1'.format(api_url=self.url, address=address)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            received_balance = int(r.text)
        except Exception as ex:
            LOG.error('Unable to get balance of address %s from Blockchain.info: %s' % (address, ex))
            return {'error': 'Unable to get balance of address %s from Blockchain.info' % address}

        url = '{api_url}/q/getsentbyaddress/{address}?confirmations=1'.format(api_url=self.url, address=address)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            sent_balance = int(r.text)
        except Exception as ex:
            LOG.error('Unable to get balance of address %s from Blockchain.info: %s' % (address, ex))
            return {'error': 'Unable to get balance of address %s from Blockchain.info' % address}

        balance = {'final': final_balance,
                   'received': received_balance,
                   'sent': sent_balance}
        return {'balance': balance}

    def get_transaction(self, txid):
        url = '{api_url}/rawtx/{txid}'.format(api_url=self.url, txid=txid)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get tx %s from Blockchain.info: %s' % (txid, ex))
            return {'error': 'Unable to get tx %s from Blockchain.info' % txid}

        tx = TX()
        tx.txid = txid
        tx.block_height = data['block_height'] if 'block_height' in data else None
        tx.confirmations = self.get_latest_block_height() - tx.block_height if tx.block_height is not None else 0

        for item in data['inputs']:
            tx_input = TxInput()
            tx_input.address = item['prev_out']['addr']
            tx_input.value = item['prev_out']['value']
            tx_input.n = item['prev_out']['n']
            tx_input.script = item['prev_out']['script']

            tx.inputs.append(tx_input)

        for item in data['out']:
            tx_output = TxOutput()
            tx_output.address = item['addr']
            tx_output.value = item['value']
            tx_output.n = item['n']
            tx_output.spent = item['spent']
            tx_output.script = item['script']
            if item['script'][:2] == '6a':
                tx_output.op_return = tx.decode_op_return(item['script'])

            tx.outputs.append(tx_output)

        return {'transaction': tx.json_encodable()}

    def get_prime_input_address(self, txid):
        url = '{api_url}/rawtx/{txid}'.format(api_url=self.url, txid=txid)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get prime input address of tx %s from Blockchain.info: %s' % (txid, ex))
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
        url = '{api_url}/unspent?active={address}&limit={limit}&confirmations={confirmations}'.format(api_url=self.url, address=address, limit=limit, confirmations=confirmations)
        try:
            LOG.info('GET %s' % url)
            r = requests.get(url)
            if r.text == 'No free outputs to spend':
                return {'utxos': []}

            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get utxos of address %s from %s: %s' % (address, url, ex))
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

    def push_tx(self, tx):
        url = '{api_url}/pushtx'.format(api_url=self.url)
        LOG.info('POST %s' % url)
        try:
            r = requests.post(url, data=dict(tx=tx))
        except Exception as ex:
            LOG.error('Unable to push tx via Blockchain.info: %s' % ex)
            return {'error': 'Unable to push tx Blockchain.info: %s' % ex}

        data = r.text.strip()
        if r.status_code == 200 and data == 'Transaction Submitted':
            return {'success': True}
        else:
            LOG.error('Unable to push tx via Blockchain.info: %s' % data)
            return {'error': 'Unable to push tx Blockchain.info: %s' % data}
