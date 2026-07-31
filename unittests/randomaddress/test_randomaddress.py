#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from unittest.mock import patch

from randomaddress.randomaddress import (
    random_number_from_blockhash,
    random_address_from_sil,
    random_address_from_sul,
    random_address_from_lbl,
    random_address_from_lrl,
    random_address_from_lsl,
    RandomAddress,
)


VALID_ADDRESS = '1Bobk6PuJst6ot6ay2DcVugv8nxfJh5y'
VALID_ADDRESS_2 = '1Alice3WtXqygdLq7BdvygPcQ9U2NQ9xX'
VALID_ADDRESS_3 = '1Charlie9XqygdLq7BdvygPcQ9U2NQ9xX'
VALID_XPUB = 'xpub661MyMwAqRbcFkPHucMnrGNzDz6UfZEJzLk7yZJ4Z8vJLqY8c5W6jL9PbNL6EnZcKcZ9XK2qL3M5N7pQ8r4T2uV1wS3i5j7k'

BLOCK_HASH = '0000000000000000000aef1a3b2c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c'


class TestRandomNumberFromBlockhash:
    @patch('randomaddress.randomaddress.latest_block')
    def test_latest_block(self, mock_latest):
        mock_latest.return_value = {'block': {'hash': BLOCK_HASH}}
        result = random_number_from_blockhash(0)
        assert isinstance(result, float)
        assert 0 <= result <= 1

    @patch('randomaddress.randomaddress.block_by_height')
    def test_specific_block_height(self, mock_block):
        mock_block.return_value = {'block': {'hash': BLOCK_HASH}}
        result = random_number_from_blockhash(500)
        assert isinstance(result, float)
        assert 0 <= result <= 1

    @patch('randomaddress.randomaddress.latest_block')
    def test_no_block_data(self, mock_latest):
        mock_latest.return_value = {'error': 'failed'}
        result = random_number_from_blockhash(0)
        assert result is None

    @patch('randomaddress.randomaddress.latest_block')
    def test_no_hash_in_block(self, mock_latest):
        mock_latest.return_value = {'block': {}}
        result = random_number_from_blockhash(0)
        assert result is None


class TestRandomAddressFromSil:
    @patch('randomaddress.randomaddress.random_number_from_blockhash')
    @patch('randomaddress.randomaddress.get_sil')
    def test_valid_address(self, mock_sil, mock_rng):
        mock_sil.return_value = {'SIL': [[VALID_ADDRESS_2, 1000, 0.6, 500]]}
        mock_rng.return_value = 0.5
        result = random_address_from_sil(VALID_ADDRESS)
        assert 'distribution_source' in result
        assert result['distribution_source'] == 'SIL'
        assert 'chosen_address' in result

    def test_invalid_address(self):
        result = random_address_from_sil('invalid')
        assert 'error' in result


class TestRandomAddressFromSul:
    @patch('randomaddress.randomaddress.random_number_from_blockhash')
    @patch('randomaddress.randomaddress.get_sul')
    def test_valid_address(self, mock_sul, mock_rng):
        mock_sul.return_value = {'SUL': [[VALID_ADDRESS_2, 1000, 1.0]]}
        mock_rng.return_value = 0.5
        result = random_address_from_sul(VALID_ADDRESS)
        assert result['distribution_source'] == 'SUL'

    def test_invalid_address(self):
        result = random_address_from_sul('invalid')
        assert 'error' in result


class TestRandomAddressFromLbl:
    @patch('randomaddress.randomaddress.random_number_from_blockhash')
    @patch('randomaddress.randomaddress.get_lbl')
    def test_valid(self, mock_lbl, mock_rng):
        mock_lbl.return_value = {'LBL': [[VALID_ADDRESS_2, 1000, 0.6]]}
        mock_rng.return_value = 0.5
        result = random_address_from_lbl(VALID_ADDRESS, VALID_XPUB)
        assert result['distribution_source'] == 'LBL'

    def test_invalid_address(self):
        result = random_address_from_lbl('invalid', VALID_XPUB)
        assert 'error' in result

    def test_invalid_xpub(self):
        result = random_address_from_lbl(VALID_ADDRESS, 'invalid')
        assert 'error' in result


class TestRandomAddressFromLrl:
    @patch('randomaddress.randomaddress.random_number_from_blockhash')
    @patch('randomaddress.randomaddress.get_lrl')
    def test_valid(self, mock_lrl, mock_rng):
        mock_lrl.return_value = {'LRL': [[VALID_ADDRESS_2, 2000, 0.6]]}
        mock_rng.return_value = 0.5
        result = random_address_from_lrl(VALID_ADDRESS, VALID_XPUB)
        assert result['distribution_source'] == 'LRL'

    def test_invalid_address(self):
        result = random_address_from_lrl('invalid', VALID_XPUB)
        assert 'error' in result

    def test_invalid_xpub(self):
        result = random_address_from_lrl(VALID_ADDRESS, 'invalid')
        assert 'error' in result


