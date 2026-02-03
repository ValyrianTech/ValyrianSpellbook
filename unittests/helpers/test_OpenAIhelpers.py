#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock


class TestOpenAIHelpersInitialization(unittest.TestCase):
    """Test cases for OpenAI initialization when enabled"""

    def test_openai_initialization_when_enabled(self):
        """Test that openai is configured when get_enable_openai returns True
        
        This test covers lines 8-9 of OpenAIhelpers.py by reloading the module
        with mocked configuration functions that return True/test values.
        """
        import sys
        import importlib
        import openai
        
        # Save original values
        original_org = getattr(openai, 'organization', None)
        original_key = getattr(openai, 'api_key', None)
        
        # Remove the module from cache to force reimport
        if 'helpers.OpenAIhelpers' in sys.modules:
            del sys.modules['helpers.OpenAIhelpers']
        
        try:
            # Patch at the source - the configurationhelpers module
            with patch('helpers.configurationhelpers.get_enable_openai', return_value=True), \
                 patch('helpers.configurationhelpers.get_openai_organization', return_value='test-org'), \
                 patch('helpers.configurationhelpers.get_openai_api_key', return_value='test-api-key'):
                
                # Import fresh - this will execute lines 7-9
                import helpers.OpenAIhelpers
                
                # Verify the openai module was configured
                self.assertEqual(openai.organization, 'test-org')
                self.assertEqual(openai.api_key, 'test-api-key')
        finally:
            # Restore original values
            openai.organization = original_org
            openai.api_key = original_key


class TestOpenAIHelpers(unittest.TestCase):
    """Test cases for helpers/OpenAIhelpers.py"""

    @patch('helpers.OpenAIhelpers.get_enable_openai', return_value=False)
    def test_get_model_ids_error(self, mock_enable):
        """Test get_model_ids returns empty list on error"""
        from helpers.OpenAIhelpers import get_model_ids
        
        with patch('helpers.OpenAIhelpers.openai.Model.list', side_effect=Exception("API Error")):
            result = get_model_ids()
            self.assertEqual(result, [])

    @patch('helpers.OpenAIhelpers.get_enable_openai', return_value=False)
    def test_get_model_ids_success(self, mock_enable):
        """Test get_model_ids returns list of model ids"""
        from helpers.OpenAIhelpers import get_model_ids
        
        mock_result = {'data': [{'id': 'gpt-4'}, {'id': 'gpt-3.5-turbo'}]}
        with patch('helpers.OpenAIhelpers.openai.Model.list', return_value=mock_result):
            result = get_model_ids()
            self.assertEqual(result, ['gpt-4', 'gpt-3.5-turbo'])

    @patch('helpers.OpenAIhelpers.get_enable_openai', return_value=False)
    def test_openai_complete_error(self, mock_enable):
        """Test openai_complete returns error dict on exception"""
        from helpers.OpenAIhelpers import openai_complete
        
        with patch('helpers.OpenAIhelpers.openai.Completion.create', side_effect=Exception("API Error")):
            result = openai_complete("test prompt")
            self.assertIn('error', result)

    @patch('helpers.OpenAIhelpers.get_enable_openai', return_value=False)
    def test_openai_complete_success(self, mock_enable):
        """Test openai_complete returns response on success"""
        from helpers.OpenAIhelpers import openai_complete
        
        mock_response = {'choices': [{'text': 'completion'}]}
        with patch('helpers.OpenAIhelpers.openai.Completion.create', return_value=mock_response):
            result = openai_complete("test prompt")
            self.assertEqual(result, mock_response)

    @patch('helpers.OpenAIhelpers.get_enable_openai', return_value=False)
    def test_openai_chat_complete_error(self, mock_enable):
        """Test openai_chat_complete returns error dict on exception"""
        from helpers.OpenAIhelpers import openai_chat_complete
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        with patch('helpers.OpenAIhelpers.openai.ChatCompletion.create', side_effect=Exception("API Error")):
            result = openai_chat_complete(messages)
            self.assertIn('error', result)

    @patch('helpers.OpenAIhelpers.get_enable_openai', return_value=False)
    def test_openai_chat_complete_success(self, mock_enable):
        """Test openai_chat_complete returns response on success"""
        from helpers.OpenAIhelpers import openai_chat_complete
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        mock_response = {'choices': [{'message': {'content': 'Hi!'}}]}
        with patch('helpers.OpenAIhelpers.openai.ChatCompletion.create', return_value=mock_response):
            result = openai_chat_complete(messages)
            self.assertEqual(result, mock_response)

    @patch('helpers.OpenAIhelpers.get_enable_openai', return_value=False)
    def test_openai_edit_error(self, mock_enable):
        """Test openai_edit returns error dict on exception"""
        from helpers.OpenAIhelpers import openai_edit
        
        with patch('helpers.OpenAIhelpers.openai.Edit.create', side_effect=Exception("API Error")):
            result = openai_edit("Fix the code", "def foo():")
            self.assertIn('error', result)

    @patch('helpers.OpenAIhelpers.get_enable_openai', return_value=False)
    def test_openai_edit_success(self, mock_enable):
        """Test openai_edit returns response on success"""
        from helpers.OpenAIhelpers import openai_edit
        
        mock_response = {'choices': [{'text': 'def foo():\n    pass'}]}
        with patch('helpers.OpenAIhelpers.openai.Edit.create', return_value=mock_response):
            result = openai_edit("Fix the code", "def foo():")
            self.assertEqual(result, mock_response)


if __name__ == '__main__':
    unittest.main()
