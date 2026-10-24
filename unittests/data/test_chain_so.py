#!/usr/bin/env python
from unittest import mock

import requests

from data.blockexplorers.chain_so import ChainSoAPI
from data.blockexplorers.explorer_http import DEFAULT_TIMEOUT

BASE = 'https://sochain.com/api/v3'


def make_mock_response(json_data=None, text_data=None, status_code=200):
    resp = mock.MagicMock()
    resp.status_code = status_code
    if json_data is not None:
        resp.json.return_value = json_data
    if text_data is not None:
        resp.text = text_data
    return resp


def success(data):
    return make_mock_response(json_data={'status': 'success', 'data': data})


BLOCK = {'height': 100, 'hash': 'abc', 'time': 123, 'merkleroot': 'm', 'size': 500}

TRANSACTION = {
    'hash': 'tx1', 'block_height': 100, 'block_hash': 'abc', 'confirmations': 6, 'locktime': 0, 'time': 123,
    'inputs': [{'index': 0, 'value': '0.00100000', 'address': 'addr1',
                'scriptSig': {'hex': 'sig', 'asm': ''}, 'witness': [],
                'previous_output': {'hash': 'intx', 'index': 1}, 'sequence': 4294967295}],
    'outputs': [{'index': 0, 'value': '0.00050000', 'address': 'addr2', 'type': 'pubkeyhash',
                 'script': {'hex': '76a9', 'asm': ''}, 'spent': None, 'is_change': None},
                {'index': 1, 'value': '0.00040000', 'address': 'addr1', 'type': 'pubkeyhash',
                 'script': {'hex': '76a8', 'asm': ''}, 'spent': {'hash': 'next', 'index': 0}, 'is_change': True}]
}


def utxo(n, block=95):
    return {'hash': f'tx{n}', 'index': n % 2, 'script': '76a9', 'address': 'addr', 'value': '0.00000001', 'block': block, 'tx_hex': ''}


class TestChainSoAPIInit:
    def test_init_mainnet(self):
        api = ChainSoAPI()
        assert api.network == 'BTC'
        assert api.url == BASE

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_init_testnet_makes_no_request(self, mock_get):
        api = ChainSoAPI(testnet=True)
        assert 'error' in api.get_latest_block()
        assert 'error' in api.get_balance('addr')
        mock_get.assert_not_called()


class TestApiKey:
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_key_sent_as_header(self, mock_get):
        mock_get.return_value = success(BLOCK)
        ChainSoAPI(key='k').get_block_by_height(100)
        assert mock_get.call_args.kwargs['headers'] == {'API-KEY': 'k'}

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_no_key_no_header(self, mock_get):
        mock_get.return_value = success(BLOCK)
        ChainSoAPI().get_block_by_height(100)
        assert mock_get.call_args.kwargs['headers'] is None


class TestGetLatestBlock:
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_success(self, mock_get):
        mock_get.side_effect = [success({'block_count': 100}), success(BLOCK)]
        api = ChainSoAPI()
        result = api.get_latest_block()
        assert result['block']['height'] == 100
        assert mock_get.call_args_list[0].args[0] == f'{BASE}/network_info/BTC'
        assert mock_get.call_args_list[1].args[0] == f'{BASE}/block/BTC/100'

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = ValueError('fail')
        api = ChainSoAPI()
        result = api.get_latest_block()
        assert 'error' in result
        assert 'Unable to get latest block from SoChain' in result['error']

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_fail_status(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'status': 'fail', 'data': {'error_message': 'x'}})
        api = ChainSoAPI()
        result = api.get_latest_block()
        assert 'error' in result

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_no_block_count_key(self, mock_get):
        mock_get.return_value = success({'foo': 'bar'})
        api = ChainSoAPI()
        result = api.get_latest_block()
        assert 'error' in result