class TestRandomAddressFromLsl:
    @patch('randomaddress.randomaddress.random_number_from_blockhash')
    @patch('randomaddress.randomaddress.get_lsl')
    def test_valid(self, mock_lsl, mock_rng):
        mock_lsl.return_value = {'LSL': [[VALID_ADDRESS_2, 800, 0.6]]}
        mock_rng.return_value = 0.5
        result = random_address_from_lsl(VALID_ADDRESS, VALID_XPUB)
        assert result['distribution_source'] == 'LSL'

    def test_invalid_address(self):
        result = random_address_from_lsl('invalid', VALID_XPUB)
        assert 'error' in result

    def test_invalid_xpub(self):
        result = random_address_from_lsl(VALID_ADDRESS, 'invalid')
        assert 'error' in result


class TestRandomAddressGetDistribution:
    @patch('randomaddress.randomaddress.get_sil')
    def test_sil_source(self, mock_sil):
        mock_sil.return_value = {'SIL': [[VALID_ADDRESS_2, 1000, 0.6, 500]]}
        ra = RandomAddress(address=VALID_ADDRESS)
        dist = ra.get_distribution('SIL')
        assert dist == [(VALID_ADDRESS_2, 1000)]

    @patch('randomaddress.randomaddress.get_sul')
    def test_sul_source(self, mock_sul):
        mock_sul.return_value = {'SUL': [[VALID_ADDRESS_2, 1000, 1.0]]}
        ra = RandomAddress(address=VALID_ADDRESS)
        dist = ra.get_distribution('SUL')
        assert dist == [(VALID_ADDRESS_2, 1000)]

    @patch('randomaddress.randomaddress.get_lbl')
    def test_lbl_source(self, mock_lbl):
        mock_lbl.return_value = {'LBL': [[VALID_ADDRESS_2, 500, 1.0]]}
        ra = RandomAddress(address=VALID_ADDRESS, xpub=VALID_XPUB)
        dist = ra.get_distribution('LBL')
        assert dist == [(VALID_ADDRESS_2, 500)]

    @patch('randomaddress.randomaddress.get_lrl')
    def test_lrl_source(self, mock_lrl):
        mock_lrl.return_value = {'LRL': [[VALID_ADDRESS_2, 2000, 1.0]]}
        ra = RandomAddress(address=VALID_ADDRESS, xpub=VALID_XPUB)
        dist = ra.get_distribution('LRL')
        assert dist == [(VALID_ADDRESS_2, 2000)]

    @patch('randomaddress.randomaddress.get_lsl')
    def test_lsl_source(self, mock_lsl):
        mock_lsl.return_value = {'LSL': [[VALID_ADDRESS_2, 800, 1.0]]}
        ra = RandomAddress(address=VALID_ADDRESS, xpub=VALID_XPUB)
        dist = ra.get_distribution('LSL')
        assert dist == [(VALID_ADDRESS_2, 800)]

    def test_unknown_source(self):
        ra = RandomAddress(address=VALID_ADDRESS)
        with pytest.raises(NotImplementedError):
            ra.get_distribution('UNKNOWN')


class TestRandomAddressResults:
    def test_results_with_distribution(self):
        ra = RandomAddress(address=VALID_ADDRESS)
        distribution = [(VALID_ADDRESS_2, 1000), (VALID_ADDRESS_3, 500)]
        result = ra.results(distribution, 0.5)
        assert 'chosen_address' in result
        assert 'chosen_index' in result
        assert 'target' in result
        assert result['target'] == 1500 * 0.5

    def test_results_empty_distribution(self):
        ra = RandomAddress(address=VALID_ADDRESS)
        result = ra.results([], 0.5)
        assert result == {}


class TestGetChosenIndex:
    def test_single_value(self):
        idx = RandomAddress.get_chosen_index([1000], 0.5)
        assert idx == 0

    def test_multiple_values_first(self):
        idx = RandomAddress.get_chosen_index([1000, 500], 0.1)
        assert idx == 0

    def test_multiple_values_second(self):
        idx = RandomAddress.get_chosen_index([1000, 500], 0.9)
        assert idx == 1

    def test_zero_total(self):
        idx = RandomAddress.get_chosen_index([0, 0], 0.5)
        assert idx is None


class TestRandomAddressGet:
    @patch('randomaddress.randomaddress.random_number_from_blockhash')
    @patch('randomaddress.randomaddress.get_sil')
    def test_full_get(self, mock_sil, mock_rng):
        mock_sil.return_value = {'SIL': [[VALID_ADDRESS_2, 1000, 0.6, 500]]}
        mock_rng.return_value = 0.5
        ra = RandomAddress(address=VALID_ADDRESS)
        result = ra.get(source='SIL', rng_block_height=0)
        assert result['distribution_source'] == 'SIL'
        assert result['random_number'] == 0.5
        assert 'chosen_address' in result
