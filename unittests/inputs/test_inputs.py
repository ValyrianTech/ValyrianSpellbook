#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest.mock import patch

from inputs.inputs import get_sil, txs_2_sil, get_profile, txs_to_profile, get_sul, utxos_to_sul, get_sil_section


VALID_ADDRESS = '1Bobk6PuJst6ot6ay2DcVugv8nxfJh5y'
VALID_ADDRESS_2 = '1Alice3WtXqygdLq7BdvygPcQ9U2NQ9xX'
VALID_ADDRESS_3 = '1Charlie9XqygdLq7BdvygPcQ9U2NQ9xX'


def make_tx(txid, prime_input_address, received_value, block_height, receiving=True, outputs=None):
    tx = {
        'txid': txid,
        'prime_input_address': prime_input_address,
        'receivedValue': received_value,
        'block_height': block_height,
        'receiving': receiving,
        'outputs': outputs or [],
    }
    return tx


class TestTxs2Sil:
    def test_single_tx(self):
        txs = [make_tx('aaa', VALID_ADDRESS_2, 1000, 500)]
        sil = txs_2_sil(txs)
        assert len(sil) == 1
        assert sil[0][0] == VALID_ADDRESS_2
        assert sil[0][1] == 1000
        assert sil[0][2] == 1.0
        assert sil[0][3] == 500

    def test_multiple_tx_same_sender(self):
        txs = [
            make_tx('aaa', VALID_ADDRESS_2, 1000, 500),
            make_tx('bbb', VALID_ADDRESS_2, 500, 510),
        ]
        sil = txs_2_sil(txs)
        assert len(sil) == 1
        assert sil[0][1] == 1500
        assert sil[0][2] == 1.0

    def test_multiple_tx_different_senders(self):
        txs = [
            make_tx('aaa', VALID_ADDRESS_2, 1000, 500),
            make_tx('bbb', VALID_ADDRESS_3, 500, 510),
        ]
        sil = txs_2_sil(txs)
        assert len(sil) == 2
        assert sil[0][1] == 1000
        assert sil[0][2] == 1000 / 1500
        assert sil[1][1] == 500
        assert sil[1][2] == 500 / 1500

    def test_block_height_filter(self):
        txs = [
            make_tx('aaa', VALID_ADDRESS_2, 1000, 500),
            make_tx('bbb', VALID_ADDRESS_3, 500, 600),
        ]
        sil = txs_2_sil(txs, block_height=550)
        assert len(sil) == 1
        assert sil[0][0] == VALID_ADDRESS_2

    def test_skip_non_receiving(self):
        txs = [make_tx('aaa', VALID_ADDRESS_2, 1000, 500, receiving=False)]
        sil = txs_2_sil(txs)
        assert len(sil) == 0

    def test_skip_none_block_height(self):
        txs = [make_tx('aaa', VALID_ADDRESS_2, 1000, None)]
        sil = txs_2_sil(txs)
        assert len(sil) == 0


class TestGetSil:
    @patch('inputs.inputs.data.transactions')
    def test_valid_address(self, mock_txs):
        mock_txs.return_value = {'transactions': [make_tx('aaa', VALID_ADDRESS_2, 1000, 500)]}
        result = get_sil(VALID_ADDRESS)
        assert 'SIL' in result
        assert len(result['SIL']) == 1

    @patch('inputs.inputs.data.transactions')
    def test_no_transactions(self, mock_txs):
        mock_txs.return_value = {'error': 'something went wrong'}
        result = get_sil(VALID_ADDRESS)
        assert 'error' in result

    def test_invalid_address(self):
        result = get_sil('invalid')
        assert 'error' in result


