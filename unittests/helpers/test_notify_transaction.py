#!/usr/bin/env python
import runpy
import sys
import unittest
from unittest.mock import MagicMock, patch

import helpers.notify_transaction as nt_module


class TestNotifyTransaction(unittest.TestCase):
    """Test cases for helpers/notify_transaction.py

    The script posts a JSON notification to a webhook URL via requests.
    """

    @patch('requests.post')
    def test_notify_transaction_script(self, mock_post):
        """Test executing notify_transaction.py as a module to cover the __main__ block"""
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        original_argv = sys.argv
        sys.argv = ['notify_transaction', 'http://example.com/notify', 'pr123', 'tx456']

        try:
            runpy.run_path(nt_module.__file__, run_name='__main__')
        except SystemExit:
            pass
        finally:
            sys.argv = original_argv

        mock_post.assert_called_once_with(
            'http://example.com/notify',
            json={'payment_request_id': 'pr123', 'txid': 'tx456'},
            timeout=10,
        )
        mock_response.raise_for_status.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
