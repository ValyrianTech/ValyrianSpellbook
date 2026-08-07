#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mock

from data.blockexplorers.blocktrail_com import BlocktrailComAPI


def make_mock_response(json_data=None, text_data=None, status_code=200):
    resp = mock.MagicMock()
    resp.status_code = status_code
    if json_data is not None:
        resp.json.return_value = json_data
    if text_data is not None:
        resp.text = text_data
    return resp


class TestBlocktrailComAPIInit(object):
    def test_init_mainnet(self):
        api = BlocktrailComAPI(key='mykey')
        assert 'api.blocktrail.com/v1/BTC' in api.url
        assert api.key == 'mykey'

    def test_init_testnet(self):
        api = BlocktrailComAPI(key='mykey', testnet=True)
        assert 'tBTC' in api.url


class TestGetLatestBlock(object):
    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_success(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(json_data={'height': 100, 'hash': 'abc'}),
            make_mock_response(json_data={
                'height': 100, 'hash': 'abc', 'block_time': '2020-01-01T00:00:00+0000',
                'merkleroot': 'm', 'byte_size': 500
            })
        ]
        api = BlocktrailComAPI(key='mykey')
        result = api.get_latest_block()
        assert result['block']['height'] == 100

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlocktrailComAPI(key='mykey')
        result = api.get_latest_block()
        assert 'error' in result

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_invalid_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = BlocktrailComAPI(key='mykey')
        result = api.get_latest_block()
        assert 'error' in result


class TestGetBlockByHeight(object):
    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'height': 100, 'hash': 'abc', 'block_time': '2020-01-01T00:00:00+0000',
            'merkleroot': 'm', 'byte_size': 500
        })
        api = BlocktrailComAPI(key='mykey')
        result = api.get_block_by_height(100)
        assert result['block']['height'] == 100

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlocktrailComAPI(key='mykey')
        result = api.get_block_by_height(100)
        assert 'error' in result

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_invalid_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = BlocktrailComAPI(key='mykey')
        result = api.get_block_by_height(100)
        assert 'error' in result


class TestGetBlockByHash(object):
    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'height': 100, 'hash': 'abc', 'block_time': '2020-01-01T00:00:00+0000',
            'merkleroot': 'm', 'byte_size': 500
        })
        api = BlocktrailComAPI(key='mykey')
        result = api.get_block_by_hash('abc')
        assert result['block']['height'] == 100

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlocktrailComAPI(key='mykey')
        result = api.get_block_by_hash('abc')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_invalid_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = BlocktrailComAPI(key='mykey')
        result = api.get_block_by_hash('abc')
        assert 'error' in result