class TestTxsToProfile:
    def test_profile_with_self_message(self):
        outputs = [
            {'address': VALID_ADDRESS, 'value': 1000},
            {'address': VALID_ADDRESS, 'value': 500, 'op_return': '@1:NAME=Robb Stark'},
        ]
        txs = [make_tx('aaa', VALID_ADDRESS_2, 1000, 500, outputs=outputs)]
        profile = txs_to_profile(txs, VALID_ADDRESS)
        assert VALID_ADDRESS_2 in profile
        assert profile[VALID_ADDRESS_2]['last_update'] == 500
        assert 'SELF' in profile[VALID_ADDRESS_2]
        assert profile[VALID_ADDRESS_2]['SELF']['NAME'] == 'Robb Stark'

    def test_profile_with_from_address_message(self):
        outputs = [
            {'address': VALID_ADDRESS_2, 'value': 1000},
            {'address': VALID_ADDRESS, 'value': 500, 'op_return': '0@1:RELATION=Sister'},
        ]
        txs = [make_tx('aaa', VALID_ADDRESS_2, 1000, 500, outputs=outputs)]
        profile = txs_to_profile(txs, VALID_ADDRESS)
        assert VALID_ADDRESS_2 in profile
        assert profile[VALID_ADDRESS_2][VALID_ADDRESS_2]['RELATION'] == 'Sister'

    def test_profile_multiple_messages(self):
        outputs = [
            {'address': VALID_ADDRESS, 'value': 1000},
            {'address': VALID_ADDRESS, 'value': 500, 'op_return': '@1:NAME=Robb Stark|@1:HOUSE=Stark'},
        ]
        txs = [make_tx('aaa', VALID_ADDRESS_2, 1000, 500, outputs=outputs)]
        profile = txs_to_profile(txs, VALID_ADDRESS)
        assert profile[VALID_ADDRESS_2]['SELF']['NAME'] == 'Robb Stark'
        assert profile[VALID_ADDRESS_2]['SELF']['HOUSE'] == 'Stark'

    def test_profile_skip_invalid_op_return(self):
        outputs = [
            {'address': VALID_ADDRESS, 'value': 500, 'op_return': 'x' * 100},
        ]
        txs = [make_tx('aaa', VALID_ADDRESS_2, 1000, 500, outputs=outputs)]
        profile = txs_to_profile(txs, VALID_ADDRESS)
        assert len(profile) == 0

    def test_profile_skip_invalid_blockprofile(self):
        outputs = [
            {'address': VALID_ADDRESS, 'value': 500, 'op_return': 'invalid_message'},
        ]
        txs = [make_tx('aaa', VALID_ADDRESS_2, 1000, 500, outputs=outputs)]
        profile = txs_to_profile(txs, VALID_ADDRESS)
        assert len(profile) == 0

    def test_profile_block_height_filter(self):
        outputs = [
            {'address': VALID_ADDRESS, 'value': 500, 'op_return': '0@1:NAME=Robb Stark'},
        ]
        txs = [make_tx('aaa', VALID_ADDRESS_2, 1000, 600, outputs=outputs)]
        profile = txs_to_profile(txs, VALID_ADDRESS, block_height=550)
        assert len(profile) == 0

    def test_profile_skip_none_block_height(self):
        outputs = [
            {'address': VALID_ADDRESS, 'value': 500, 'op_return': '0@1:NAME=Robb Stark'},
        ]
        txs = [make_tx('aaa', VALID_ADDRESS_2, 1000, None, outputs=outputs)]
        profile = txs_to_profile(txs, VALID_ADDRESS)
        assert len(profile) == 0

    def test_profile_to_address_mismatch(self):
        outputs = [
            {'address': VALID_ADDRESS_3, 'value': 500, 'op_return': '@1:NAME=Robb Stark'},
            {'address': VALID_ADDRESS_3, 'value': 500},
        ]
        txs = [make_tx('aaa', VALID_ADDRESS_2, 1000, 500, outputs=outputs)]
        profile = txs_to_profile(txs, VALID_ADDRESS)
        assert VALID_ADDRESS_2 in profile
        assert 'SELF' not in profile[VALID_ADDRESS_2]
        assert profile[VALID_ADDRESS_2] == {'last_update': 500}


class TestGetProfile:
    @patch('inputs.inputs.data.transactions')
    def test_valid_address(self, mock_txs):
        outputs = [
            {'address': VALID_ADDRESS, 'value': 500},
            {'address': VALID_ADDRESS, 'value': 500, 'op_return': '@1:NAME=Robb Stark'},
        ]
        mock_txs.return_value = {'transactions': [make_tx('aaa', VALID_ADDRESS_2, 1000, 500, outputs=outputs)]}
        result = get_profile(VALID_ADDRESS)
        assert 'profile' in result
        assert VALID_ADDRESS_2 in result['profile']

    @patch('inputs.inputs.data.transactions')
    def test_no_transactions(self, mock_txs):
        mock_txs.return_value = {'error': 'failed'}
        result = get_profile(VALID_ADDRESS)
        assert 'error' in result

    def test_invalid_address(self):
        result = get_profile('invalid')
        assert 'error' in result


