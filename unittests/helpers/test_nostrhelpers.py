#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock
import sys

# Mock pynostr modules before importing
mock_private_key = MagicMock()
mock_public_key = MagicMock()
mock_event = MagicMock()
mock_relay_manager = MagicMock()
mock_filters = MagicMock()

sys.modules['pynostr'] = MagicMock()
sys.modules['pynostr.event'] = MagicMock(Event=mock_event)
sys.modules['pynostr.relay_manager'] = MagicMock(RelayManager=mock_relay_manager)
sys.modules['pynostr.filters'] = MagicMock(FiltersList=MagicMock(), Filters=MagicMock())
sys.modules['pynostr.key'] = MagicMock(PrivateKey=mock_private_key, PublicKey=mock_public_key)


class TestNostrHelpers(unittest.TestCase):
    """Test cases for helpers/nostrhelpers.py"""

    @patch('helpers.nostrhelpers.get_nostr_nsec', return_value='nsec1test123456789')
    def test_get_nostr_private_key(self, mock_get_nsec):
        """Test get_nostr_private_key returns PrivateKey"""
        from helpers.nostrhelpers import get_nostr_private_key, PrivateKey
        
        mock_pk = MagicMock()
        PrivateKey.from_nsec.return_value = mock_pk
        
        result = get_nostr_private_key()
        
        PrivateKey.from_nsec.assert_called_with('nsec1test123456789')

    @patch('helpers.nostrhelpers.get_nostr_nsec', return_value='nsec1test123456789')
    def test_get_nostr_public_key(self, mock_get_nsec):
        """Test get_nostr_public_key returns public key from private key"""
        from helpers.nostrhelpers import get_nostr_public_key, PrivateKey
        
        mock_pk = MagicMock()
        mock_pubkey = MagicMock()
        mock_pk.public_key = mock_pubkey
        PrivateKey.from_nsec.return_value = mock_pk
        
        result = get_nostr_public_key()
        
        self.assertEqual(result, mock_pubkey)

    @patch('helpers.nostrhelpers.time.sleep')
    @patch('helpers.nostrhelpers.get_nostr_nsec', return_value='nsec1test123456789')
    def test_post_note(self, mock_get_nsec, mock_sleep):
        """Test post_note publishes event to relays"""
        from helpers.nostrhelpers import post_note, PrivateKey, RelayManager, Event
        
        mock_pk = MagicMock()
        mock_pk.public_key.hex.return_value = 'pubkey_hex'
        mock_pk.hex.return_value = 'privkey_hex'
        PrivateKey.from_nsec.return_value = mock_pk
        
        mock_rm = MagicMock()
        mock_rm.message_pool.has_ok_notices.return_value = False
        mock_rm.message_pool.has_events.return_value = False
        RelayManager.return_value = mock_rm
        
        mock_evt = MagicMock()
        Event.return_value = mock_evt
        
        post_note("Test note")
        
        Event.assert_called_with("Test note")
        mock_evt.sign.assert_called_with('privkey_hex')
        mock_rm.publish_event.assert_called_with(mock_evt)
        mock_rm.run_sync.assert_called()


if __name__ == '__main__':
    unittest.main()
