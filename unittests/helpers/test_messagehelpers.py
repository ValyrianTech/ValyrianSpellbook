#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock


class TestSignMessage(unittest.TestCase):
    """Test cases for sign_message function"""

    @patch('helpers.messagehelpers.CBitcoinSecret')
    @patch('helpers.messagehelpers.SignMessage')
    @patch('helpers.messagehelpers.BitcoinMessage')
    def test_sign_message(self, mock_bitcoin_msg, mock_sign, mock_secret):
        """Test sign_message function"""
        from helpers.messagehelpers import sign_message
        
        mock_key = MagicMock()
        mock_secret.return_value = mock_key
        mock_sign.return_value = b'signature_bytes'
        
        result = sign_message('test message', 'private_key_wif')
        
        self.assertEqual(result, 'signature_bytes')
        mock_secret.assert_called_once_with('private_key_wif')


class TestVerifyMessage(unittest.TestCase):
    """Test cases for verify_message function"""

    @patch('helpers.messagehelpers.VerifyMessage')
    @patch('helpers.messagehelpers.BitcoinMessage')
    def test_verify_message_valid(self, mock_bitcoin_msg, mock_verify):
        """Test verify_message with valid signature"""
        from helpers.messagehelpers import verify_message
        
        mock_verify.return_value = True
        
        result = verify_message('1Address', 'test message', 'signature')
        
        self.assertTrue(result)

    @patch('helpers.messagehelpers.VerifyMessage')
    @patch('helpers.messagehelpers.BitcoinMessage')
    def test_verify_message_invalid(self, mock_bitcoin_msg, mock_verify):
        """Test verify_message with invalid signature"""
        from helpers.messagehelpers import verify_message
        
        mock_verify.return_value = False
        
        result = verify_message('1Address', 'test message', 'bad_signature')
        
        self.assertFalse(result)

    @patch('helpers.messagehelpers.VerifyMessage')
    @patch('helpers.messagehelpers.BitcoinMessage')
    def test_verify_message_exception(self, mock_bitcoin_msg, mock_verify):
        """Test verify_message when exception occurs"""
        from helpers.messagehelpers import verify_message
        
        mock_verify.side_effect = Exception('Verification error')
        
        result = verify_message('1Address', 'test message', 'signature')
        
        self.assertFalse(result)


class TestSignAndVerify(unittest.TestCase):
    """Test cases for sign_and_verify function"""

    @patch('helpers.messagehelpers.CBitcoinSecret')
    @patch('helpers.messagehelpers.SignMessage')
    @patch('helpers.messagehelpers.VerifyMessage')
    @patch('helpers.messagehelpers.BitcoinMessage')
    def test_sign_and_verify_success(self, mock_bitcoin_msg, mock_verify, mock_sign, mock_secret):
        """Test sign_and_verify function success"""
        from helpers.messagehelpers import sign_and_verify
        
        mock_key = MagicMock()
        mock_secret.return_value = mock_key
        mock_sign.return_value = b'signature'
        mock_verify.return_value = True
        
        result = sign_and_verify('private_key', 'message', '1Address')
        
        self.assertEqual(result, b'signature')

    @patch('helpers.messagehelpers.CBitcoinSecret')
    @patch('helpers.messagehelpers.SignMessage')
    @patch('helpers.messagehelpers.VerifyMessage')
    @patch('helpers.messagehelpers.BitcoinMessage')
    def test_sign_and_verify_failure(self, mock_bitcoin_msg, mock_verify, mock_sign, mock_secret):
        """Test sign_and_verify function when verification fails"""
        from helpers.messagehelpers import sign_and_verify
        
        mock_key = MagicMock()
        mock_secret.return_value = mock_key
        mock_sign.return_value = b'signature'
        mock_verify.return_value = False
        
        with self.assertRaises(AssertionError):
            sign_and_verify('private_key', 'message', '1Address')


class TestSignData(unittest.TestCase):
    """Test cases for sign_data function"""

    @patch('helpers.messagehelpers.get_address_from_wallet')
    @patch('helpers.messagehelpers.get_private_key_from_wallet')
    @patch('helpers.messagehelpers.sign_message')
    @patch('helpers.messagehelpers.verify_message')
    def test_sign_data_success(self, mock_verify, mock_sign, mock_get_priv, mock_get_addr):
        """Test sign_data function success"""
        from helpers.messagehelpers import sign_data
        
        mock_get_addr.return_value = '1TestAddress'
        mock_get_priv.return_value = {'1TestAddress': 'private_key'}
        mock_sign.return_value = 'signature_string'
        mock_verify.return_value = True
        
        data = {'key': 'value', 'number': 123}
        result = sign_data(data, account=0, index=0)
        
        self.assertEqual(result['address'], '1TestAddress')
        self.assertIn('/sha256/', result['message'])
        self.assertEqual(result['signature'], 'signature_string')
        self.assertEqual(result['data'], data)

    @patch('helpers.messagehelpers.get_address_from_wallet')
    @patch('helpers.messagehelpers.get_private_key_from_wallet')
    @patch('helpers.messagehelpers.sign_message')
    @patch('helpers.messagehelpers.verify_message')
    def test_sign_data_verification_failure(self, mock_verify, mock_sign, mock_get_priv, mock_get_addr):
        """Test sign_data function when verification fails"""
        from helpers.messagehelpers import sign_data
        
        mock_get_addr.return_value = '1TestAddress'
        mock_get_priv.return_value = {'1TestAddress': 'private_key'}
        mock_sign.return_value = 'signature_string'
        mock_verify.return_value = False
        
        data = {'key': 'value'}
        
        with self.assertRaises(AssertionError):
            sign_data(data, account=0, index=0)

    @patch('helpers.messagehelpers.get_address_from_wallet')
    @patch('helpers.messagehelpers.get_private_key_from_wallet')
    @patch('helpers.messagehelpers.sign_message')
    @patch('helpers.messagehelpers.verify_message')
    def test_sign_data_different_accounts(self, mock_verify, mock_sign, mock_get_priv, mock_get_addr):
        """Test sign_data with different account and index"""
        from helpers.messagehelpers import sign_data
        
        mock_get_addr.return_value = '1AccountAddress'
        mock_get_priv.return_value = {'1AccountAddress': 'priv_key'}
        mock_sign.return_value = 'sig'
        mock_verify.return_value = True
        
        result = sign_data({'test': 'data'}, account=5, index=10)
        
        mock_get_addr.assert_called_once_with(account=5, index=10)
        mock_get_priv.assert_called_once_with(account=5, index=10)

    @patch('helpers.messagehelpers.get_address_from_wallet')
    @patch('helpers.messagehelpers.get_private_key_from_wallet')
    @patch('helpers.messagehelpers.sign_message')
    @patch('helpers.messagehelpers.verify_message')
    def test_sign_data_hash_consistency(self, mock_verify, mock_sign, mock_get_priv, mock_get_addr):
        """Test that sign_data produces consistent hash for same data"""
        from helpers.messagehelpers import sign_data
        
        mock_get_addr.return_value = '1Address'
        mock_get_priv.return_value = {'1Address': 'key'}
        mock_sign.return_value = 'sig'
        mock_verify.return_value = True
        
        data = {'a': 1, 'b': 2}
        result1 = sign_data(data, account=0, index=0)
        result2 = sign_data(data, account=0, index=0)
        
        # Same data should produce same hash
        self.assertEqual(result1['message'], result2['message'])


if __name__ == '__main__':
    unittest.main()
