#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock

from helpers.feehelpers import (
    get_medium_priority_fee,
    get_low_priority_fee,
    get_high_priority_fee,
    get_recommended_fee,
    get_recommended_fee_blockcypher,
)


class TestFeeHelpers(object):
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
        mock_get.side_effect = Exception('Network error')
        
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
        
        result = get_recommended_fee_blockcypher()
        mock_get.assert_called_with(url='https://api.blockcypher.com/v1/btc/test3')

    @mock.patch('helpers.feehelpers.get_use_testnet', return_value=False)
    @mock.patch('helpers.feehelpers.requests.get')
    def test_get_recommended_fee_blockcypher_error(self, mock_get, mock_testnet):
        """Test error handling when blockcypher API fails"""
        mock_get.side_effect = Exception('Network error')
        
        with pytest.raises(Exception) as excinfo:
            get_recommended_fee_blockcypher()
        assert 'Unable get recommended fee from blockcypher' in str(excinfo.value)