class TestGetTransactions(object):
    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'total': 1,
            'data': [{
                'hash': 'tx1', 'block_height': 100, 'confirmations': 6,
                'inputs': [{'address': 'addr1', 'value': 100, 'type': 'normal', 'output_hash': 'intx', 'output_index': 0, 'script_signature': 'sig'}],
                'outputs': [{'address': 'addr2', 'value': 50, 'index': 0, 'spent_hash': None, 'script_hex': '76a9'}]
            }]
        })
        api = BlocktrailComAPI(key='mykey')
        result = api.get_transactions('addr1')
        assert 'transactions' in result

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlocktrailComAPI(key='mykey')
        result = api.get_transactions('addr1')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_invalid_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = BlocktrailComAPI(key='mykey')
        result = api.get_transactions('addr1')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_unconfirmed_tx(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'total': 1,
            'data': [{
                'hash': 'tx1', 'block_height': None, 'confirmations': 0,
                'inputs': [], 'outputs': []
            }]
        })
        api = BlocktrailComAPI(key='mykey')
        result = api.get_transactions('addr1')
        assert 'transactions' in result

    @mock.patch('data.blockexplorers.blocktrail_com.sleep')
    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_mismatch_count(self, mock_get, mock_sleep):
        mock_get.side_effect = [
            make_mock_response(json_data={
                'total': 2,
                'data': [{
                    'hash': 'tx1', 'block_height': 100, 'confirmations': 6,
                    'inputs': [{'address': 'addr1', 'value': 100, 'type': 'normal', 'output_hash': 'intx', 'output_index': 0, 'script_signature': 'sig'}],
                    'outputs': [{'address': 'addr2', 'value': 50, 'index': 0, 'spent_hash': None, 'script_hex': '76a9'}]
                }]
            }),
            make_mock_response(json_data={
                'total': 2,
                'data': [{
                    'hash': 'tx2', 'block_height': 101, 'confirmations': 5,
                    'inputs': [{'address': 'addr1', 'value': 100, 'type': 'normal', 'output_hash': 'intx', 'output_index': 0, 'script_signature': 'sig'}],
                    'outputs': [{'address': 'addr2', 'value': 50, 'index': 0, 'spent_hash': None, 'script_hex': '76a9'}]
                }, {
                    'hash': 'tx3', 'block_height': 102, 'confirmations': 4,
                    'inputs': [{'address': 'addr1', 'value': 100, 'type': 'normal', 'output_hash': 'intx', 'output_index': 0, 'script_signature': 'sig'}],
                    'outputs': [{'address': 'addr2', 'value': 50, 'index': 0, 'spent_hash': None, 'script_hex': '76a9'}]
                }]
            })
        ]
        api = BlocktrailComAPI(key='mykey')
        result = api.get_transactions('addr1')
        assert 'transactions' in result
        assert len(result['transactions']) == 3

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_coinbase_input(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'total': 1,
            'data': [{
                'hash': 'tx1', 'block_height': 100, 'confirmations': 6,
                'inputs': [{'address': 'addr1', 'value': 500000, 'type': 'coinbase', 'output_hash': None, 'output_index': None, 'script_signature': 'sig'}],
                'outputs': [{'address': 'addr2', 'value': 50, 'index': 0, 'spent_hash': 'spenthash', 'script_hex': '76a9'}]
            }]
        })
        api = BlocktrailComAPI(key='mykey')
        result = api.get_transactions('addr1')
        assert 'transactions' in result

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_op_return_output(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'total': 1,
            'data': [{
                'hash': 'tx1', 'block_height': 100, 'confirmations': 6,
                'inputs': [{'address': 'addr1', 'value': 100, 'type': 'normal', 'output_hash': 'intx', 'output_index': 0, 'script_signature': 'sig'}],
                'outputs': [{'address': None, 'value': 0, 'index': 0, 'spent_hash': None, 'script_hex': '6a0568656c6c6f'}]
            }]
        })
        api = BlocktrailComAPI(key='mykey')
        result = api.get_transactions('addr1')
        assert 'transactions' in result


class TestGetBalance(object):
    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'balance': 100, 'received': 200, 'sent': 100
        })
        api = BlocktrailComAPI(key='mykey')
        result = api.get_balance('addr')
        assert result['balance']['final'] == 100

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlocktrailComAPI(key='mykey')
        result = api.get_balance('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_invalid_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = BlocktrailComAPI(key='mykey')
        result = api.get_balance('addr')
        assert 'error' in result


class TestGetTransaction(object):
    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'block_height': 100, 'confirmations': 6,
            'inputs': [{'address': 'addr1', 'value': 100, 'type': 'normal', 'output_hash': 'intx', 'output_index': 0, 'script_signature': 'sig', 'sequence': 1}],
            'outputs': [{'address': 'addr2', 'value': 50, 'index': 0, 'spent_hash': None, 'script_hex': '76a9'}]
        })
        api = BlocktrailComAPI(key='mykey')
        result = api.get_transaction('txid')
        assert 'transaction' in result

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlocktrailComAPI(key='mykey')
        result = api.get_transaction('txid')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_no_confirmations(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'inputs': [{'address': 'addr1', 'value': 100, 'type': 'normal', 'output_hash': 'intx', 'output_index': 0, 'script_signature': 'sig', 'sequence': 1}],
            'outputs': [{'address': 'addr2', 'value': 50, 'index': 0, 'spent_hash': None, 'script_hex': '76a9'}]
        })
        api = BlocktrailComAPI(key='mykey')
        result = api.get_transaction('txid')
        assert 'transaction' in result

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_op_return_output(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'block_height': 100, 'confirmations': 6,
            'inputs': [{'address': 'addr1', 'value': 100, 'type': 'normal', 'output_hash': 'intx', 'output_index': 0, 'script_signature': 'sig', 'sequence': 1}],
            'outputs': [{'address': None, 'value': 0, 'index': 0, 'spent_hash': None, 'script_hex': '6a0568656c6c6f'}]
        })
        api = BlocktrailComAPI(key='mykey')
        result = api.get_transaction('txid')
        assert 'transaction' in result


