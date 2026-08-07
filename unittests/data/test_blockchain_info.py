#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mock

from data.blockexplorers.blockchain_info import BlockchainInfoAPI


def make_mock_response(json_data=None, text_data=None, status_code=200):
    resp = mock.MagicMock()
    resp.status_code = status_code
    if json_data is not None:
        resp.json.return_value = json_data
    if text_data is not None:
        resp.text = text_data
    return resp


class TestBlockchainInfoAPIInit(object):
    def test_init_mainnet(self):
        api = BlockchainInfoAPI()
        assert api.url == 'https://blockchain.info'
        assert api.testnet is False

    def test_init_testnet(self):
        api = BlockchainInfoAPI(testnet=True)
        assert api.url == 'https://testnet.blockchain.info'
        assert api.testnet is True


class TestGetLatestBlock(object):
    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_get_latest_block_success(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(json_data={'height': 100, 'hash': 'abc', 'time': 12345}),
            make_mock_response(json_data={'mrkl_root': 'merkle', 'size': 1000})
        ]
        api = BlockchainInfoAPI()
        result = api.get_latest_block()
        assert result['block']['height'] == 100
        assert result['block']['hash'] == 'abc'
        assert result['block']['merkleroot'] == 'merkle'
        assert result['block']['size'] == 1000

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_get_latest_block_request_error(self, mock_get):
        mock_get.side_effect = Exception('Network error')
        api = BlockchainInfoAPI()
        result = api.get_latest_block()
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_get_latest_block_invalid_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = BlockchainInfoAPI()
        result = api.get_latest_block()
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_get_latest_block_value_error_on_block(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(json_data={'height': 100, 'hash': 'abc', 'time': 12345}),
            mock.MagicMock(status_code=500, text='error', json=mock.MagicMock(side_effect=ValueError('bad json')))
        ]
        api = BlockchainInfoAPI()
        result = api.get_latest_block()
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_get_latest_block_exception_on_block(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(json_data={'height': 100, 'hash': 'abc', 'time': 12345}),
            mock.MagicMock(status_code=500, json=mock.MagicMock(side_effect=Exception('fail')))
        ]
        api = BlockchainInfoAPI()
        result = api.get_latest_block()
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_get_latest_block_missing_keys_in_block(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(json_data={'height': 100, 'hash': 'abc', 'time': 12345}),
            make_mock_response(json_data={'foo': 'bar'})
        ]
        api = BlockchainInfoAPI()
        result = api.get_latest_block()
        assert result['block']['height'] == 100
        assert 'merkleroot' not in result['block']


class TestGetBlockByHash(object):
    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'height': 100, 'hash': 'abc', 'time': 123, 'mrkl_root': 'm', 'size': 500
        })
        api = BlockchainInfoAPI()
        result = api.get_block_by_hash('abc')
        assert result['block']['height'] == 100

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlockchainInfoAPI()
        result = api.get_block_by_hash('abc')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_invalid_data(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = BlockchainInfoAPI()
        result = api.get_block_by_hash('abc')
        assert 'error' in result


class TestGetBlockByHeight(object):
    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'blocks': [{'main_chain': True, 'height': 100, 'hash': 'abc', 'time': 123, 'mrkl_root': 'm', 'size': 500}]
        })
        api = BlockchainInfoAPI()
        result = api.get_block_by_height(100)
        assert result['block']['height'] == 100

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlockchainInfoAPI()
        result = api.get_block_by_height(100)
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_no_blocks_key(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = BlockchainInfoAPI()
        result = api.get_block_by_height(100)
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_no_matching_block(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'blocks': [{'main_chain': False, 'height': 99, 'hash': 'abc', 'time': 123, 'mrkl_root': 'm', 'size': 500}]
        })
        api = BlockchainInfoAPI()
        result = api.get_block_by_height(100)
        assert 'error' in result


