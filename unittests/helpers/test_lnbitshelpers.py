#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock

from helpers.lnbitshelpers import (
    get_wallet_details, create_invoice, decode_invoice, check_invoice, LNBITS_URL
)


class TestLnbitsHelpers(unittest.TestCase):
    """Test cases for helpers/lnbitshelpers.py"""

    def test_lnbits_url_constant(self):
        """Test LNBITS_URL constant"""
        self.assertEqual(LNBITS_URL, 'https://legend.lnbits.com')

    @patch('helpers.lnbitshelpers.requests.get')
    def test_get_wallet_details_success(self, mock_get):
        """Test successful wallet details retrieval"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 'wallet123', 'name': 'Test Wallet', 'balance': 1000}
        mock_get.return_value = mock_response

        result = get_wallet_details('test-api-key')

        self.assertEqual(result, {'id': 'wallet123', 'name': 'Test Wallet', 'balance': 1000})
        mock_get.assert_called_once_with(
            f'{LNBITS_URL}/api/v1/wallet',
            headers={'X-Api-Key': 'test-api-key'}
        )

    @patch('helpers.lnbitshelpers.requests.get')
    def test_get_wallet_details_failure(self, mock_get):
        """Test failed wallet details retrieval"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_get.return_value = mock_response

        result = get_wallet_details('invalid-key')
        self.assertIsNone(result)

    @patch('helpers.lnbitshelpers.requests.post')
    def test_create_invoice_success(self, mock_post):
        """Test successful invoice creation"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'payment_hash': 'hash123',
            'payment_request': 'lnbc...',
            'checking_id': 'check123'
        }
        mock_post.return_value = mock_response

        result = create_invoice('test-api-key', amount=100000, memo='Test payment', expiry=3600)

        self.assertEqual(result['payment_hash'], 'hash123')
        mock_post.assert_called_once()

    @patch('helpers.lnbitshelpers.requests.post')
    def test_create_invoice_failure(self, mock_post):
        """Test failed invoice creation"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = 'Bad request'
        mock_post.return_value = mock_response

        result = create_invoice('test-api-key', amount=100000, memo='Test', expiry=3600)
        self.assertIsNone(result)

    @patch('helpers.lnbitshelpers.requests.post')
    def test_decode_invoice_success(self, mock_post):
        """Test successful invoice decoding"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'amount': 100000, 'description': 'Test'}
        mock_post.return_value = mock_response

        result = decode_invoice('test-api-key', 'lnbc...')

        self.assertEqual(result, {'amount': 100000, 'description': 'Test'})

    @patch('helpers.lnbitshelpers.requests.post')
    def test_decode_invoice_failure(self, mock_post):
        """Test failed invoice decoding"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = 'Invalid invoice'
        mock_post.return_value = mock_response

        result = decode_invoice('test-api-key', 'invalid')
        self.assertIsNone(result)

    @patch('helpers.lnbitshelpers.requests.get')
    def test_check_invoice_success(self, mock_get):
        """Test successful invoice check"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'paid': True, 'preimage': 'preimage123'}
        mock_get.return_value = mock_response

        result = check_invoice('test-api-key', 'payment_hash_123')

        self.assertEqual(result, {'paid': True, 'preimage': 'preimage123'})

    @patch('helpers.lnbitshelpers.requests.get')
    def test_check_invoice_failure(self, mock_get):
        """Test failed invoice check"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = 'Not found'
        mock_get.return_value = mock_response

        result = check_invoice('test-api-key', 'nonexistent')
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
