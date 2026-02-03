#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock


class TestAnthropicLLM(unittest.TestCase):
    """Test cases for helpers/anthropic_llm.py"""

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.anthropic_llm.anthropic.Anthropic')
    @patch('helpers.anthropic_llm.LOG')
    def test_init(self, mock_log, mock_anthropic, mock_ws):
        """Test AnthropicLLM initialization"""
        from helpers.anthropic_llm import AnthropicLLM
        
        llm = AnthropicLLM(model_name='claude-3-opus', api_key='test-key')
        
        self.assertEqual(llm.model_name, 'claude-3-opus')
        mock_anthropic.assert_called_once_with(api_key='test-key')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.anthropic_llm.anthropic.Anthropic')
    @patch('helpers.anthropic_llm.broadcast_message')
    @patch('helpers.anthropic_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.anthropic_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.anthropic_llm.LOG')
    def test_get_completion_text_error(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_anthropic, mock_ws):
        """Test get_completion_text handles errors"""
        from helpers.anthropic_llm import AnthropicLLM
        
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic.return_value = mock_client
        
        llm = AnthropicLLM(model_name='claude-3-opus', api_key='test-key')
        messages = [{'role': 'user', 'content': 'Hello'}]
        
        result, usage = llm.get_completion_text(messages)
        
        self.assertIn('Error', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.anthropic_llm.anthropic.Anthropic')
    @patch('helpers.anthropic_llm.broadcast_message')
    @patch('helpers.anthropic_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.anthropic_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.anthropic_llm.LOG')
    def test_get_completion_text_success(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_anthropic, mock_ws):
        """Test successful completion"""
        from helpers.anthropic_llm import AnthropicLLM
        
        # Create mock chunks
        mock_start_chunk = MagicMock()
        mock_start_chunk.type = 'message_start'
        mock_start_chunk.message.usage.input_tokens = 10
        
        mock_content_chunk = MagicMock()
        mock_content_chunk.type = 'content_block_delta'
        mock_content_chunk.delta.text = 'Hello!'
        
        mock_end_chunk = MagicMock()
        mock_end_chunk.type = 'message_delta'
        mock_end_chunk.usage.output_tokens = 5
        
        mock_client = MagicMock()
        mock_client.messages.create.return_value = iter([mock_start_chunk, mock_content_chunk, mock_end_chunk])
        mock_anthropic.return_value = mock_client
        
        llm = AnthropicLLM(model_name='claude-3-opus', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)
        
        self.assertEqual(result, 'Hello!')
        self.assertEqual(usage['prompt_tokens'], 10)
        self.assertEqual(usage['completion_tokens'], 5)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.anthropic_llm.anthropic.Anthropic')
    @patch('helpers.anthropic_llm.broadcast_message')
    @patch('helpers.anthropic_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.anthropic_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.anthropic_llm.LOG')
    @patch('helpers.anthropic_llm.LLMInterface.check_stop_generation', return_value=True)
    def test_get_completion_text_stop_generation(self, mock_stop, mock_log, mock_sender, mock_channel, mock_broadcast, mock_anthropic, mock_ws):
        """Test completion stops when stop file is detected - covering lines 39-41"""
        from helpers.anthropic_llm import AnthropicLLM
        
        # Create mock chunk that would normally produce output
        mock_content_chunk = MagicMock()
        mock_content_chunk.type = 'content_block_delta'
        mock_content_chunk.delta.text = 'Hello!'
        
        mock_client = MagicMock()
        mock_client.messages.create.return_value = iter([mock_content_chunk])
        mock_anthropic.return_value = mock_client
        
        llm = AnthropicLLM(model_name='claude-3-opus', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)
        
        # Should have stopped early with empty completion
        self.assertEqual(result, '')


if __name__ == '__main__':
    unittest.main()
