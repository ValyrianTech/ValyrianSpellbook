#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock


class TestTogetherAILLM(unittest.TestCase):
    """Test cases for helpers/together_ai_LLM.py"""

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.together_ai_LLM.Together')
    @patch('helpers.together_ai_LLM.get_together_ai_bearer_token', return_value='default-token')
    @patch('helpers.together_ai_LLM.LOG')
    def test_init_with_api_key(self, mock_log, mock_get_token, mock_together, mock_ws):
        """Test TogetherAILLM initialization with provided API key"""
        from helpers.together_ai_LLM import TogetherAILLM
        
        llm = TogetherAILLM(model_name='mistralai/Mixtral-8x7B', api_key='test-key')
        
        self.assertEqual(llm.model_name, 'mistralai/Mixtral-8x7B')
        self.assertEqual(llm.api_key, 'test-key')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.together_ai_LLM.Together')
    @patch('helpers.together_ai_LLM.get_together_ai_bearer_token', return_value='default-token')
    @patch('helpers.together_ai_LLM.LOG')
    def test_init_without_api_key(self, mock_log, mock_get_token, mock_together, mock_ws):
        """Test TogetherAILLM initialization without API key uses default"""
        from helpers.together_ai_LLM import TogetherAILLM
        
        llm = TogetherAILLM(model_name='mistralai/Mixtral-8x7B')
        
        self.assertEqual(llm.api_key, 'default-token')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.together_ai_LLM.Together')
    @patch('helpers.together_ai_LLM.broadcast_message')
    @patch('helpers.together_ai_LLM.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.together_ai_LLM.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.together_ai_LLM.get_together_ai_bearer_token', return_value='test-token')
    @patch('helpers.together_ai_LLM.LOG')
    def test_get_completion_text_error(self, mock_log, mock_get_token, mock_sender, mock_channel, mock_broadcast, mock_together, mock_ws):
        """Test get_completion_text handles errors"""
        from helpers.together_ai_LLM import TogetherAILLM
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_together.return_value = mock_client
        
        llm = TogetherAILLM(model_name='mistralai/Mixtral-8x7B', api_key='test-key')
        messages = [{'role': 'user', 'content': 'Hello'}]
        
        result = llm.get_completion_text(messages)
        
        self.assertIn('Error', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.together_ai_LLM.Together')
    @patch('helpers.together_ai_LLM.broadcast_message')
    @patch('helpers.together_ai_LLM.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.together_ai_LLM.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.together_ai_LLM.get_together_ai_bearer_token', return_value='test-token')
    @patch('helpers.together_ai_LLM.LOG')
    def test_get_completion_text_success(self, mock_log, mock_get_token, mock_sender, mock_channel, mock_broadcast, mock_together, mock_ws):
        """Test successful completion"""
        from helpers.together_ai_LLM import TogetherAILLM
        
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = 'Hello!'
        mock_chunk.usage = MagicMock()
        mock_chunk.usage.prompt_tokens = 10
        mock_chunk.usage.completion_tokens = 5
        mock_chunk.usage.total_tokens = 15
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk])
        mock_together.return_value = mock_client
        
        llm = TogetherAILLM(model_name='mistralai/Mixtral-8x7B', api_key='test-key')
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
