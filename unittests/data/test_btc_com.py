#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock

from data.blockexplorers.btc_com import BTCComAPI


def make_mock_response(json_data=None, text_data=None, status_code=200):
    resp = mock.MagicMock()
    resp.status_code = status_code
    if json_data is not None:
        resp.json.return_value = json_data
    if text_data is not None:
        resp.text = text_data
    return resp


class TestBTCComAPIInit(object):
    def test_init_mainnet(self):
        api = BTCComAPI()
        assert 'chain.api.btc.com/v3' in api.url

    def test_init_testnet(self):
        api = BTCComAPI(testnet=True)
        assert 'tchain.api.btc.com/v3' in api.url


class TestGetLatestBlock(object):
    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'data': {'height': 100, 'hash': 'abc', 'timestamp': 123, 'mrkl_root': 'm', 'size': 500}
        })
        api = BTCComAPI()
        result = api.get_latest_block()
        assert result['block']['height'] == 100

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BTCComAPI()
        result = api.get_latest_block()
        assert 'error' in result

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_null_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'data': None})
        api = BTCComAPI()
        result = api.get_latest_block()
        assert 'error' in result

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_invalid_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'data': {'foo': 'bar'}})
        api = BTCComAPI()
        result = api.get_latest_block()
        assert 'error' in result


class TestGetBlockByHeight(object):
    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'data': {'height': 100, 'hash': 'abc', 'timestamp': 123, 'mrkl_root': 'm', 'size': 500}
        })
        api = BTCComAPI()
        result = api.get_block_by_height(100)
        assert result['block']['height'] == 100

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BTCComAPI()
        result = api.get_block_by_height(100)
        assert 'error' in result

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_null_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'data': None})
        api = BTCComAPI()
        result = api.get_block_by_height(100)
        assert 'error' in result


class TestGetBlockByHash(object):
    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'data': {'height': 100, 'hash': 'abc', 'timestamp': 123, 'mrkl_root': 'm', 'size': 500}
        })
        api = BTCComAPI()
        result = api.get_block_by_hash('abc')
        assert result['block']['height'] == 100

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BTCComAPI()
        result = api.get_block_by_hash('abc')
        assert 'error' in result

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_null_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'data': None})
        api = BTCComAPI()
        result = api.get_block_by_hash('abc')
        assert 'error' in result


