#!/usr/bin/env python
from unittest import mock

import pytest

from helpers.feehelpers import (
    MIN_SAT_PER_BYTE,
    _per_byte,
    get_high_priority_fee,
    get_low_priority_fee,
    get_medium_priority_fee,
    get_recommended_fee,
    get_recommended_fee_blockcypher,
)


class TestFeeHelpers:
    """Tests for fee helper functions"""

    @mock.patch('helpers.feehelpers.get_recommended_fee_blockcypher')
    def test_get_medium_priority_fee(self, mock_get_fee):
        """Test getting medium priority fee"""
        mock_get_fee.return_value = {'medium_priority': 10240, 'low_priority': 5120, 'high_priority': 20480}
        result = get_medium_priority_fee()
        assert result == 10  # 10240 / 1024

    @mock.patch('helpers.feehelpers.get_recommended_fee_blockcypher')
    def test_get_low_priority_fee(self, mock_get_fee):
        """Test getting low priority fee"""
        mock_get_fee.return_value = {'medium_priority': 10240, 'low_priority': 5120, 'high_priority': 20480}
        result = get_low_priority_fee()
        assert result == 5  # 5120 / 1024

    @mock.patch('helpers.feehelpers.get_recommended_fee_blockcypher')
    def test_get_high_priority_fee(self, mock_get_fee):
        """Test getting high priority fee"""
        mock_get_fee.return_value = {'medium_priority': 10240, 'low_priority': 5120, 'high_priority': 20480}
        result = get_high_priority_fee()
        assert result == 20  # 20480 / 1024

    @mock.patch('helpers.feehelpers.get_recommended_fee_blockcypher')
    def test_get_medium_priority_fee_sub_1024(self, mock_get_fee):
        """Test medium priority fee below 1024 sat/kB is clamped to MIN_SAT_PER_BYTE"""
        mock_get_fee.return_value = {'medium_priority': 500, 'low_priority': 5120, 'high_priority': 20480}
        result = get_medium_priority_fee()
        assert result == 1  # ceil(500/1024) = 1, clamped to MIN_SAT_PER_BYTE

    @mock.patch('helpers.feehelpers.get_recommended_fee_blockcypher')
    def test_get_low_priority_fee_sub_1024(self, mock_get_fee):
        """Test low priority fee below 1024 sat/kB is clamped to MIN_SAT_PER_BYTE"""
        mock_get_fee.return_value = {'medium_priority': 10240, 'low_priority': 500, 'high_priority': 20480}
        result = get_low_priority_fee()
        assert result == 1

    @mock.patch('helpers.feehelpers.get_recommended_fee_blockcypher')
    def test_get_high_priority_fee_sub_1024(self, mock_get_fee):
        """Test high priority fee below 1024 sat/kB is clamped to MIN_SAT_PER_BYTE"""
        mock_get_fee.return_value = {'medium_priority': 10240, 'low_priority': 5120, 'high_priority': 500}
        result = get_high_priority_fee()
        assert result == 1

    @mock.patch('helpers.feehelpers.get_recommended_fee_blockcypher')
    def test_get_medium_priority_fee_not_exact_multiple(self, mock_get_fee):
        """Test medium priority fee not an exact multiple of 1024 is ceiled"""
        mock_get_fee.return_value = {'medium_priority': 1025, 'low_priority': 5120, 'high_priority': 20480}
        result = get_medium_priority_fee()
        assert result == 2  # ceil(1025/1024) = 2

    @mock.patch('helpers.feehelpers.get_recommended_fee_blockcypher')
    def test_get_medium_priority_fee_zero(self, mock_get_fee):
        """Test medium priority fee of zero still returns MIN_SAT_PER_BYTE"""
        mock_get_fee.return_value = {'medium_priority': 0, 'low_priority': 5120, 'high_priority': 20480}
        result = get_medium_priority_fee()
        assert result == MIN_SAT_PER_BYTE

    @mock.patch('helpers.feehelpers.get_recommended_fee_blockcypher')
    def test_get_medium_priority_fee_exactly_1024(self, mock_get_fee):
        """Test medium priority fee exactly 1024 returns 1"""
        mock_get_fee.return_value = {'medium_priority': 1024, 'low_priority': 5120, 'high_priority': 20480}
        result = get_medium_priority_fee()
        assert result == 1

    def test_per_byte_exact_multiple(self):
        """Test _per_byte with an exact multiple of 1024"""
        assert _per_byte(10240) == 10

    def test_per_byte_not_exact_multiple(self):
        """Test _per_byte with a value that is not an exact multiple of 1024"""
        assert _per_byte(1025) == 2

    def test_per_byte_sub_1024(self):
        """Test _per_byte with a sub-1024 value clamps to MIN_SAT_PER_BYTE"""
        assert _per_byte(500) == 1

    def test_per_byte_zero(self):
        """Test _per_byte with zero clamps to MIN_SAT_PER_BYTE"""
        assert _per_byte(0) == MIN_SAT_PER_BYTE

    def test_per_byte_exactly_1024(self):
        """Test _per_byte with exactly 1024"""
        assert _per_byte(1024) == 1

    def test_per_byte_string(self):
        """Test _per_byte with a string input to cover the int() conversion path"""
        assert _per_byte('500') == 1

    def test_per_byte_string_exact_multiple(self):
        """Test _per_byte with a string input that is an exact multiple"""
        assert _per_byte('10240') == 10

    @mock.patch('helpers.feehelpers.requests.get')
    def test_get_recommended_fee(self, mock_get):
        """Test getting recommended fee from bitcoinfees.earn.com"""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            'fastestFee': 20,
            'halfHourFee': 10,
            'hourFee': 5
        }
        mock_get.return_value = mock_response
        
        result = get_recommended_fee()
        assert result['high_priority'] == 20 * 1024
        assert result['medium_priority'] == 10 * 1024
        assert result['low_priority'] == 5 * 1024

    @mock.patch('helpers.feehelpers.requests.get')
    def test_get_recommended_fee_error(self, mock_get):
        """Test error handling when API fails"""
        mock_get.side_effect = ValueError('Network error')
        
        with pytest.raises(Exception) as excinfo:
            get_recommended_fee()
        assert 'Unable get recommended fee' in str(excinfo.value)

    @mock.patch('helpers.feehelpers.get_use_testnet', return_value=False)
    @mock.patch('helpers.feehelpers.requests.get')
    def test_get_recommended_fee_blockcypher_mainnet(self, mock_get, mock_testnet):
        """Test getting recommended fee from blockcypher (mainnet)"""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            'high_fee_per_kb': 20000,
            'medium_fee_per_kb': 10000,
            'low_fee_per_kb': 5000
        }
        mock_get.return_value = mock_response
        
        result = get_recommended_fee_blockcypher()
        assert result['high_priority'] == 20000
        assert result['medium_priority'] == 10000
        assert result['low_priority'] == 5000
        mock_get.assert_called_with(url='https://api.blockcypher.com/v1/btc/main')

    @mock.patch('helpers.feehelpers.get_use_testnet', return_value=True)
    @mock.patch('helpers.feehelpers.requests.get')
    def test_get_recommended_fee_blockcypher_testnet(self, mock_get, mock_testnet):
        """Test getting recommended fee from blockcypher (testnet)"""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            'high_fee_per_kb': 20000,
            'medium_fee_per_kb': 10000,
            'low_fee_per_kb': 5000
        }
        mock_get.return_value = mock_response
        
        get_recommended_fee_blockcypher()
        mock_get.assert_called_with(url='https://api.blockcypher.com/v1/btc/test3')

    @mock.patch('helpers.feehelpers.get_use_testnet', return_value=False)
    @mock.patch('helpers.feehelpers.requests.get')
    def test_get_recommended_fee_blockcypher_error(self, mock_get, mock_testnet):
        """Test error handling when blockcypher API fails"""
        mock_get.side_effect = ValueError('Network error')
        
        with pytest.raises(Exception) as excinfo:
            get_recommended_fee_blockcypher()
        assert 'Unable get recommended fee from blockcypher' in str(excinfo.value)
