#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from unittest.mock import patch

from linker.linker import get_lal, get_lbl, get_lrl, get_lsl


VALID_ADDRESS = '1Bobk6PuJst6ot6ay2DcVugv8nxfJh5y'
VALID_ADDRESS_2 = '1Alice3WtXqygdLq7BdvygPcQ9U2NQ9xX'
VALID_ADDRESS_3 = '1Charlie9XqygdLq7BdvygPcQ9U2NQ9xX'
VALID_XPUB = 'xpub661MyMwAqRbcFkPHucMnrGNzDz6UfZEJzLk7yZJ4Z8vJLqY8c5W6jL9PbNL6EnZcKcZ9XK2qL3M5N7pQ8r4T2uV1wS3i5j7k'
VALID_DERIVED_ADDRESS_1 = '1Derived1AbcdefghijKlmnopQrsTuvwxYz123'
VALID_DERIVED_ADDRESS_2 = '1Derived2AbcdefghijKlmnopQrsTuvwxYz123'


class TestGetLal:
    @patch('linker.linker.get_sil')
    @patch('linker.linker.get_addresses_from_xpub')
    def test_valid_lal(self, mock_xpub, mock_sil):
        mock_sil.return_value = {'SIL': [
            [VALID_ADDRESS_2, 1000, 0.6, 500],
            [VALID_ADDRESS_3, 500, 0.4, 510],
        ]}
        mock_xpub.return_value = [VALID_DERIVED_ADDRESS_1, VALID_DERIVED_ADDRESS_2]
        result = get_lal(VALID_ADDRESS, VALID_XPUB)
        assert 'LAL' in result
        assert len(result['LAL']) == 2
        assert result['LAL'][0] == [VALID_ADDRESS_2, VALID_DERIVED_ADDRESS_1]
        assert result['LAL'][1] == [VALID_ADDRESS_3, VALID_DERIVED_ADDRESS_2]

    @patch('linker.linker.get_sil')
    def test_sil_error(self, mock_sil):
        mock_sil.return_value = {'error': 'failed'}
        result = get_lal(VALID_ADDRESS, VALID_XPUB)
        assert 'error' in result

    def test_invalid_address(self):
        result = get_lal('invalid', VALID_XPUB)
        assert 'error' in result

    def test_invalid_xpub(self):
        result = get_lal(VALID_ADDRESS, 'invalid')
        assert 'error' in result


class TestGetLbl:
    @patch('linker.linker.balance')
    @patch('linker.linker.get_sil')
    @patch('linker.linker.get_addresses_from_xpub')
    def test_valid_lbl(self, mock_xpub, mock_sil, mock_balance):
        mock_sil.return_value = {'SIL': [
            [VALID_ADDRESS_2, 1000, 0.6, 500],
            [VALID_ADDRESS_3, 500, 0.4, 510],
        ]}
        mock_xpub.return_value = [VALID_DERIVED_ADDRESS_1, VALID_DERIVED_ADDRESS_2]
        mock_balance.side_effect = [
            {'balance': {'final': 500}},
            {'balance': {'final': 300}},
        ]
        result = get_lbl(VALID_ADDRESS, VALID_XPUB)
        assert 'LBL' in result
        assert len(result['LBL']) == 2
        assert result['LBL'][0][1] == 500
        assert result['LBL'][1][1] == 300
        assert result['LBL'][0][2] == 500 / 800
        assert result['LBL'][1][2] == 300 / 800

    @patch('linker.linker.balance')
    @patch('linker.linker.get_sil')
    @patch('linker.linker.get_addresses_from_xpub')
    def test_lbl_balance_error(self, mock_xpub, mock_sil, mock_balance):
        mock_sil.return_value = {'SIL': [
            [VALID_ADDRESS_2, 1000, 0.6, 500],
        ]}
        mock_xpub.return_value = [VALID_DERIVED_ADDRESS_1]
        mock_balance.return_value = {'error': 'failed'}
        result = get_lbl(VALID_ADDRESS, VALID_XPUB)
        assert 'error' in result

    @patch('linker.linker.get_sil')
    def test_lbl_sil_error(self, mock_sil):
        mock_sil.return_value = {'error': 'failed'}
        result = get_lbl(VALID_ADDRESS, VALID_XPUB)
        assert 'error' in result


