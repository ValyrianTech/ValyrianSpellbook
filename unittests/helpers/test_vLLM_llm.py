#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock


class TestVLLMLLM(unittest.TestCase):
    """Test cases for helpers/vLLM_llm.py"""

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.vLLM_llm.LOG')
    def test_init(self, mock_log, mock_ws):
        """Test VLLMLLM initialization"""
        from helpers.vLLM_llm import VLLMLLM
        
        llm = VLLMLLM(model_name='mistral-7b', host='http://localhost', port=8000)
        
        self.assertEqual(llm.model_name, 'mistral-7b')
        self.assertEqual(llm.host, 'http://localhost')
        self.assertEqual(llm.port, 8000)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.vLLM_llm.OpenAI')
    @patch('helpers.vLLM_llm.broadcast_message')
    @patch('helpers.vLLM_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.vLLM_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.vLLM_llm.LOG')
    def test_get_completion_text_error(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test get_completion_text handles errors"""
        from helpers.vLLM_llm import VLLMLLM
        
        mock_client = MagicMock()
        mock_client.completions.create.side_effect = Exception("Connection Error")
        mock_openai.return_value = mock_client
        
        llm = VLLMLLM(model_name='mistral-7b', host='http://localhost', port=8000)
        messages = [{'role': 'user', 'content': 'Hello'}]
        
        result = llm.get_completion_text(messages)
        
        self.assertIn('Error', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.vLLM_llm.OpenAI')
    @patch('helpers.vLLM_llm.broadcast_message')
    @patch('helpers.vLLM_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.vLLM_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.vLLM_llm.LOG')
    def test_get_completion_text_success(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test successful completion"""
        from helpers.vLLM_llm import VLLMLLM
        
        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].text = 'Hello!'
        
        mock_chunk2 = MagicMock()
        mock_chunk2.choices = []
        mock_chunk2.usage = MagicMock()
        mock_chunk2.usage.prompt_tokens = 10
        mock_chunk2.usage.completion_tokens = 5
        mock_chunk2.usage.total_tokens = 15
        
        mock_client = MagicMock()
        mock_client.completions.create.return_value = iter([mock_chunk1, mock_chunk2])
        mock_openai.return_value = mock_client
        
        llm = VLLMLLM(model_name='mistral-7b', host='http://localhost', port=8000)
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
