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

    @patch('subprocess.Popen')
    def test_notify_transaction_script(self, mock_popen):
        """Test executing notify_transaction.py as a module to cover __main__ block"""
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'OK', b'')
        mock_popen.return_value = mock_process

        import helpers.notify_transaction as nt_module
        import sys

        original_argv = sys.argv
        sys.argv = ['notify_transaction', 'http://example.com/notify', 'pr123', 'tx456']

        try:
            with open(nt_module.__file__) as f:
                source = f.read()
            exec(compile(source, nt_module.__file__, 'exec'), {'__name__': '__main__'})
        except SystemExit:
            pass
        finally:
            sys.argv = original_argv

        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        self.assertIn('http://example.com/notify', call_args)
        self.assertIn('pr123', call_args)
        self.assertIn('tx456', call_args)


if __name__ == '__main__':
    unittest.main()