class TestGetBlock:
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_by_height(self, mock_get):
        mock_get.return_value = success(BLOCK)
        result = ChainSoAPI().get_block_by_height(100)
        assert result['block'] == {'height': 100, 'hash': 'abc', 'time': 123, 'merkleroot': 'm', 'size': 500}

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_by_hash(self, mock_get):
        mock_get.return_value = success(BLOCK)
        result = ChainSoAPI().get_block_by_hash('abc')
        assert result['block']['height'] == 100
        assert mock_get.call_args.args[0] == f'{BASE}/block/BTC/abc'

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError('fail')
        assert 'error' in ChainSoAPI().get_block_by_height(100)

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_no_data_key(self, mock_get):
        mock_get.return_value = make_mock_response(json_data={'foo': 'bar'})
        assert 'error' in ChainSoAPI().get_block_by_hash('abc')

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_invalid_data(self, mock_get):
        mock_get.return_value = success({'foo': 'bar'})
        assert 'error' in ChainSoAPI().get_block_by_height(100)


class TestGetTransaction:
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = success(TRANSACTION)
        result = ChainSoAPI().get_transaction('tx1')
        tx = result['transaction']
        assert mock_get.call_args.args[0] == f'{BASE}/transaction/BTC/tx1'
        assert tx['txid'] == 'tx1'
        assert tx['block_height'] == 100
        assert tx['confirmations'] == 6
        assert tx['inputs'][0] == {'address': 'addr1', 'value': 100000, 'txid': 'intx', 'n': 1, 'script': 'sig', 'sequence': 4294967295}
        assert tx['outputs'][0]['value'] == 50000
        assert tx['outputs'][0]['spent'] is False
        assert tx['outputs'][1]['spent'] is True
        assert tx['outputs'][1]['script'] == '76a8'

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_coinbase_input(self, mock_get):
        data = dict(TRANSACTION, inputs=[{'index': 0, 'value': '0.00000000', 'address': None, 'scriptSig': {'hex': '03ab', 'asm': ''},
                                          'witness': [], 'previous_output': None, 'sequence': 4294967295}])
        mock_get.return_value = success(data)
        tx = ChainSoAPI().get_transaction('tx1')['transaction']
        assert tx['inputs'][0]['address'] is None
        assert tx['inputs'][0]['value'] == 0
        assert tx['inputs'][0]['txid'] is None

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_op_return_output(self, mock_get):
        data = dict(TRANSACTION, outputs=[{'index': 0, 'value': '0.00000000', 'address': 'op_return', 'type': 'nulldata',
                                           'script': {'hex': '6a0568656c6c6f', 'asm': ''}, 'spent': None, 'is_change': None}])
        mock_get.return_value = success(data)
        tx = ChainSoAPI().get_transaction('tx1')['transaction']
        assert tx['outputs'][0]['address'] is None
        assert tx['outputs'][0]['op_return'] == 'hello'

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_exact_amounts(self, mock_get):
        data = dict(TRANSACTION, outputs=[dict(TRANSACTION['outputs'][0], value='20999999.97690000')])
        mock_get.return_value = success(data)
        tx = ChainSoAPI().get_transaction('tx1')['transaction']
        assert tx['outputs'][0]['value'] == 2099999997690000

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = ValueError('fail')
        assert 'error' in ChainSoAPI().get_transaction('tx1')

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_invalid_data(self, mock_get):
        mock_get.return_value = success({'hash': 'tx1'})
        assert 'error' in ChainSoAPI().get_transaction('tx1')


class TestGetTransactions:
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_success_with_cursor(self, mock_get):
        mock_get.side_effect = [
            success({'transactions': [{'hash': 'tx1'}], 'next_cursor': 'c1'}),
            success({'transactions': [{'hash': 'tx1'}], 'next_cursor': None}),
            success(TRANSACTION),
            success(TRANSACTION),
        ]
        result = ChainSoAPI().get_transactions('addr2')
        assert len(result['transactions']) == 2
        assert mock_get.call_args_list[0].kwargs['params'] == {'unconfirmed': 'exclude', 'page_size': 100}
        assert mock_get.call_args_list[1].kwargs['params'] == {'cursor': 'c1'}
        assert result['transactions'][0]['receiving'] is True
        assert result['transactions'][0]['receivedValue'] == 50000

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = ValueError('fail')
        assert 'error' in ChainSoAPI().get_transactions('addr1')

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_transaction_error(self, mock_get):
        mock_get.side_effect = [
            success({'transactions': [{'hash': 'tx1'}], 'next_cursor': None}),
            make_mock_response(json_data={'status': 'fail', 'data': {'error_message': 'x'}}),
        ]
        assert 'error' in ChainSoAPI().get_transactions('addr1')


