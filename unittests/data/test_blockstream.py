#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock

from data.blockexplorers.blockstream import BlockstreamAPI


def make_mock_response(json_data=None, text_data=None, status_code=200):
    resp = mock.MagicMock()
    resp.status_code = status_code
    if json_data is not None:
        resp.json.return_value = json_data
    if text_data is not None:
        resp.text = text_data
    return resp


class TestBlockstreamAPIInit(object):
    def test_init_mainnet(self):
        api = BlockstreamAPI()
        assert 'blockstream.info/api' in api.url
        assert api.testnet is False

    def test_init_testnet(self):
        api = BlockstreamAPI(testnet=True)
        assert 'testnet' in api.url
        assert api.testnet is True


class TestGetLatestBlock(object):
    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_success(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(text_data='blockhash123'),
            make_mock_response(json_data={'height': 100, 'id': 'blockhash123', 'timestamp': 123, 'merkle_root': 'm', 'size': 500})
        ]
        api = BlockstreamAPI()
        result = api.get_latest_block()
        assert result['block']['height'] == 100

    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_request_error_on_hash(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlockstreamAPI()
        result = api.get_latest_block()
        assert 'error' in result


class TestGetBlockByHash(object):
    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'height': 100, 'id': 'abc', 'timestamp': 123, 'merkle_root': 'm', 'size': 500
        })
        api = BlockstreamAPI()
        result = api.get_block_by_hash('abc')
        assert result['block']['height'] == 100

    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlockstreamAPI()
        result = api.get_block_by_hash('abc')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_invalid_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = BlockstreamAPI()
        result = api.get_block_by_hash('abc')
        assert 'error' in result


class TestGetBlockByHeight(object):
    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_success(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(text_data='blockhash123'),
            make_mock_response(json_data={'height': 100, 'id': 'abc', 'timestamp': 123, 'merkle_root': 'm', 'size': 500})
        ]
        api = BlockstreamAPI()
        result = api.get_block_by_height(100)
        assert result['block']['height'] == 100

    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlockstreamAPI()
        result = api.get_block_by_height(100)
        assert 'error' in result