class TestGetPrimeInputAddress(object):
    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'inputs': [{'address': 'b_addr'}, {'address': 'a_addr'}]
        })
        api = BlocktrailComAPI(key='mykey')
        result = api.get_prime_input_address('txid')
        assert result['prime_input_address'] == 'a_addr'

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlocktrailComAPI(key='mykey')
        result = api.get_prime_input_address('txid')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_no_inputs(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = BlocktrailComAPI(key='mykey')
        result = api.get_prime_input_address('txid')
        assert 'error' in result


class TestGetUtxos(object):
    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'total': 1,
            'data': [{'confirmations': 5, 'hash': 'tx1', 'index': 0, 'value': 100, 'script_hex': 'hex'}]
        })
        api = BlocktrailComAPI(key='mykey')
        result = api.get_utxos('addr')
        assert len(result['utxos']) == 1

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlocktrailComAPI(key='mykey')
        result = api.get_utxos('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_invalid_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = BlocktrailComAPI(key='mykey')
        result = api.get_utxos('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_mismatch_count(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'total': 1,
            'data': [
                {'confirmations': 5, 'hash': 'tx1', 'index': 0, 'value': 100, 'script_hex': 'hex'},
                {'confirmations': 5, 'hash': 'tx2', 'index': 0, 'value': 200, 'script_hex': 'hex'}
            ]
        })
        api = BlocktrailComAPI(key='mykey')
        result = api.get_utxos('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blocktrail_com.sleep')
    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_pagination_with_sleep(self, mock_get, mock_sleep):
        mock_get.side_effect = [
            make_mock_response(json_data={
                'total': 2,
                'data': [{'confirmations': 5, 'hash': 'tx1', 'index': 0, 'value': 100, 'script_hex': 'hex'}]
            }),
            make_mock_response(json_data={
                'total': 2,
                'data': [{'confirmations': 5, 'hash': 'tx2', 'index': 0, 'value': 200, 'script_hex': 'hex'}]
            })
        ]
        api = BlocktrailComAPI(key='mykey')
        result = api.get_utxos('addr')
        assert len(result['utxos']) == 2
        mock_sleep.assert_called_once_with(1)

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_insufficient_confirmations(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'total': 1,
            'data': [{'confirmations': 1, 'hash': 'tx1', 'index': 0, 'value': 100, 'script_hex': 'hex'}]
        })
        api = BlocktrailComAPI(key='mykey')
        result = api.get_utxos('addr', confirmations=3)
        assert len(result['utxos']) == 0


class TestGetRecommendedFee(object):
    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'optimal': 100})
        api = BlocktrailComAPI(key='mykey')
        result = api.get_recommended_fee()
        assert result == {'optimal': 100}

    @mock.patch('data.blockexplorers.blocktrail_com.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlocktrailComAPI(key='mykey')
        result = api.get_recommended_fee()
        assert 'error' in result


class TestPushTx(object):
    @mock.patch('data.data.get_explorer_api')
    def test_push_tx_delegates(self, mock_get_api):
        mock_bc_api = mock.MagicMock()
        mock_bc_api.push_tx.return_value = {'success': True}
        mock_get_api.return_value = mock_bc_api
        result = BlocktrailComAPI.push_tx('rawtx')
        assert result == {'success': True}
        mock_get_api.assert_called_once_with('blockchain.info')
