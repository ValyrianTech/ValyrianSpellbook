#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from time import sleep

from helpers.loghelpers import LOG
from data.transaction import TX, TxInput, TxOutput
from data.explorer_api import ExplorerAPI

from pprint import pprint


class BlockstreamAPI(ExplorerAPI):
    def __init__(self, url='', key='', testnet=False):
        super(BlockstreamAPI, self).__init__(url=url, testnet=testnet)
        # Set the url of the api depending on testnet or mainnet
        self.url = 'https://blockstream.info/testnet/api' if self.testnet is True else 'https://blockstream.info/api'

    def get_latest_block(self):
        url = self.url + '/blocks/tip/hash'
        LOG.info('GET %s' % url)
        try:
            r = requests.get(url)
            block_hash = r.text
        except Exception as ex:
            LOG.error('Unable to get latest block_hash from Blockstream.info: %s' % ex)
            return {'error': 'Unable to get latest block_hash from Blockstream.info'}

        return self.get_block_by_hash(block_hash=block_hash)

    def get_block_by_hash(self, block_hash):
        url = self.url + '/block/{hash}'.format(hash=block_hash)
        LOG.info('GET %s' % url)
        try:
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get block %s from Blockstream.info: %s' % (block_hash, ex))
            return {'error': 'Unable to get block %s from Blockstream.info' % block_hash}

        if all(key in data for key in ('height', 'id', 'timestamp', 'merkle_root', 'size')):
            block = {'height': data['height'],
                     'hash': data['id'],
                     'time': data['timestamp'],
                     'merkleroot': data['merkle_root'],
                     'size': data['size']}  # Todo weight?
            return {'block': block}
        else:
            return {'error': 'Received invalid data: %s' % data}

    def get_block_by_height(self, height):
        url = self.url + '/block-height/{height}'.format(height=height)
        LOG.info('GET %s' % url)
        try:
            r = requests.get(url)
            block_hash = r.text
        except Exception as ex:
            LOG.error('Unable to get block %s from Blockstream.info: %s' % (height, ex))
            return {'error': 'Unable to get block %s from Blockstream.info' % height}

        return self.get_block_by_hash(block_hash=block_hash)

    def get_transactions(self, address):
        url = self.url + '/blocks/tip/height'
        LOG.info('GET %s' % url)
        try:
            r = requests.get(url)
            latest_block_height = int(r.text)
        except Exception as ex:
            LOG.error('Unable to get latest block_height from Blockstream.info: %s' % ex)
            return {'error': 'Unable to get latest block_height from Blockstream.info'}

        url = self.url + '/address/{address}/txs'.format(address=address)
        LOG.info('GET %s' % url)
        try:
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get address transactions for %s from Blockstream.info: %s' % (address, ex))
            return {'error': 'Unable to get address transactions for %s from Blockstream.info' % address}

        txs = []
        for transaction in data:
            txs.append(self.parse_transaction(data=transaction, latest_block_height=latest_block_height).to_dict(address=address))

        while len(data) == 25:
            sleep(0.5)
            last_txid = data[24]['txid']
            url = self.url + '/address/{address}/txs/chain/{last_txid}'.format(address=address, last_txid=last_txid)
            LOG.info('GET %s' % url)
            try:
                r = requests.get(url)
                data = r.json()
            except Exception as ex:
                LOG.error('Unable to get address transactions for %s from Blockstream.info: %s' % (address, ex))
                return {'error': 'Unable to get address transactions for %s from Blockstream.info' % address}

            for transaction in data:
                txs.append(self.parse_transaction(data=transaction, latest_block_height=latest_block_height).to_dict(address=address))

        LOG.info('Retrieved %s transactions' % len(txs))
        return {'transactions': txs}

    def get_balance(self, address):
        url = self.url + '/address/{address}'.format(address=address)
        LOG.info('GET %s' % url)
        try:
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get address info for %s from Blockstream.info: %s' % (address, ex))
            return {'error': 'Unable to get address info for %s from Blockstream.info' % address}

        sent_balance = data['chain_stats']['spent_txo_sum']  # Todo fix the sent and received balance because blockstream reports this wrong (also counts when change is sent back to the address itself)
        received_balance = data['chain_stats']['funded_txo_sum']
        final_balance = received_balance - sent_balance

        balance = {'final': final_balance,
                   'received': received_balance,
                   'sent': sent_balance}
        return {'balance': balance}

    def get_transaction(self, txid):
        url = self.url + '/tx/{txid}'.format(txid=txid)
        LOG.info('GET %s' % url)
        try:
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get transaction %s from Blockstream.info: %s' % (txid, ex))
            return {'error': 'Unable to get transaction %s from Blockstream.info' % txid}

        tx = self.parse_transaction(data=data)

        return {'transaction': tx.json_encodable()}

    def parse_transaction(self, data, latest_block_height=None):
        if latest_block_height is None:
            url = self.url + '/blocks/tip/height'
            LOG.info('GET %s' % url)
            try:
                r = requests.get(url)
                latest_block_height = int(r.text)
            except Exception as ex:
                LOG.error('Unable to get latest block_height from Blockstream.info: %s' % ex)
                return {'error': 'Unable to get latest block_height from Blockstream.info'}

        tx = TX()
        tx.txid = data['txid']
        tx.lock_time = data['locktime']
        tx.block_height = data['status']['block_height'] if 'block_height' in data['status'] else None
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
            tx_output.address = item['scriptpubkey_address'] if 'scriptpubkey_address' in item else None
            tx_output.value = item['value']
            tx_output.n = i
            tx_output.spent = None  # Blockstream does not provide information if a tx output has been spent
            tx_output.script = item['scriptpubkey']
            if item['scriptpubkey'][:2] == '6a':
                tx_output.op_return = tx.decode_op_return(item['scriptpubkey'])

            tx.outputs.append(tx_output)

        return tx

    def get_prime_input_address(self, txid):
        transaction_data = self.get_transaction(txid=txid)
        return {'prime_input_address': transaction_data['transaction']['prime_input_address']} if 'prime_input_address' in transaction_data['transaction'] else {'error': 'Received invalid data: %s' % transaction_data}

    def get_utxos(self, address, confirmations=3):
        url = self.url + '/blocks/tip/height'
        LOG.info('GET %s' % url)
        try:
            r = requests.get(url)
            latest_block_height = int(r.text)
        except Exception as ex:
            LOG.error('Unable to get latest block_height from Blockstream.info: %s' % ex)
            return {'error': 'Unable to get latest block_height from Blockstream.info'}

        url = self.url + '/address/{address}/utxo'.format(address=address)
        LOG.info('GET %s' % url)
        try:
            r = requests.get(url)
            data = r.json()
        except Exception as ex:
            LOG.error('Unable to get address utxos for %s from Blockstream.info: %s' % (address, ex))
            return {'error': 'Unable to get utxos info for %s from Blockstream.info' % address}

        LOG.info('Got %s utxos' % len(data))

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
        url = self.url + '/broadcast?tx={tx}'.format(tx=tx)
        LOG.info('GET %s' % url)
        try:
            r = requests.get(url)
        except Exception as ex:
            LOG.error('Unable to push tx via Blockstream.info: %s' % ex)
            return {'error': 'Unable to push tx Blockstream.info: %s' % ex}

        data = r.text.strip()
        if r.status_code == 200:
            return {'success': True,
                    'txid': data}
        else:
            LOG.error('Unable to push tx via Blockstream.info: %s' % data)
            return {'error': 'Unable to push tx Blockstream.info: %s' % data}
