#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mock

from data.blockexplorers.chain_so import ChainSoAPI


def make_mock_response(json_data=None, text_data=None, status_code=200):
    resp = mock.MagicMock()
    resp.status_code = status_code
    if json_data is not None:
        resp.json.return_value = json_data
    if text_data is not None:
        resp.text = text_data
    return resp


class TestChainSoAPIInit(object):
    def test_init_mainnet(self):
        api = ChainSoAPI()
        assert api.network == 'BTC'
        assert api.url == 'https://chain.so/api/v2'

    def test_init_testnet(self):
        api = ChainSoAPI(testnet=True)
        assert api.network == 'BTCTEST'


class TestGetLatestBlock(object):
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_success(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(json_data={'data': {'blocks': 100}}),
            make_mock_response(json_data={
                'data': {'block_no': 100, 'blockhash': 'abc', 'time': 123, 'merkleroot': 'm', 'size': 500}
            })
        ]
        api = ChainSoAPI()
        result = api.get_latest_block()
        assert result['block']['height'] == 100

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = ChainSoAPI()
        result = api.get_latest_block()
        assert 'error' in result
        assert 'Unable to get latest block from Chain.so' in result['error']

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_no_data_key(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = ChainSoAPI()
        result = api.get_latest_block()
        assert 'error' in result

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_no_blocks_key(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'data': {'foo': 'bar'}})
        api = ChainSoAPI()
        result = api.get_latest_block()
        assert 'error' in result


class TestGetBlockByHeight(object):
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'data': {'block_no': 100, 'blockhash': 'abc', 'time': 123, 'merkleroot': 'm', 'size': 500}
        })
        api = ChainSoAPI()
        result = api.get_block_by_height(100)
        assert result['block']['height'] == 100

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = ChainSoAPI()
        result = api.get_block_by_height(100)
        assert 'error' in result

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_no_data_key(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = ChainSoAPI()
        result = api.get_block_by_height(100)
        assert 'error' in result

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_invalid_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'data': {'foo': 'bar'}})
        api = ChainSoAPI()
        result = api.get_block_by_height(100)
        assert 'error' in result


class TestGetBlockByHash(object):
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'data': {'block_no': 100, 'blockhash': 'abc', 'time': 123, 'merkleroot': 'm', 'size': 500}
        })
        api = ChainSoAPI()
        result = api.get_block_by_hash('abc')
        assert result['block']['height'] == 100

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = ChainSoAPI()
        result = api.get_block_by_hash('abc')
        assert 'error' in result

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_no_data_key(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = ChainSoAPI()
        result = api.get_block_by_hash('abc')
        assert 'error' in result

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_invalid_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'data': {'foo': 'bar'}})
        api = ChainSoAPI()
        result = api.get_block_by_hash('abc')
        assert 'error' in result


class TestGetTransactions(object):
    @mock.patch('data.blockexplorers.chain_so.sleep')
    @mock.patch('data.blockexplorers.chain_so.ChainSoAPI.get_transaction')
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_success(self, mock_get, mock_get_tx, mock_sleep):
        mock_get.return_value = make_mock_response(json_data={
            'data': {'txs': [{'txid': 'tx1'}, {'txid': 'tx2'}]}
        })
        mock_get_tx.return_value = {'transaction': {'txid': 'tx1'}}
        api = ChainSoAPI()
        result = api.get_transactions('addr1')
        assert 'transactions' in result
        assert len(result['transactions']) == 2

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = ChainSoAPI()
        result = api.get_transactions('addr1')
        assert 'error' in result

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_no_data_key(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = ChainSoAPI()
        result = api.get_transactions('addr1')
        assert 'error' in result

    @mock.patch('data.blockexplorers.chain_so.sleep')
    @mock.patch('data.blockexplorers.chain_so.ChainSoAPI.get_transaction')
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_transaction_error(self, mock_get, mock_get_tx, mock_sleep):
        mock_get.return_value = make_mock_response(json_data={
            'data': {'txs': [{'txid': 'tx1'}]}
        })
        mock_get_tx.return_value = {'error': 'fail'}
        api = ChainSoAPI()
        result = api.get_transactions('addr1')
        assert 'transactions' in result
        assert len(result['transactions']) == 0


class TestGetBalance(object):
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'data': {'balance': '0.001', 'received_value': '0.002'}
        })
        api = ChainSoAPI()
        result = api.get_balance('addr')
        assert 'balance' in result

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = ChainSoAPI()
        result = api.get_balance('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_no_data_key(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = ChainSoAPI()
        result = api.get_balance('addr')
        assert 'error' in result


class TestGetUtxos(object):
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'data': {'txs': [{'confirmations': 5, 'txid': 'tx1', 'output_no': 0, 'value': '0.001', 'script_hex': 'hex'}]}
        })
        api = ChainSoAPI()
        result = api.get_utxos('addr')
        assert len(result['utxos']) == 1

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = ChainSoAPI()
        result = api.get_utxos('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_no_data_key(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = ChainSoAPI()
        result = api.get_utxos('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_missing_keys(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'data': {'txs': [{'confirmations': 5}]}
        })
        api = ChainSoAPI()
        result = api.get_utxos('addr')
        assert len(result['utxos']) == 0


