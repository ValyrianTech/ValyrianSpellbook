#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock


class TestSpellbookCall(unittest.TestCase):
    """Test cases for spellbook_call function"""

    @patch('helpers.setupscripthelpers.Popen')
    @patch('helpers.setupscripthelpers.get_python_exe', return_value='/usr/bin/python3')
    @patch('helpers.setupscripthelpers.format_args', side_effect=lambda x: ' '.join(x))
    def test_spellbook_call_success(self, mock_format, mock_python, mock_popen):
        """Test successful spellbook_call"""
        from helpers.setupscripthelpers import spellbook_call
        
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'{"result": "success"}', b'')
        mock_popen.return_value = mock_process
        
        result = spellbook_call('get_triggers')
        
        self.assertEqual(result, {"result": "success"})

    @patch('helpers.setupscripthelpers.Popen')
    @patch('helpers.setupscripthelpers.get_python_exe', return_value='/usr/bin/python3')
    @patch('helpers.setupscripthelpers.format_args', side_effect=lambda x: ' '.join(x))
    def test_spellbook_call_with_error(self, mock_format, mock_python, mock_popen):
        """Test spellbook_call with stderr output"""
        from helpers.setupscripthelpers import spellbook_call
        
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'{"result": "success"}', b'Warning: something')
        mock_popen.return_value = mock_process
        
        result = spellbook_call('get_triggers')
        
        self.assertEqual(result, {"result": "success"})

    @patch('helpers.setupscripthelpers.Popen')
    @patch('helpers.setupscripthelpers.get_python_exe', return_value='/usr/bin/python3')
    @patch('helpers.setupscripthelpers.format_args', side_effect=lambda x: ' '.join(x))
    def test_spellbook_call_empty_output(self, mock_format, mock_python, mock_popen):
        """Test spellbook_call with empty output"""
        from helpers.setupscripthelpers import spellbook_call
        
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_popen.return_value = mock_process
        
        result = spellbook_call('get_triggers')
        
        self.assertIsNone(result)


class TestBitcoinwandCall(unittest.TestCase):
    """Test cases for bitcoinwand_call function"""

    @patch('helpers.setupscripthelpers.Popen')
    @patch('helpers.setupscripthelpers.get_python_exe', return_value='/usr/bin/python3')
    @patch('helpers.setupscripthelpers.format_args', side_effect=lambda x: ' '.join(x))
    def test_bitcoinwand_call_success(self, mock_format, mock_python, mock_popen):
        """Test successful bitcoinwand_call"""
        from helpers.setupscripthelpers import bitcoinwand_call
        
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'{"signed": true}', b'')
        mock_popen.return_value = mock_process
        
        result = bitcoinwand_call('1A1zP1...', 'message', 'http://example.com')
        
        self.assertEqual(result, {"signed": True})


class TestCleanUpTriggers(unittest.TestCase):
    """Test cases for clean_up_triggers function"""

    @patch('helpers.setupscripthelpers.spellbook_call')
    def test_clean_up_triggers(self, mock_spellbook):
        """Test clean_up_triggers removes specified triggers"""
        from helpers.setupscripthelpers import clean_up_triggers
        
        mock_spellbook.side_effect = [
            ['trigger1', 'trigger2', 'trigger3'],  # get_triggers
            None,  # delete_trigger trigger1
            None,  # delete_trigger trigger2
        ]
        
        clean_up_triggers(['trigger1', 'trigger2'])
        
        self.assertEqual(mock_spellbook.call_count, 3)


class TestCleanUpActions(unittest.TestCase):
    """Test cases for clean_up_actions function"""

    @patch('helpers.setupscripthelpers.spellbook_call')
    def test_clean_up_actions(self, mock_spellbook):
        """Test clean_up_actions removes specified actions"""
        from helpers.setupscripthelpers import clean_up_actions
        
        mock_spellbook.side_effect = [
            ['action1', 'action2', 'action3'],  # get_actions
            None,  # delete_action action1
            None,  # delete_action action2
        ]
        
        clean_up_actions(['action1', 'action2'])
        
        self.assertEqual(mock_spellbook.call_count, 3)


if __name__ == '__main__':
    unittest.main()