class TestGetBalance:
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_success(self, mock_get):
        mock_get.return_value = success({'txs_sent': 1, 'txs_received': 2, 'txs_total': 2,
                                         'confirmed_balance': '0.00100000', 'unconfirmed_balance': '0.00000000',
                                         'confirmed_received': '0.00200000'})
        result = ChainSoAPI().get_balance('addr')
        assert result['balance'] == {'final': 100000, 'received': 200000, 'sent': 100000}
        assert mock_get.call_args.args[0] == f'{BASE}/address_summary/BTC/addr'

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = ValueError('fail')
        assert 'error' in ChainSoAPI().get_balance('addr')

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_missing_keys(self, mock_get):
        mock_get.return_value = success({'foo': 'bar'})
        assert 'error' in ChainSoAPI().get_balance('addr')


class TestGetUtxos:
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_success_paged(self, mock_get):
        mock_get.side_effect = [
            success({'block_count': 100}),
            success({'outputs': [utxo(n) for n in range(10)]}),
            success({'outputs': [utxo(10), utxo(11, block=99), utxo(12, block=None)]}),
        ]
        result = ChainSoAPI().get_utxos('addr')
        assert len(result['utxos']) == 11
        assert result['utxos'][0] == {'confirmations': 6, 'output_hash': 'tx0', 'output_n': 0, 'value': 1, 'script': '76a9'}
        assert mock_get.call_args_list[2].args[0] == f'{BASE}/unspent_outputs/BTC/addr/2'

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_confirmations_zero_includes_unconfirmed(self, mock_get):
        mock_get.side_effect = [success({'block_count': 100}), success({'outputs': [utxo(1, block=None)]})]
        result = ChainSoAPI().get_utxos('addr', confirmations=0)
        assert result['utxos'][0]['confirmations'] == 0

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_request_error(self, mock_get):
        mock_get.side_effect = ValueError('fail')
        assert 'error' in ChainSoAPI().get_utxos('addr')

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_page_error(self, mock_get):
        mock_get.side_effect = [success({'block_count': 100}), make_mock_response(json_data={'foo': 'bar'})]
        assert 'error' in ChainSoAPI().get_utxos('addr')

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_missing_keys(self, mock_get):
        mock_get.side_effect = [success({'block_count': 100}), success({'outputs': [{'hash': 'tx1'}]})]
        assert len(ChainSoAPI().get_utxos('addr')['utxos']) == 0


class TestGetPrimeInputAddress:
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_success(self, mock_get):
        data = dict(TRANSACTION, inputs=[dict(TRANSACTION['inputs'][0], address='b_addr'), dict(TRANSACTION['inputs'][0], address='a_addr')])
        mock_get.return_value = success(data)
        assert ChainSoAPI().get_prime_input_address('tx1')['prime_input_address'] == 'a_addr'

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_no_transaction(self, mock_get):
        mock_get.side_effect = ValueError('fail')
        assert 'error' in ChainSoAPI().get_prime_input_address('tx1')

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_no_input_addresses(self, mock_get):
        mock_get.return_value = success(dict(TRANSACTION, inputs=[]))
        assert 'error' in ChainSoAPI().get_prime_input_address('tx1')


class TestPushTx:
    @mock.patch('data.blockexplorers.chain_so.requests.post')
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_no_broadcast(self, mock_get, mock_post):
        result = ChainSoAPI().push_tx('0100')
        assert 'error' in result
        mock_get.assert_not_called()
        mock_post.assert_not_called()


class TestTimeoutHandling:
    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_timeout_exception_is_caught(self, mock_get):
        mock_get.side_effect = requests.exceptions.ReadTimeout('timed out')
        api = ChainSoAPI()
        result = api.get_latest_block()
        assert 'error' in result

    @mock.patch('data.blockexplorers.chain_so.requests.get')
    def test_timeout_kwarg_is_passed(self, mock_get):
        mock_get.side_effect = [success({'block_count': 100}), success(BLOCK)]
        api = ChainSoAPI()
        api.get_latest_block()
        assert mock_get.call_args.kwargs.get('timeout') == DEFAULT_TIMEOUT
