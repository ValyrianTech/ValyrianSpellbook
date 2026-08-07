#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mock

from data.blockexplorers.insight import InsightAPI


def make_mock_response(json_data=None, text_data=None, status_code=200):
    resp = mock.MagicMock()
    resp.status_code = status_code
    if json_data is not None:
        resp.json.return_value = json_data
    if text_data is not None:
        resp.text = text_data
    return resp


class TestInsightAPIInit(object):
    def test_init(self):
        api = InsightAPI(url='http://example.com')
        assert api.url == 'http://example.com'


class TestGetLatestBlock(object):
    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_success(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(json_data={'bestblockhash': 'abc'}),
            make_mock_response(json_data={'height': 100, 'hash': 'abc', 'time': 123, 'merkleroot': 'm', 'size': 500})
        ]
        api = InsightAPI(url='http://example.com')
        result = api.get_latest_block()
        assert result['block']['height'] == 100

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = InsightAPI(url='http://example.com')
        result = api.get_latest_block()
        assert 'error' in result

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_no_bestblockhash(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = InsightAPI(url='http://example.com')
        result = api.get_latest_block()
        assert 'error' in result


class TestGetBlockByHash(object):
    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'height': 100, 'hash': 'abc', 'time': 123, 'merkleroot': 'm', 'size': 500
        })
        api = InsightAPI(url='http://example.com')
        result = api.get_block_by_hash('abc')
        assert result['block']['height'] == 100

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = InsightAPI(url='http://example.com')
        result = api.get_block_by_hash('abc')
        assert 'error' in result

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_invalid_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = InsightAPI(url='http://example.com')
        result = api.get_block_by_hash('abc')
        assert 'error' in result


class TestGetBlockByHeight(object):
    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_success(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(json_data={'blockHash': 'abc'}),
            make_mock_response(json_data={'height': 100, 'hash': 'abc', 'time': 123, 'merkleroot': 'm', 'size': 500})
        ]
        api = InsightAPI(url='http://example.com')
        result = api.get_block_by_height(100)
        assert result['block']['height'] == 100

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = InsightAPI(url='http://example.com')
        result = api.get_block_by_height(100)
        assert 'error' in result

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_no_blockhash(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = InsightAPI(url='http://example.com')
        result = api.get_block_by_height(100)
        assert 'error' in result


class TestGetTransactions(object):
    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'totalItems': 1,
            'items': [{
                'txid': 'tx1', 'locktime': 0, 'confirmations': 6, 'blockheight': 100,
                'vin': [{'addr': 'addr1', 'valueSat': 100, 'txid': 'intx', 'vout': 0, 'scriptSig': {'hex': 'sig'}, 'sequence': 1}],
                'vout': [{'scriptPubKey': {'addresses': ['addr2'], 'hex': '76a9'}, 'value': '0.00000050', 'n': 0, 'spentTxId': None}]
            }]
        })
        api = InsightAPI(url='http://example.com')
        result = api.get_transactions('addr1')
        assert 'transactions' in result

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = InsightAPI(url='http://example.com')
        result = api.get_transactions('addr1')
        assert 'error' in result

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_invalid_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = InsightAPI(url='http://example.com')
        result = api.get_transactions('addr1')
        assert 'error' in result

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_unconfirmed_tx(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'totalItems': 1,
            'items': [{
                'txid': 'tx1', 'locktime': 0, 'confirmations': 0, 'blockheight': -1,
                'vin': [], 'vout': []
            }]
        })
        api = InsightAPI(url='http://example.com')
        result = api.get_transactions('addr1')
        assert 'transactions' in result

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_mismatch_count(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(json_data={
                'totalItems': 2,
                'items': [{
                    'txid': 'tx1', 'locktime': 0, 'confirmations': 6, 'blockheight': 100,
                    'vin': [{'addr': 'addr1', 'valueSat': 100, 'txid': 'intx', 'vout': 0, 'scriptSig': {'hex': 'sig'}, 'sequence': 1}],
                    'vout': [{'scriptPubKey': {'addresses': ['addr2'], 'hex': '76a9'}, 'value': '0.00000050', 'n': 0, 'spentTxId': None}]
                }]
            }),
            make_mock_response(json_data={
                'totalItems': 2,
                'items': [{
                    'txid': 'tx2', 'locktime': 0, 'confirmations': 5, 'blockheight': 101,
                    'vin': [{'addr': 'addr1', 'valueSat': 200, 'txid': 'intx2', 'vout': 0, 'scriptSig': {'hex': 'sig'}, 'sequence': 1}],
                    'vout': [{'scriptPubKey': {'addresses': ['addr3'], 'hex': '76a9'}, 'value': '0.00000100', 'n': 0, 'spentTxId': None}]
                }, {
                    'txid': 'tx3', 'locktime': 0, 'confirmations': 4, 'blockheight': 102,
                    'vin': [{'addr': 'addr1', 'valueSat': 300, 'txid': 'intx3', 'vout': 0, 'scriptSig': {'hex': 'sig'}, 'sequence': 1}],
                    'vout': [{'scriptPubKey': {'addresses': ['addr4'], 'hex': '76a9'}, 'value': '0.00000150', 'n': 0, 'spentTxId': None}]
                }]
            })
        ]
        api = InsightAPI(url='http://example.com')
        result = api.get_transactions('addr1')
        assert 'error' in result

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_coinbase_input(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'totalItems': 1,
            'items': [{
                'txid': 'tx1', 'locktime': 0, 'confirmations': 6, 'blockheight': 100,
                'vin': [{'coinbase': 'hex', 'sequence': 1}],
                'vout': [{'scriptPubKey': {'hex': '76a9'}, 'value': '0.00000050', 'n': 0, 'spentTxId': None}]
            }]
        })
        api = InsightAPI(url='http://example.com')
        result = api.get_transactions('addr1')
        assert 'transactions' in result

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_op_return_output(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'totalItems': 1,
            'items': [{
                'txid': 'tx1', 'locktime': 0, 'confirmations': 6, 'blockheight': 100,
                'vin': [{'addr': 'addr1', 'valueSat': 100, 'txid': 'intx', 'vout': 0, 'scriptSig': {'hex': 'sig'}, 'sequence': 1}],
                'vout': [{'scriptPubKey': {'hex': '6a0568656c6c6f'}, 'value': '0.00000000', 'n': 0, 'spentTxId': None}]
            }]
        })
        api = InsightAPI(url='http://example.com')
        result = api.get_transactions('addr1')
        assert 'transactions' in result

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_no_addresses_in_vout(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'totalItems': 1,
            'items': [{
                'txid': 'tx1', 'locktime': 0, 'confirmations': 6, 'blockheight': 100,
                'vin': [{'addr': 'addr1', 'valueSat': 100, 'txid': 'intx', 'vout': 0, 'scriptSig': {'hex': 'sig'}, 'sequence': 1}],
                'vout': [{'scriptPubKey': {'hex': '76a9'}, 'value': '0.00000050', 'n': 0, 'spentTxId': 'spent'}]
            }]
        })
        api = InsightAPI(url='http://example.com')
        result = api.get_transactions('addr1')
        assert 'transactions' in result