class TestGetTransactions(object):
    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    @mock.patch('data.blockexplorers.blockchain_info.BlockchainInfoAPI.get_latest_block_height')
    def test_success(self, mock_height, mock_get):
        mock_height.return_value = 200
        tx_data = {
            'n_tx': 1,
            'txs': [{
                'hash': 'txid1', 'lock_time': 0, 'block_height': 100,
                'inputs': [{'script': 'abc', 'sequence': 1, 'prev_out': {'addr': 'addr1', 'value': 100, 'n': 0}}],
                'out': [{'addr': 'addr2', 'value': 50, 'n': 0, 'spent': True, 'script': '76a9'}]
            }]
        }
        mock_get.return_value = make_mock_response(json_data=tx_data)
        api = BlockchainInfoAPI()
        result = api.get_transactions('addr1')
        assert 'transactions' in result

    @mock.patch('data.blockexplorers.blockchain_info.BlockchainInfoAPI.get_latest_block_height')
    def test_no_latest_block_height(self, mock_height):
        mock_height.return_value = None
        api = BlockchainInfoAPI()
        result = api.get_transactions('addr1')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    @mock.patch('data.blockexplorers.blockchain_info.BlockchainInfoAPI.get_latest_block_height')
    def test_request_error(self, mock_height, mock_get):
        mock_height.return_value = 200
        mock_get.side_effect = Exception('fail')
        api = BlockchainInfoAPI()
        result = api.get_transactions('addr1')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    @mock.patch('data.blockexplorers.blockchain_info.BlockchainInfoAPI.get_latest_block_height')
    def test_invalid_data(self, mock_height, mock_get):
        mock_height.return_value = 200
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = BlockchainInfoAPI()
        result = api.get_transactions('addr1')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    @mock.patch('data.blockexplorers.blockchain_info.BlockchainInfoAPI.get_latest_block_height')
    def test_unconfirmed_tx(self, mock_height, mock_get):
        mock_height.return_value = 200
        tx_data = {
            'n_tx': 1,
            'txs': [{
                'hash': 'txid1', 'lock_time': 0,
                'inputs': [{'script': 'abc', 'sequence': 1}],
                'out': [{'value': 50, 'n': 0, 'spent': True, 'script': '76a9'}]
            }]
        }
        mock_get.return_value = make_mock_response(json_data=tx_data)
        api = BlockchainInfoAPI()
        result = api.get_transactions('addr1')
        assert 'transactions' in result
        assert len(result['transactions']) == 0

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    @mock.patch('data.blockexplorers.blockchain_info.BlockchainInfoAPI.get_latest_block_height')
    def test_op_return_output(self, mock_height, mock_get):
        mock_height.return_value = 200
        tx_data = {
            'n_tx': 1,
            'txs': [{
                'hash': 'txid1', 'lock_time': 0, 'block_height': 100,
                'inputs': [{'script': 'abc', 'sequence': 1, 'prev_out': {'addr': 'addr1', 'value': 100, 'n': 0}}],
                'out': [{'value': 0, 'n': 0, 'spent': False, 'script': '6a0568656c6c6f'}]
            }]
        }
        mock_get.return_value = make_mock_response(json_data=tx_data)
        api = BlockchainInfoAPI()
        result = api.get_transactions('addr1')
        assert 'transactions' in result

    @mock.patch('data.blockexplorers.blockchain_info.sleep')
    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    @mock.patch('data.blockexplorers.blockchain_info.BlockchainInfoAPI.get_latest_block_height')
    def test_pagination_with_sleep(self, mock_height, mock_get, mock_sleep):
        mock_height.return_value = 200
        page1 = {
            'n_tx': 2,
            'txs': [{
                'hash': 'txid1', 'lock_time': 0, 'block_height': 100,
                'inputs': [{'script': 'abc', 'sequence': 1, 'prev_out': {'addr': 'addr1', 'value': 100, 'n': 0}}],
                'out': [{'addr': 'addr2', 'value': 50, 'n': 0, 'spent': True, 'script': '76a9'}]
            }]
        }
        page2 = {
            'n_tx': 2,
            'txs': [{
                'hash': 'txid2', 'lock_time': 0, 'block_height': 101,
                'inputs': [{'script': 'abc', 'sequence': 1, 'prev_out': {'addr': 'addr1', 'value': 100, 'n': 0}}],
                'out': [{'addr': 'addr2', 'value': 50, 'n': 0, 'spent': True, 'script': '76a9'}]
            }]
        }
        mock_get.side_effect = [
            make_mock_response(json_data=page1),
            make_mock_response(json_data=page2)
        ]
        api = BlockchainInfoAPI()
        result = api.get_transactions('addr1')
        assert 'transactions' in result
        assert len(result['transactions']) == 2
        mock_sleep.assert_called_once_with(1)

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    @mock.patch('data.blockexplorers.blockchain_info.BlockchainInfoAPI.get_latest_block_height')
    def test_mismatch_count(self, mock_height, mock_get):
        mock_height.return_value = 200
        tx_data = {
            'n_tx': 1,
            'txs': [
                {
                    'hash': 'txid1', 'lock_time': 0, 'block_height': 100,
                    'inputs': [{'script': 'abc', 'sequence': 1, 'prev_out': {'addr': 'addr1', 'value': 100, 'n': 0}}],
                    'out': [{'addr': 'addr2', 'value': 50, 'n': 0, 'spent': True, 'script': '76a9'}]
                },
                {
                    'hash': 'txid2', 'lock_time': 0, 'block_height': 101,
                    'inputs': [{'script': 'abc', 'sequence': 1, 'prev_out': {'addr': 'addr1', 'value': 100, 'n': 0}}],
                    'out': [{'addr': 'addr2', 'value': 50, 'n': 0, 'spent': True, 'script': '76a9'}]
                }
            ]
        }
        mock_get.return_value = make_mock_response(json_data=tx_data)
        api = BlockchainInfoAPI()
        result = api.get_transactions('addr1')
        assert 'error' in result


