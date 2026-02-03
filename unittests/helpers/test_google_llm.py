#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock


class TestGoogleLLM(unittest.TestCase):
    """Test cases for helpers/google_llm.py"""

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.google_llm.LOG')
    def test_init(self, mock_log, mock_ws):
        """Test GoogleLLM initialization"""
        from helpers.google_llm import GoogleLLM
        
        llm = GoogleLLM(model_name='gemini-pro', api_key='test-key')
        
        self.assertEqual(llm.model_name, 'gemini-pro')
        self.assertEqual(llm.api_key, 'test-key')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.google_llm.OpenAI')
    @patch('helpers.google_llm.broadcast_message')
    @patch('helpers.google_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.google_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.google_llm.LOG')
    def test_get_completion_text_error(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test get_completion_text handles errors"""
        from helpers.google_llm import GoogleLLM
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        llm = GoogleLLM(model_name='gemini-pro', api_key='test-key')
        messages = [{'role': 'user', 'content': 'Hello'}]
        
        result = llm.get_completion_text(messages)
        
        self.assertIn('Error', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.google_llm.OpenAI')
    @patch('helpers.google_llm.broadcast_message')
    @patch('helpers.google_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.google_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.google_llm.LOG')
    def test_get_completion_text_success(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test successful completion"""
        from helpers.google_llm import GoogleLLM
        
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = 'Hello!'
        mock_chunk.choices[0].delta.reasoning_content = None
        mock_chunk.usage = MagicMock()
        mock_chunk.usage.prompt_tokens = 10
        mock_chunk.usage.completion_tokens = 5
        mock_chunk.usage.total_tokens = 15
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk])
        mock_openai.return_value = mock_client
        
        llm = GoogleLLM(model_name='gemini-pro', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)
        
        self.assertEqual(result, 'Hello!')
        self.assertEqual(usage['prompt_tokens'], 10)


if __name__ == '__main__':
    unittest.main()
