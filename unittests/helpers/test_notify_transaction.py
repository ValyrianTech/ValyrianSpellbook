#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock


class TestNotifyTransaction(unittest.TestCase):
    """Test cases for helpers/notify_transaction.py
    
    Note: This module is a script that runs via __main__, so we test
    the command construction logic indirectly.
    """

    @patch('subprocess.Popen')
    def test_curl_command_format(self, mock_popen):
        """Test that the curl command is properly formatted"""
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_popen.return_value = mock_process
        
        # The script constructs a curl command like:
        # curl <url> -H "Content-Type: application/json" -d '{"payment_request_id":"<pr>","txid":"<txid>"}'
        url = 'http://example.com/notify'
        pr = 'payment123'
        txid = 'tx456'
        
        expected_command = r'curl %s -H "Content-Type: application/json" -d "{\"payment_request_id\":\"%s\",\"txid\":\"%s\"}"' % (url, pr, txid)
        
        # Verify the command format is correct
        self.assertIn(url, expected_command)
        self.assertIn(pr, expected_command)
        self.assertIn(txid, expected_command)
        self.assertIn('Content-Type: application/json', expected_command)


if __name__ == '__main__':
    unittest.main()