class TestGetBalance(object):
    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_success(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(text_data='100'),
            make_mock_response(text_data='200'),
            make_mock_response(text_data='50')
        ]
        api = InsightAPI(url='http://example.com')
        result = api.get_balance('addr')
        assert result['balance']['final'] == 100
        assert result['balance']['received'] == 200
        assert result['balance']['sent'] == 50

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_error_first_request(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = InsightAPI(url='http://example.com')
        result = api.get_balance('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_error_second_request(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(text_data='100'),
            mock.MagicMock(text='error', json=mock.MagicMock(side_effect=Exception('fail')))
        ]
        api = InsightAPI(url='http://example.com')
        result = api.get_balance('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_error_third_request(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(text_data='100'),
            make_mock_response(text_data='200'),
            mock.MagicMock(text='error', json=mock.MagicMock(side_effect=Exception('fail')))
        ]
        api = InsightAPI(url='http://example.com')
        result = api.get_balance('addr')
        assert 'error' in result


class TestGetTransaction(object):
    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'blockheight': 100, 'locktime': 0, 'confirmations': 6,
            'vin': [{'addr': 'addr1', 'valueSat': 100, 'txid': 'intx', 'n': 0, 'scriptSig': {'hex': 'sig'}, 'sequence': 1}],
            'vout': [{'scriptPubKey': {'addresses': ['addr2'], 'hex': '76a9'}, 'value': 0.00000050, 'n': 0, 'spentTxId': None}]
        })
        api = InsightAPI(url='http://example.com')
        result = api.get_transaction('txid')
        assert 'transaction' in result

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = InsightAPI(url='http://example.com')
        result = api.get_transaction('txid')
        assert 'error' in result

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_no_blockheight(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'locktime': 0,
            'vin': [{'addr': 'addr1', 'valueSat': 100, 'txid': 'intx', 'n': 0, 'scriptSig': {'hex': 'sig'}, 'sequence': 1}],
            'vout': [{'scriptPubKey': {'addresses': ['addr2'], 'hex': '76a9'}, 'value': 0.00000050, 'n': 0, 'spentTxId': None}]
        })
        api = InsightAPI(url='http://example.com')
        result = api.get_transaction('txid')
        assert 'transaction' in result

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_coinbase_input(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'blockheight': 100, 'locktime': 0, 'confirmations': 6,
            'vin': [{'coinbase': 'hex', 'sequence': 1}],
            'vout': [{'scriptPubKey': {'hex': '76a9'}, 'value': 0.00000050, 'n': 0, 'spentTxId': 'spent'}]
        })
        api = InsightAPI(url='http://example.com')
        result = api.get_transaction('txid')
        assert 'transaction' in result

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_no_confirmations(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'blockheight': 100, 'locktime': 0,
            'vin': [{'addr': 'addr1', 'valueSat': 100, 'txid': 'intx', 'n': 0, 'scriptSig': {'hex': 'sig'}, 'sequence': 1}],
            'vout': [{'scriptPubKey': {'addresses': ['addr2'], 'hex': '76a9'}, 'value': 0.00000050, 'n': 0, 'spentTxId': None}]
        })
        api = InsightAPI(url='http://example.com')
        result = api.get_transaction('txid')
        assert 'transaction' in result

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_op_return_output(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'blockheight': 100, 'locktime': 0, 'confirmations': 6,
            'vin': [{'addr': 'addr1', 'valueSat': 100, 'txid': 'intx', 'n': 0, 'scriptSig': {'hex': 'sig'}, 'sequence': 1}],
            'vout': [{'scriptPubKey': {'hex': '6a0568656c6c6f'}, 'value': 0.0, 'n': 0, 'spentTxId': None}]
        })
        api = InsightAPI(url='http://example.com')
        result = api.get_transaction('txid')
        assert 'transaction' in result