class TestUtxosToSul:
    @patch('inputs.inputs.data.prime_input_address')
    def test_single_utxo(self, mock_pia):
        mock_pia.return_value = {'prime_input_address': VALID_ADDRESS_2}
        utxos = [{'output_hash': 'aaa', 'value': 1000}]
        sul = utxos_to_sul(utxos)
        assert len(sul) == 1
        assert sul[0][0] == VALID_ADDRESS_2
        assert sul[0][1] == 1000
        assert sul[0][2] == 1.0

    @patch('inputs.inputs.data.prime_input_address')
    def test_multiple_utxos_same_sender(self, mock_pia):
        mock_pia.return_value = {'prime_input_address': VALID_ADDRESS_2}
        utxos = [
            {'output_hash': 'aaa', 'value': 1000},
            {'output_hash': 'bbb', 'value': 500},
        ]
        sul = utxos_to_sul(utxos)
        assert len(sul) == 1
        assert sul[0][1] == 1500

    @patch('inputs.inputs.data.prime_input_address')
    def test_multiple_utxos_different_senders(self, mock_pia):
        mock_pia.side_effect = [
            {'prime_input_address': VALID_ADDRESS_2},
            {'prime_input_address': VALID_ADDRESS_3},
        ]
        utxos = [
            {'output_hash': 'aaa', 'value': 1000},
            {'output_hash': 'bbb', 'value': 500},
        ]
        sul = utxos_to_sul(utxos)
        assert len(sul) == 2
        assert sul[0][2] == 1000 / 1500
        assert sul[1][2] == 500 / 1500

    @patch('inputs.inputs.data.prime_input_address')
    def test_prime_input_address_error(self, mock_pia):
        mock_pia.return_value = {'error': 'not found'}
        utxos = [{'output_hash': 'aaa', 'value': 1000}]
        result = utxos_to_sul(utxos)
        assert 'error' in result


class TestGetSul:
    @patch('inputs.inputs.data.utxos')
    @patch('inputs.inputs.data.prime_input_address')
    def test_valid_address(self, mock_pia, mock_utxos):
        mock_utxos.return_value = {'utxos': [{'output_hash': 'aaa', 'value': 1000}]}
        mock_pia.return_value = {'prime_input_address': VALID_ADDRESS_2}
        result = get_sul(VALID_ADDRESS)
        assert 'SUL' in result

    @patch('inputs.inputs.data.utxos')
    @patch('inputs.inputs.data.prime_input_address')
    def test_sul_error(self, mock_pia, mock_utxos):
        mock_utxos.return_value = {'utxos': [{'output_hash': 'aaa', 'value': 1000}]}
        mock_pia.return_value = {'error': 'not found'}
        result = get_sul(VALID_ADDRESS)
        assert 'error' in result

    @patch('inputs.inputs.data.utxos')
    def test_no_utxos(self, mock_utxos):
        mock_utxos.return_value = {'error': 'failed'}
        result = get_sul(VALID_ADDRESS)
        assert 'error' in result

    def test_invalid_address(self):
        result = get_sul('invalid')
        assert 'error' in result


class TestGetSilSection:
    def test_invalid_from_block_height(self):
        result = get_sil_section(VALID_ADDRESS, 0, 100)
        assert 'error' in result

    def test_invalid_block_range(self):
        result = get_sil_section(VALID_ADDRESS, 100, 50)
        assert 'error' in result

    @patch('inputs.inputs.get_sil')
    def test_valid_section(self, mock_get_sil):
        before_sil = [[VALID_ADDRESS_2, 1000, 0.5, 500]]
        after_sil = [[VALID_ADDRESS_2, 1500, 0.75, 500], [VALID_ADDRESS_3, 500, 0.25, 510]]

        mock_get_sil.side_effect = [
            {'SIL': before_sil},
            {'SIL': after_sil},
        ]
        result = get_sil_section(VALID_ADDRESS, 501, 510)
        assert 'SIL_section' in result
        assert len(result['SIL_section']) == 2
        assert result['SIL_section'][0][1] == 500  # 1500 - 1000
        assert result['SIL_section'][1][1] == 500  # new entry, full value