class TestGetTransactions(object):
    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'data': {
                'total_count': 1,
                'list': [{
                    'hash': 'tx1', 'block_height': 100, 'confirmations': 6, 'witness_hash': 'wtx', 'lock_time': 0,
                    'inputs': [{'prev_addresses': ['addr1'], 'prev_value': 100, 'prev_tx_hash': 'intx', 'prev_position': 0, 'script_hex': 'hex', 'sequence': 1}],
                    'outputs': [{'addresses': ['addr2'], 'value': 50, 'spent_by_tx': None, 'script_hex': '76a9'}]
                }]
            }
        })
        api = BTCComAPI()
        result = api.get_transactions('addr1')
        assert 'transactions' in result

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BTCComAPI()
        result = api.get_transactions('addr1')
        assert 'error' in result

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_null_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'data': None})
        api = BTCComAPI()
        result = api.get_transactions('addr1')
        assert 'error' in result

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_invalid_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'data': {'foo': 'bar'}})
        api = BTCComAPI()
        result = api.get_transactions('addr1')
        assert 'error' in result

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_unconfirmed_tx(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'data': {
                'total_count': 1,
                'list': [{
                    'hash': 'tx1', 'block_height': -1, 'confirmations': 0, 'witness_hash': 'wtx', 'lock_time': 0,
                    'inputs': [], 'outputs': []
                }]
            }
        })
        api = BTCComAPI()
        result = api.get_transactions('addr1')
        assert 'transactions' in result

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_empty_prev_addresses(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'data': {
                'total_count': 1,
                'list': [{
                    'hash': 'tx1', 'block_height': 100, 'confirmations': 6, 'witness_hash': 'wtx', 'lock_time': 0,
                    'inputs': [{'prev_addresses': [], 'prev_value': 100, 'prev_tx_hash': 'intx', 'prev_position': -1, 'script_hex': 'hex', 'sequence': 1}],
                    'outputs': [{'addresses': [], 'value': 50, 'spent_by_tx': 'spent', 'script_hex': '6a0568656c6c6f'}]
                }]
            }
        })
        api = BTCComAPI()
        result = api.get_transactions('addr1')
        assert 'transactions' in result

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_mismatch_count(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(json_data={
                'data': {
                    'total_count': 2,
                    'list': [{
                        'hash': 'tx1', 'block_height': 100, 'confirmations': 6, 'witness_hash': 'wtx', 'lock_time': 0,
                        'inputs': [{'prev_addresses': ['addr1'], 'prev_value': 100, 'prev_tx_hash': 'intx', 'prev_position': 0, 'script_hex': 'hex', 'sequence': 1}],
                        'outputs': [{'addresses': ['addr2'], 'value': 50, 'spent_by_tx': None, 'script_hex': '76a9'}]
                    }]
                }
            }),
            make_mock_response(json_data={
                'data': {
                    'total_count': 2,
                    'list': [{
                        'hash': 'tx2', 'block_height': 101, 'confirmations': 5, 'witness_hash': 'wtx2', 'lock_time': 0,
                        'inputs': [{'prev_addresses': ['addr1'], 'prev_value': 200, 'prev_tx_hash': 'intx2', 'prev_position': 0, 'script_hex': 'hex', 'sequence': 1}],
                        'outputs': [{'addresses': ['addr3'], 'value': 100, 'spent_by_tx': None, 'script_hex': '76a9'}]
                    }, {
                        'hash': 'tx3', 'block_height': 102, 'confirmations': 4, 'witness_hash': 'wtx3', 'lock_time': 0,
                        'inputs': [{'prev_addresses': ['addr1'], 'prev_value': 300, 'prev_tx_hash': 'intx3', 'prev_position': 0, 'script_hex': 'hex', 'sequence': 1}],
                        'outputs': [{'addresses': ['addr4'], 'value': 150, 'spent_by_tx': None, 'script_hex': '76a9'}]
                    }]
                }
            })
        ]
        api = BTCComAPI()
        result = api.get_transactions('addr1')
        assert 'error' in result


class TestGetBalance(object):
    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'data': {'balance': 100, 'received': 200, 'sent': 100, 'unconfirmed_received': 10, 'unconfirmed_sent': 5}
        })
        api = BTCComAPI()
        result = api.get_balance('addr')
        assert result['balance']['final'] == 95
        assert result['balance']['received'] == 190
        assert result['balance']['sent'] == 95

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BTCComAPI()
        result = api.get_balance('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_null_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'data': None})
        api = BTCComAPI()
        result = api.get_balance('addr')
        assert 'error' in result


class TestGetTransaction(object):
    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'data': {
                'witness_hash': 'wtx', 'lock_time': 0, 'block_height': 100, 'confirmations': 6,
                'inputs': [{'prev_addresses': ['addr1'], 'prev_value': 100, 'prev_tx_hash': 'intx', 'prev_position': 0, 'script_hex': 'hex', 'sequence': 1}],
                'outputs': [{'addresses': ['addr2'], 'value': 50, 'spent_by_tx': None, 'script_hex': '76a9'}]
            }
        })
        api = BTCComAPI()
        result = api.get_transaction('txid')
        assert 'transaction' in result

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BTCComAPI()
        result = api.get_transaction('txid')
        assert 'error' in result

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_null_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'data': None})
        api = BTCComAPI()
        # When data is None, code sets data={} then tries data['witness_hash']
        # which raises KeyError (not caught by the try/except)
        with pytest.raises(KeyError):
            api.get_transaction('txid')

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_no_confirmations(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'data': {'witness_hash': 'wtx', 'lock_time': 0, 'block_height': -1,
                     'inputs': [{'prev_addresses': ['addr1'], 'prev_value': 100, 'prev_tx_hash': 'intx', 'prev_position': 0, 'script_hex': 'hex', 'sequence': 1}],
                     'outputs': [{'addresses': ['addr2'], 'value': 50, 'spent_by_tx': None, 'script_hex': '76a9'}]}
        })
        api = BTCComAPI()
        result = api.get_transaction('txid')
        assert 'transaction' in result

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_op_return_output(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'data': {
                'witness_hash': 'wtx', 'lock_time': 0, 'block_height': 100, 'confirmations': 6,
                'inputs': [{'prev_addresses': ['addr1'], 'prev_value': 100, 'prev_tx_hash': 'intx', 'prev_position': 0, 'script_hex': 'hex', 'sequence': 1}],
                'outputs': [{'addresses': [], 'value': 0, 'spent_by_tx': None, 'script_hex': '6a0568656c6c6f'}]
            }
        })
        api = BTCComAPI()
        result = api.get_transaction('txid')
        assert 'transaction' in result