class TestGetPrimeInputAddress(object):
    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'vin': [{'addr': 'b_addr'}, {'addr': 'a_addr'}]
        })
        api = InsightAPI(url='http://example.com')
        result = api.get_prime_input_address('txid')
        assert result['prime_input_address'] == 'a_addr'

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = InsightAPI(url='http://example.com')
        result = api.get_prime_input_address('txid')
        assert 'error' in result

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_no_vin(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = InsightAPI(url='http://example.com')
        result = api.get_prime_input_address('txid')
        assert 'error' in result


class TestGetUtxos(object):
    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data=[{
            'confirmations': 5, 'txid': 'tx1', 'vout': 0, 'satoshis': 100, 'scriptPubKey': 'hex'
        }])
        api = InsightAPI(url='http://example.com')
        result = api.get_utxos('addr')
        assert len(result['utxos']) == 1

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = InsightAPI(url='http://example.com')
        result = api.get_utxos('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_missing_keys(self, mock_get):
        mock_get.return_value = make_mock_response(json_data=[{'confirmations': 5}])
        api = InsightAPI(url='http://example.com')
        result = api.get_utxos('addr')
        assert len(result['utxos']) == 0

    @mock.patch('data.blockexplorers.insight.requests.get')
    def test_insufficient_confirmations(self, mock_get):
        mock_get.return_value = make_mock_response(json_data=[{
            'confirmations': 1, 'txid': 'tx1', 'vout': 0, 'satoshis': 100, 'scriptPubKey': 'hex'
        }])
        api = InsightAPI(url='http://example.com')
        result = api.get_utxos('addr', confirmations=3)
        assert len(result['utxos']) == 0


class TestPushTx(object):
    @mock.patch('data.blockexplorers.insight.requests.post')
    def test_success(self, mock_post):
        mock_post.return_value = make_mock_response(json_data={'txid': 'newtx'}, status_code=200)
        api = InsightAPI(url='http://example.com')
        result = api.push_tx('rawtx')
        assert result['success'] is True

    @mock.patch('data.blockexplorers.insight.requests.post')
    def test_failure_status_code(self, mock_post):
        mock_post.return_value = make_mock_response(json_data={'error': 'bad tx'}, status_code=400)
        api = InsightAPI(url='http://example.com')
        result = api.push_tx('rawtx')
        assert 'error' in result

    @mock.patch('data.blockexplorers.insight.requests.post')
    def test_no_txid_in_response(self, mock_post):
        mock_post.return_value = make_mock_response(json_data={'foo': 'bar'}, status_code=200)
        api = InsightAPI(url='http://example.com')
        result = api.push_tx('rawtx')
        assert 'error' in result

    @mock.patch('data.blockexplorers.insight.requests.post')
    def test_value_error_on_json(self, mock_post):
        mock_post.return_value = mock.MagicMock(status_code=400, text='error text', json=mock.MagicMock(side_effect=ValueError('bad json')))
        api = InsightAPI(url='http://example.com')
        result = api.push_tx('rawtx')
        assert 'error' in result

    @mock.patch('data.blockexplorers.insight.requests.post')
    def test_request_error(self, mock_post):
        mock_post.side_effect = Exception('fail')
        api = InsightAPI(url='http://example.com')
        result = api.push_tx('rawtx')
        assert 'error' in result