class TestGetTransaction(object):
    @mock.patch('data.blockexplorers.chain_so.ChainSoAPI.get_block_by_hash')
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_success(self, mock_get, mock_get_block):
        mock_get.return_value = make_mock_response(json_data={
            'data': {
                'blockhash': 'abc', 'confirmations': 6,
                'inputs': [{'address': 'addr1', 'value': '0.001', 'from_output': {'txid': 'intx', 'output_no': 0}, 'script': 'sig'}],
                'outputs': [{'address': 'addr2', 'value': '0.0005', 'output_no': 0, 'script': '76a9'}]
            }
        })
        mock_get_block.return_value = {'block': {'height': 100}}
        api = ChainSoAPI()
        result = api.get_transaction('txid')
        assert 'transaction' in result

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = ChainSoAPI()
        result = api.get_transaction('txid')
        assert 'error' in result

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_no_data_key(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = ChainSoAPI()
        result = api.get_transaction('txid')
        assert 'error' in result

    @mock.patch('data.blockexplorers.chain_so.ChainSoAPI.get_block_by_hash')
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_block_error(self, mock_get, mock_get_block):
        mock_get.return_value = make_mock_response(json_data={
            'data': {'blockhash': 'abc', 'confirmations': 6, 'inputs': [], 'outputs': []}
        })
        mock_get_block.return_value = {'error': 'fail'}
        api = ChainSoAPI()
        result = api.get_transaction('txid')
        assert 'error' in result

    @mock.patch('data.blockexplorers.chain_so.ChainSoAPI.get_block_by_hash')
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_coinbase_input(self, mock_get, mock_get_block):
        mock_get.return_value = make_mock_response(json_data={
            'data': {
                'blockhash': 'abc', 'confirmations': 6,
                'inputs': [{'address': 'coinbase', 'value': '0.001', 'from_output': None, 'script': 'sig'}],
                'outputs': [{'address': 'addr2', 'value': '0.0005', 'output_no': 0, 'script': '76a9'}]
            }
        })
        mock_get_block.return_value = {'block': {'height': 100}}
        api = ChainSoAPI()
        result = api.get_transaction('txid')
        assert 'transaction' in result

    @mock.patch('data.blockexplorers.chain_so.ChainSoAPI.get_block_by_hash')
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_nonstandard_output(self, mock_get, mock_get_block):
        mock_get.return_value = make_mock_response(json_data={
            'data': {
                'blockhash': 'abc', 'confirmations': 6,
                'inputs': [{'address': 'addr1', 'value': '0.001', 'from_output': {'txid': 'intx', 'output_no': 0}, 'script': 'sig'}],
                'outputs': [{'address': 'nonstandard', 'value': '0.0005', 'output_no': 0, 'script': 'OP_RETURN 68656c6c6f'}]
            }
        })
        mock_get_block.return_value = {'block': {'height': 100}}
        api = ChainSoAPI()
        result = api.get_transaction('txid')
        assert 'transaction' in result

    @mock.patch('data.blockexplorers.chain_so.ChainSoAPI.get_block_by_hash')
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_op_return_cp1252_fallback(self, mock_get, mock_get_block):
        mock_get.return_value = make_mock_response(json_data={
            'data': {
                'blockhash': 'abc', 'confirmations': 6,
                'inputs': [{'address': 'addr1', 'value': '0.001', 'from_output': {'txid': 'intx', 'output_no': 0}, 'script': 'sig'}],
                'outputs': [{'address': 'nonstandard', 'value': '0', 'output_no': 0, 'script': 'OP_RETURN 80'}]
            }
        })
        mock_get_block.return_value = {'block': {'height': 100}}
        api = ChainSoAPI()
        result = api.get_transaction('txid')
        assert 'transaction' in result

    @mock.patch('data.blockexplorers.chain_so.ChainSoAPI.get_block_by_hash')
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_op_return_decode_error(self, mock_get, mock_get_block):
        mock_get.return_value = make_mock_response(json_data={
            'data': {
                'blockhash': 'abc', 'confirmations': 6,
                'inputs': [{'address': 'addr1', 'value': '0.001', 'from_output': {'txid': 'intx', 'output_no': 0}, 'script': 'sig'}],
                'outputs': [{'address': 'nonstandard', 'value': '0', 'output_no': 0, 'script': 'OP_RETURN 81'}]
            }
        })
        mock_get_block.return_value = {'block': {'height': 100}}
        api = ChainSoAPI()
        result = api.get_transaction('txid')
        assert 'transaction' in result


class TestGetPrimeInputAddress(object):
    @mock.patch('data.blockexplorers.chain_so.ChainSoAPI.get_transaction')
    def test_success(self, mock_get_tx):
        mock_get_tx.return_value = {'transaction': {'inputs': [{'address': 'b_addr'}, {'address': 'a_addr'}]}}
        api = ChainSoAPI()
        result = api.get_prime_input_address('txid')
        assert result['prime_input_address'] == 'a_addr'

    @mock.patch('data.blockexplorers.chain_so.ChainSoAPI.get_transaction')
    def test_no_transaction(self, mock_get_tx):
        mock_get_tx.return_value = {'error': 'fail'}
        api = ChainSoAPI()
        result = api.get_prime_input_address('txid')
        assert 'error' in result

    @mock.patch('data.blockexplorers.chain_so.ChainSoAPI.get_transaction')
    def test_no_inputs(self, mock_get_tx):
        mock_get_tx.return_value = {'transaction': {}}
        api = ChainSoAPI()
        result = api.get_prime_input_address('txid')
        assert 'error' in result