class TestGetBalance(object):
    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_success(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(text_data='100'),
            make_mock_response(text_data='200'),
            make_mock_response(text_data='50')
        ]
        api = BlockchainInfoAPI()
        result = api.get_balance('addr')
        assert result['balance']['final'] == 100
        assert result['balance']['received'] == 200
        assert result['balance']['sent'] == 50

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_error_first_request(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlockchainInfoAPI()
        result = api.get_balance('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_error_second_request(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(text_data='100'),
            mock.MagicMock(text='error', json=mock.MagicMock(side_effect=Exception('fail')))
        ]
        api = BlockchainInfoAPI()
        result = api.get_balance('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_error_third_request(self, mock_get):
        mock_get.side_effect = [
            make_mock_response(text_data='100'),
            make_mock_response(text_data='200'),
            mock.MagicMock(text='error', json=mock.MagicMock(side_effect=Exception('fail')))
        ]
        api = BlockchainInfoAPI()
        result = api.get_balance('addr')
        assert 'error' in result


class TestGetTransaction(object):
    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    @mock.patch('data.blockexplorers.blockchain_info.BlockchainInfoAPI.get_latest_block_height')
    def test_success(self, mock_height, mock_get):
        mock_height.return_value = 200
        mock_get.return_value = make_mock_response(json_data={
            'lock_time': 0, 'block_height': 100,
            'inputs': [{'script': 'abc', 'sequence': 1, 'prev_out': {'addr': 'addr1', 'value': 100, 'n': 0}}],
            'out': [{'addr': 'addr2', 'value': 50, 'n': 0, 'spent': True, 'script': '76a9'}]
        })
        api = BlockchainInfoAPI()
        result = api.get_transaction('txid')
        assert 'transaction' in result

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlockchainInfoAPI()
        result = api.get_transaction('txid')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    @mock.patch('data.blockexplorers.blockchain_info.BlockchainInfoAPI.get_latest_block_height')
    def test_no_block_height(self, mock_height, mock_get):
        mock_height.return_value = 200
        mock_get.return_value = make_mock_response(json_data={
            'lock_time': 0,
            'inputs': [{'script': 'abc', 'sequence': 1}],
            'out': [{'value': 50, 'n': 0, 'spent': True, 'script': '76a9'}]
        })
        api = BlockchainInfoAPI()
        result = api.get_transaction('txid')
        assert 'transaction' in result

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    @mock.patch('data.blockexplorers.blockchain_info.BlockchainInfoAPI.get_latest_block_height')
    def test_op_return_output(self, mock_height, mock_get):
        mock_height.return_value = 200
        mock_get.return_value = make_mock_response(json_data={
            'lock_time': 0, 'block_height': 100,
            'inputs': [{'script': 'abc', 'sequence': 1, 'prev_out': {'addr': 'addr1', 'value': 100, 'n': 0}}],
            'out': [{'value': 0, 'n': 0, 'spent': False, 'script': '6a0568656c6c6f'}]
        })
        api = BlockchainInfoAPI()
        result = api.get_transaction('txid')
        assert 'transaction' in result


class TestGetPrimeInputAddress(object):
    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'inputs': [{'prev_out': {'addr': 'b_addr'}}, {'prev_out': {'addr': 'a_addr'}}]
        })
        api = BlockchainInfoAPI()
        result = api.get_prime_input_address('txid')
        assert result['prime_input_address'] == 'a_addr'

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_coinbase_tx(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'inputs': [{}]
        })
        api = BlockchainInfoAPI()
        result = api.get_prime_input_address('txid')
        assert result['prime_input_address'] is None

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlockchainInfoAPI()
        result = api.get_prime_input_address('txid')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_no_inputs_key(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = BlockchainInfoAPI()
        result = api.get_prime_input_address('txid')
        assert 'error' in result


class TestGetUtxos(object):
    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'unspent_outputs': [{
                'confirmations': 5, 'tx_hash_big_endian': 'abc', 'tx_output_n': 0, 'value': 100, 'script': 'hex'
            }]
        })
        api = BlockchainInfoAPI()
        result = api.get_utxos('addr')
        assert len(result['utxos']) == 1

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_no_free_outputs(self, mock_get):
        mock_get.return_value = make_mock_response(text_data='No free outputs to spend')
        api = BlockchainInfoAPI()
        result = api.get_utxos('addr')
        assert result['utxos'] == []

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        api = BlockchainInfoAPI()
        result = api.get_utxos('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_no_unspent_outputs_key(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        api = BlockchainInfoAPI()
        result = api.get_utxos('addr')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockchain_info.requests.get')
    def test_missing_keys_in_output(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={
            'unspent_outputs': [{'confirmations': 5}]
        })
        api = BlockchainInfoAPI()
        result = api.get_utxos('addr')
        assert len(result['utxos']) == 0


class TestPushTx(object):
    @mock.patch('data.blockexplorers.blockchain_info.requests.post')
    def test_success(self, mock_post):
        mock_post.return_value = make_mock_response(text_data='Transaction Submitted', status_code=200)
        api = BlockchainInfoAPI()
        result = api.push_tx('rawtx')
        assert result['success'] is True

    @mock.patch('data.blockexplorers.blockchain_info.requests.post')
    def test_failure(self, mock_post):
        mock_post.return_value = make_mock_response(text_data='Transaction rejected', status_code=400)
        api = BlockchainInfoAPI()
        result = api.push_tx('rawtx')
        assert 'error' in result

    @mock.patch('data.blockexplorers.blockchain_info.requests.post')
    def test_request_error(self, mock_post):
        mock_post.side_effect = Exception('fail')
        api = BlockchainInfoAPI()
        result = api.push_tx('rawtx')
        assert 'error' in result