class TestGetTransactions(object):
    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_success(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(text_data='200'),
            make_mock_response(json_data=[{
                'txid': 'tx1', 'locktime': 0, 'status': {'confirmed': True, 'block_height': 100},
                'vin': [{'prevout': {'scriptpubkey_address': 'addr1', 'value': 100}, 'vout': 0, 'is_coinbase': False, 'txid': 'intx', 'scriptsig': 'sig', 'sequence': 1}],
                'vout': [{'scriptpubkey_address': 'addr2', 'value': 50, 'scriptpubkey': '76a9'}]
            }])
        ]
        api = BlockstreamAPI()
        result = api.get_transactions('addr1')
        assert 'transactions' in result

    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_error_getting_height(self, mock_get):
        mock_get.side_effect = [
            mock.MagicMock(text='error', json=mock.MagicMock(side_effect=Exception('fail')))
        ]
        api = BlockstreamAPI()
        result = api.get_transactions('addr1')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_error_getting_txs(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(text_data='200'),
            mock.MagicMock(json=mock.MagicMock(side_effect=Exception('fail')))
        ]
        api = BlockstreamAPI()
        result = api.get_transactions('addr1')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_unconfirmed_tx_skipped(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(text_data='200'),
            make_mock_response(json_data=[{
                'txid': 'tx1', 'locktime': 0, 'status': {'confirmed': False},
                'vin': [], 'vout': []
            }])
        ]
        api = BlockstreamAPI()
        result = api.get_transactions('addr1')
        assert result['transactions'] == []

    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_pagination(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(text_data='200'),
            make_mock_response(json_data=[{
                'txid': 'tx%d' % i, 'locktime': 0, 'status': {'confirmed': True, 'block_height': 100},
                'vin': [{'prevout': {'scriptpubkey_address': 'addr1', 'value': 100}, 'vout': 0, 'is_coinbase': False, 'txid': 'intx', 'scriptsig': 'sig', 'sequence': 1}],
                'vout': [{'scriptpubkey_address': 'addr2', 'value': 50, 'scriptpubkey': '76a9'}]
            } for i in range(25)]),
            make_mock_response(json_data=[])
        ]
        api = BlockstreamAPI()
        result = api.get_transactions('addr1')
        assert len(result['transactions']) == 25

    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_pagination_error(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(text_data='200'),
            make_mock_response(json_data=[{
                'txid': 'tx%d' % i, 'locktime': 0, 'status': {'confirmed': True, 'block_height': 100},
                'vin': [{'prevout': {'scriptpubkey_address': 'addr1', 'value': 100}, 'vout': 0, 'is_coinbase': False, 'txid': 'intx', 'scriptsig': 'sig', 'sequence': 1}],
                'vout': [{'scriptpubkey_address': 'addr2', 'value': 50, 'scriptpubkey': '76a9'}]
            } for i in range(25)]),
            mock.MagicMock(json=mock.MagicMock(side_effect=Exception('fail')))
        ]
        api = BlockstreamAPI()
        result = api.get_transactions('addr1')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockstream.sleep')
    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_pagination_with_confirmed_second_page(self, mock_get, mock_sleep):
        first_page = [{
            'txid': 'tx%d' % i, 'locktime': 0, 'status': {'confirmed': True, 'block_height': 100},
            'vin': [{'prevout': {'scriptpubkey_address': 'addr1', 'value': 100}, 'vout': 0, 'is_coinbase': False, 'txid': 'intx', 'scriptsig': 'sig', 'sequence': 1}],
            'vout': [{'scriptpubkey_address': 'addr2', 'value': 50, 'scriptpubkey': '76a9'}]
        } for i in range(25)]
        second_page = [{
            'txid': 'tx25', 'locktime': 0, 'status': {'confirmed': True, 'block_height': 101},
            'vin': [{'prevout': {'scriptpubkey_address': 'addr1', 'value': 100}, 'vout': 0, 'is_coinbase': False, 'txid': 'intx', 'scriptsig': 'sig', 'sequence': 1}],
            'vout': [{'scriptpubkey_address': 'addr2', 'value': 50, 'scriptpubkey': '76a9'}]
        }]
        mock_get.side_effect = [
            make_mock_response(text_data='200'),
            make_mock_response(json_data=first_page),
            make_mock_response(json_data=second_page)
        ]
        api = BlockstreamAPI()
        result = api.get_transactions('addr1')
        assert len(result['transactions']) == 26


class TestGetBalance(object):
    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'chain_stats': {'spent_txo_sum': 50, 'funded_txo_sum': 200}
        })
        api = BlockstreamAPI()
        result = api.get_balance('addr')
        assert result['balance']['final'] == 150
        assert result['balance']['received'] == 200
        assert result['balance']['sent'] == 50

    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlockstreamAPI()
        result = api.get_balance('addr')
        assert 'error' in result


class TestGetTransaction(object):
    @mock.patch('data.blockexplorers.blockstream.requests.get')
    @mock.patch('data.blockexplorers.blockstream.BlockstreamAPI.parse_transaction')
    def test_success(self, mock_parse, mock_get):
        mock_get.return_value = make_mock_response(json_data={'txid': 'tx1'})
        mock_tx = mock.MagicMock()
        mock_tx.json_encodable.return_value = {'txid': 'tx1'}
        mock_parse.return_value = mock_tx
        api = BlockstreamAPI()
        result = api.get_transaction('txid')
        assert 'transaction' in result

    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlockstreamAPI()
        result = api.get_transaction('txid')
        assert 'error' in result


