#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock


class TestOllamaLLM(unittest.TestCase):
    """Test cases for helpers/ollama_llm.py"""

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_llm.LOG')
    def test_init(self, mock_log, mock_ws):
        """Test OllamaLLM initialization"""
        from helpers.ollama_llm import OllamaLLM
        
        llm = OllamaLLM(model_name='llama2', host='http://localhost', port=11434)
        
        self.assertEqual(llm.model_name, 'llama2')
        self.assertEqual(llm.host, 'http://localhost')
        self.assertEqual(llm.port, 11434)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_llm.OpenAI')
    @patch('helpers.ollama_llm.broadcast_message')
    @patch('helpers.ollama_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_llm.LOG')
    def test_get_completion_text_error(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test get_completion_text handles errors"""
        from helpers.ollama_llm import OllamaLLM
        
        mock_client = MagicMock()
        mock_client.completions.create.side_effect = Exception("Connection Error")
        mock_openai.return_value = mock_client
        
        llm = OllamaLLM(model_name='llama2', host='http://localhost', port=11434)
        messages = [{'role': 'user', 'content': 'Hello'}]
        
        result = llm.get_completion_text(messages)
        
        self.assertIn('Error', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_llm.OpenAI')
    @patch('helpers.ollama_llm.broadcast_message')
    @patch('helpers.ollama_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_llm.LOG')
    def test_get_completion_text_success(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test successful completion"""
        from helpers.ollama_llm import OllamaLLM
        
        # Create mock chunk with content
        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].text = 'Hello!'
        
        # Create mock chunk with usage (final chunk)
        mock_chunk2 = MagicMock()
        mock_chunk2.choices = []
        mock_chunk2.usage = MagicMock()
        mock_chunk2.usage.prompt_tokens = 10
        mock_chunk2.usage.completion_tokens = 5
        mock_chunk2.usage.total_tokens = 15
        
        mock_client = MagicMock()
        mock_client.completions.create.return_value = iter([mock_chunk1, mock_chunk2])
        mock_openai.return_value = mock_client
        
        llm = OllamaLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)
        
        self.assertEqual(result, 'Hello!')
        self.assertEqual(usage['prompt_tokens'], 10)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_llm.OpenAI')
    @patch('helpers.ollama_llm.broadcast_message')
    @patch('helpers.ollama_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_llm.LOG')
    def test_get_completion_with_multimodal_messages(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion with multimodal message format"""
        from helpers.ollama_llm import OllamaLLM
        
        mock_chunk = MagicMock()
        mock_chunk.choices = []
        mock_chunk.usage = MagicMock()
        mock_chunk.usage.prompt_tokens = 10
        mock_chunk.usage.completion_tokens = 5
        mock_chunk.usage.total_tokens = 15
        
        mock_client = MagicMock()
        mock_client.completions.create.return_value = iter([mock_chunk])
        mock_openai.return_value = mock_client
        
        llm = OllamaLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        # Multimodal message format
        messages = [{'role': 'user', 'content': [{'text': 'Hello'}, {'image_url': 'data:image/png;base64,...'}]}]
        result, usage = llm.get_completion_text(messages)
        
        self.assertIsInstance(result, str)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_llm.OpenAI')
    @patch('helpers.ollama_llm.broadcast_message')
    @patch('helpers.ollama_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_llm.LOG')
    def test_get_completion_with_string_content_in_loop(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion with string content in message loop - covering line 32"""
        from helpers.ollama_llm import OllamaLLM
        
        mock_chunk = MagicMock()
        mock_chunk.choices = []
        mock_chunk.usage = MagicMock()
        mock_chunk.usage.prompt_tokens = 10
        mock_chunk.usage.completion_tokens = 5
        mock_chunk.usage.total_tokens = 15
        
        mock_client = MagicMock()
        mock_client.completions.create.return_value = iter([mock_chunk])
        mock_openai.return_value = mock_client
        
        llm = OllamaLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        # Multiple messages with string content (not single user message)
        messages = [
            {'role': 'system', 'content': 'You are helpful'},
            {'role': 'user', 'content': 'Hello'}
        ]
        result, usage = llm.get_completion_text(messages)
        
        self.assertIsInstance(result, str)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_llm.OpenAI')
    @patch('helpers.ollama_llm.broadcast_message')
    @patch('helpers.ollama_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_llm.LOG')
    @patch('helpers.ollama_llm.LLMInterface.check_stop_generation', return_value=True)
    def test_get_completion_text_stop_generation(self, mock_stop, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion stops when stop file is detected - covering lines 65-67"""
        from helpers.ollama_llm import OllamaLLM
        
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].text = 'Hello'
        
        mock_client = MagicMock()
        mock_client.completions.create.return_value = iter([mock_chunk])
        mock_openai.return_value = mock_client
        
        llm = OllamaLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)
        
        # Should have stopped early
        self.assertEqual(result, '')


if __name__ == '__main__':
    unittest.main()
