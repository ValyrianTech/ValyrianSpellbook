#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock


class TestOllamaChatLLM(unittest.TestCase):
    """Test cases for helpers/ollama_chat_llm.py"""

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_init(self, mock_log, mock_ws):
        """Test OllamaChatLLM initialization"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
        
        self.assertEqual(llm.model_name, 'llama2')
        self.assertEqual(llm.host, 'http://localhost')
        self.assertEqual(llm.port, 11434)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.OpenAI')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_get_completion_text_error(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test get_completion_text handles errors"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Connection Error")
        mock_openai.return_value = mock_client
        
        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
        messages = [{'role': 'user', 'content': 'Hello'}]
        
        result = llm.get_completion_text(messages)
        
        self.assertIn('Error', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.OpenAI')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_get_completion_text_success(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test successful completion"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        # Create mock chunk with content - need to explicitly set reasoning attributes to None/False
        # to prevent MagicMock from returning truthy mocks for hasattr checks
        mock_chunk1 = MagicMock()
        mock_choice = MagicMock()
        mock_choice.delta = MagicMock()
        mock_choice.delta.content = 'Hello!'
        mock_choice.delta.reasoning_content = None
        mock_choice.delta.reasoning = None
        mock_choice.message = None
        mock_choice.reasoning_content = None
        mock_choice.reasoning = None
        mock_chunk1.choices = [mock_choice]
        mock_chunk1.usage = None
        
        # Create mock chunk with usage (final chunk)
        mock_chunk2 = MagicMock()
        mock_chunk2.choices = []
        mock_chunk2.usage = MagicMock()
        mock_chunk2.usage.prompt_tokens = 10
        mock_chunk2.usage.completion_tokens = 5
        mock_chunk2.usage.total_tokens = 15
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk1, mock_chunk2])
        mock_openai.return_value = mock_client
        
        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
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