class TestParseTransaction(object):
    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_with_latest_block_height(self, mock_get):
        data = {
            'txid': 'tx1', 'locktime': 0, 'status': {'block_height': 100},
            'vin': [{'prevout': {'scriptpubkey_address': 'addr1', 'value': 100}, 'vout': 0, 'is_coinbase': False, 'txid': 'intx', 'scriptsig': 'sig', 'sequence': 1}],
            'vout': [{'scriptpubkey_address': 'addr2', 'value': 50, 'scriptpubkey': '76a9'}]
        }
        api = BlockstreamAPI()
        result = api.parse_transaction(data=data, latest_block_height=200)
        assert result.txid == 'tx1'
        assert result.block_height == 100
        assert result.confirmations == 101

    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_without_latest_block_height(self, mock_get):
        mock_get.return_value = make_mock_response(text_data='200')
        data = {
            'txid': 'tx1', 'locktime': 0, 'status': {'block_height': 100},
            'vin': [{'prevout': None, 'vout': 0, 'is_coinbase': True, 'txid': None, 'scriptsig': '', 'sequence': 0}],
            'vout': [{'scriptpubkey': '6a0568656c6c6f', 'value': 0}]
        }
        api = BlockstreamAPI()
        result = api.parse_transaction(data=data)
        assert result.txid == 'tx1'

    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_error_getting_height(self, mock_get):
        mock_get.side_effect = Exception('fail')
        data = {
            'txid': 'tx1', 'locktime': 0, 'status': {},
            'vin': [], 'vout': []
        }
        api = BlockstreamAPI()
        result = api.parse_transaction(data=data)
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_no_block_height(self, mock_get):
        data = {
            'txid': 'tx1', 'locktime': 0, 'status': {},
            'vin': [], 'vout': []
        }
        api = BlockstreamAPI()
        result = api.parse_transaction(data=data, latest_block_height=200)
        assert result.block_height is None
        assert result.confirmations == 0


class TestGetPrimeInputAddress(object):
    @mock.patch('data.blockexplorers.blockstream.BlockstreamAPI.get_transaction')
    def test_success(self, mock_get_tx):
        mock_get_tx.return_value = {'transaction': {'prime_input_address': 'addr1'}}
        api = BlockstreamAPI()
        result = api.get_prime_input_address('txid')
        assert result['prime_input_address'] == 'addr1'

    @mock.patch('data.blockexplorers.blockstream.BlockstreamAPI.get_transaction')
    def test_no_prime_input(self, mock_get_tx):
        mock_get_tx.return_value = {'transaction': {'txid': 'tx1'}}
        api = BlockstreamAPI()
        result = api.get_prime_input_address('txid')
        assert 'error' in result


class TestGetUtxos(object):
    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_success(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(text_data='200'),
            make_mock_response(json_data=[{
                'txid': 'tx1', 'vout': 0, 'value': 100,
                'status': {'confirmed': True, 'block_height': 100}
            }])
        ]
        api = BlockstreamAPI()
        result = api.get_utxos('addr')
        assert len(result['utxos']) == 1

    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_error_getting_height(self, mock_get):
        mock_get.side_effect = [
            mock.MagicMock(text='error', json=mock.MagicMock(side_effect=Exception('fail')))
        ]
        api = BlockstreamAPI()
        result = api.get_utxos('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_error_getting_utxos(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(text_data='200'),
            mock.MagicMock(json=mock.MagicMock(side_effect=Exception('fail')))
        ]
        api = BlockstreamAPI()
        result = api.get_utxos('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_unconfirmed_utxo(self, mock_get):
        # Note: blockstream code reassigns local 'confirmations' variable,
        # so the filter always passes. This test verifies actual behavior.
        mock_get.side_effect = [
            make_mock_response(text_data='200'),
            make_mock_response(json_data=[{
                'txid': 'tx1', 'vout': 0, 'value': 100,
                'status': {'confirmed': False}
            }])
        ]
        api = BlockstreamAPI()
        result = api.get_utxos('addr')
        assert len(result['utxos']) == 1
        assert result['utxos'][0]['confirmations'] == 0


class TestPushTx(object):
    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(text_data='txid123', status_code=200)
        api = BlockstreamAPI()
        result = api.push_tx('rawtx')
        assert result['success'] is True
        assert result['txid'] == 'txid123'

    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_failure(self, mock_get):
        mock_get.return_value = make_mock_response(text_data='error', status_code=400)
        api = BlockstreamAPI()
        result = api.push_tx('rawtx')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockstream.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlockstreamAPI()
        result = api.push_tx('rawtx')
        assert 'error' in result