class TestGetPrimeInputAddress(object):
    @mock.patch('data.blockexplorers.btc_com.BTCComAPI.get_transaction')
    def test_success(self, mock_get_tx):
        mock_get_tx.return_value = {'transaction': {'inputs': [{'address': 'b_addr'}, {'address': 'a_addr'}]}}
        api = BTCComAPI()
        result = api.get_prime_input_address('txid')
        assert result['prime_input_address'] == 'a_addr'

    @mock.patch('data.blockexplorers.btc_com.BTCComAPI.get_transaction')
    def test_no_transaction(self, mock_get_tx):
        mock_get_tx.return_value = {'error': 'fail'}
        api = BTCComAPI()
        result = api.get_prime_input_address('txid')
        assert 'error' in result

    @mock.patch('data.blockexplorers.btc_com.BTCComAPI.get_transaction')
    def test_no_inputs(self, mock_get_tx):
        mock_get_tx.return_value = {'transaction': {}}
        api = BTCComAPI()
        result = api.get_prime_input_address('txid')
        assert 'error' in result


class TestGetUtxos(object):
    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'data': {
                'total_count': 1,
                'list': [{'confirmations': 5, 'tx_hash': 'tx1', 'tx_output_n': 0, 'value': 100}]
            }
        })
        api = BTCComAPI()
        result = api.get_utxos('addr')
        assert len(result['utxos']) == 1

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BTCComAPI()
        result = api.get_utxos('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_null_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'data': None})
        api = BTCComAPI()
        result = api.get_utxos('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_invalid_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'data': {'foo': 'bar'}})
        api = BTCComAPI()
        result = api.get_utxos('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_empty_list_stops_pagination(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'data': {'total_count': 5, 'list': []}
        })
        api = BTCComAPI()
        result = api.get_utxos('addr')
        assert 'utxos' in result

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_mismatch_count(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(json_data={
                'data': {
                    'total_count': 2,
                    'list': [{'confirmations': 5, 'tx_hash': 'tx1', 'tx_output_n': 0, 'value': 100}]
                }
            }),
            make_mock_response(json_data={
                'data': {
                    'total_count': 2,
                    'list': [{'confirmations': 5, 'tx_hash': 'tx2', 'tx_output_n': 0, 'value': 100},
                             {'confirmations': 5, 'tx_hash': 'tx3', 'tx_output_n': 0, 'value': 100}]
                }
            })
        ]
        api = BTCComAPI()
        result = api.get_utxos('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.btc_com.requests.get')
    def test_insufficient_confirmations(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'data': {
                'total_count': 1,
                'list': [{'confirmations': 1, 'tx_hash': 'tx1', 'tx_output_n': 0, 'value': 100}]
            }
        })
        api = BTCComAPI()
        result = api.get_utxos('addr', confirmations=3)
        assert len(result['utxos']) == 0


class TestPushTx(object):
    @mock.patch('data.data.get_explorer_api')
    def test_push_tx_delegates(self, mock_get_api):
        mock_bc_api = mock.MagicMock()
        mock_bc_api.push_tx.return_value = {'success': True}
        mock_get_api.return_value = mock_bc_api
        result = BTCComAPI.push_tx('rawtx')
        assert result == {'success': True}
        mock_get_api.assert_called_once_with('blockchain.info')
