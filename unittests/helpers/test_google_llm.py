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


    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.google_llm.OpenAI')
    @patch('helpers.google_llm.broadcast_message')
    @patch('helpers.google_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.google_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.google_llm.LOG')
    @patch('helpers.google_llm.LLMInterface.check_stop_generation', return_value=True)
    def test_get_completion_text_stop_generation(self, mock_stop, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion stops when stop file is detected"""
        from helpers.google_llm import GoogleLLM
        
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = 'Hello'
        mock_chunk.choices[0].delta.reasoning_content = None
        mock_chunk.usage = None
        
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
        
        # Should have stopped early
        self.assertEqual(result, '')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.google_llm.OpenAI')
    @patch('helpers.google_llm.broadcast_message')
    @patch('helpers.google_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.google_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.google_llm.LOG')
    def test_get_completion_text_empty_choices(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion handles empty choices"""
        from helpers.google_llm import GoogleLLM
        
        mock_chunk = MagicMock()
        mock_chunk.choices = []
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
        
        self.assertEqual(result, '')
        self.assertEqual(usage['prompt_tokens'], 10)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.google_llm.OpenAI')
    @patch('helpers.google_llm.broadcast_message')
    @patch('helpers.google_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.google_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.google_llm.LOG')
    def test_get_completion_text_with_reasoning(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion with reasoning content - covering lines 59-62"""
        from helpers.google_llm import GoogleLLM
        
        # Create mock chunk with reasoning content
        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.reasoning_content = 'Let me think about this...'
        mock_chunk1.choices[0].delta.content = None
        mock_chunk1.usage = None
        
        # Create mock chunk with actual content
        mock_chunk2 = MagicMock()
        mock_chunk2.choices = [MagicMock()]
        mock_chunk2.choices[0].delta.reasoning_content = None
        mock_chunk2.choices[0].delta.content = 'The answer is 42'
        mock_chunk2.usage = MagicMock()
        mock_chunk2.usage.prompt_tokens = 10
        mock_chunk2.usage.completion_tokens = 15
        mock_chunk2.usage.total_tokens = 25
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk1, mock_chunk2])
        mock_openai.return_value = mock_client
        
        llm = GoogleLLM(model_name='gemini-pro', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'What is the meaning of life?'}]
        result, usage = llm.get_completion_text(messages)
        
        # Result should contain both reasoning wrapped in think tags and the answer
        self.assertIn('<think>', result)
        self.assertIn('Let me think about this...', result)
        self.assertIn('The answer is 42', result)
        self.assertEqual(usage['prompt_tokens'], 10)


if __name__ == '__main__':
    unittest.main()