class TestGetLrl:
    @patch('linker.linker.balance')
    @patch('linker.linker.get_sil')
    @patch('linker.linker.get_addresses_from_xpub')
    def test_valid_lrl(self, mock_xpub, mock_sil, mock_balance):
        mock_sil.return_value = {'SIL': [
            [VALID_ADDRESS_2, 1000, 0.6, 500],
            [VALID_ADDRESS_3, 500, 0.4, 510],
        ]}
        mock_xpub.return_value = [VALID_DERIVED_ADDRESS_1, VALID_DERIVED_ADDRESS_2]
        mock_balance.side_effect = [
            {'balance': {'received': 2000}},
            {'balance': {'received': 1000}},
        ]
        result = get_lrl(VALID_ADDRESS, VALID_XPUB)
        assert 'LRL' in result
        assert len(result['LRL']) == 2
        assert result['LRL'][0][1] == 2000
        assert result['LRL'][1][1] == 1000
        assert result['LRL'][0][2] == 2000 / 3000

    @patch('linker.linker.balance')
    @patch('linker.linker.get_sil')
    @patch('linker.linker.get_addresses_from_xpub')
    def test_lrl_balance_error(self, mock_xpub, mock_sil, mock_balance):
        mock_sil.return_value = {'SIL': [
            [VALID_ADDRESS_2, 1000, 0.6, 500],
        ]}
        mock_xpub.return_value = [VALID_DERIVED_ADDRESS_1]
        mock_balance.return_value = {'error': 'failed'}
        result = get_lrl(VALID_ADDRESS, VALID_XPUB)
        assert 'error' in result

    @patch('linker.linker.get_sil')
    def test_lrl_sil_error(self, mock_sil):
        mock_sil.return_value = {'error': 'failed'}
        result = get_lrl(VALID_ADDRESS, VALID_XPUB)
        assert 'error' in result


class TestGetLsl:
    @patch('linker.linker.balance')
    @patch('linker.linker.get_sil')
    @patch('linker.linker.get_addresses_from_xpub')
    def test_valid_lsl(self, mock_xpub, mock_sil, mock_balance):
        mock_sil.return_value = {'SIL': [
            [VALID_ADDRESS_2, 1000, 0.6, 500],
            [VALID_ADDRESS_3, 500, 0.4, 510],
        ]}
        mock_xpub.return_value = [VALID_DERIVED_ADDRESS_1, VALID_DERIVED_ADDRESS_2]
        mock_balance.side_effect = [
            {'balance': {'sent': 800}},
            {'balance': {'sent': 400}},
        ]
        result = get_lsl(VALID_ADDRESS, VALID_XPUB)
        assert 'LSL' in result
        assert len(result['LSL']) == 2
        assert result['LSL'][0][1] == 800
        assert result['LSL'][1][1] == 400
        assert result['LSL'][0][2] == 800 / 1200

    @patch('linker.linker.balance')
    @patch('linker.linker.get_sil')
    @patch('linker.linker.get_addresses_from_xpub')
    def test_lsl_balance_error(self, mock_xpub, mock_sil, mock_balance):
        mock_sil.return_value = {'SIL': [
            [VALID_ADDRESS_2, 1000, 0.6, 500],
        ]}
        mock_xpub.return_value = [VALID_DERIVED_ADDRESS_1]
        mock_balance.return_value = {'error': 'failed'}
        result = get_lsl(VALID_ADDRESS, VALID_XPUB)
        assert 'error' in result

    @patch('linker.linker.get_sil')
    def test_lsl_sil_error(self, mock_sil):
        mock_sil.return_value = {'error': 'failed'}
        result = get_lsl(VALID_ADDRESS, VALID_XPUB)
        assert 'error' in result
