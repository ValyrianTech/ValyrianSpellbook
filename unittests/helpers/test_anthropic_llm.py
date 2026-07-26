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


class TestAnthropicLLMAdvanced(unittest.TestCase):
    """Advanced tests for anthropic_llm.py covering thinking, budget_tokens, and thinking_delta"""

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.anthropic_llm.anthropic.Anthropic')
    @patch('helpers.anthropic_llm.LOG')
    def test_supports_thinking_true(self, mock_log, mock_anthropic, mock_ws):
        """Test _supports_thinking returns True for thinking models"""
        from helpers.anthropic_llm import AnthropicLLM

        for model in ['claude-opus-4', 'claude-sonnet-4-5', 'claude-3-7-sonnet', 'claude-haiku-4-5']:
            llm = AnthropicLLM(model_name=model, api_key='test-key')
            self.assertTrue(llm._supports_thinking(), f"{model} should support thinking")

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.anthropic_llm.anthropic.Anthropic')
    @patch('helpers.anthropic_llm.LOG')
    def test_supports_thinking_false(self, mock_log, mock_anthropic, mock_ws):
        """Test _supports_thinking returns False for non-thinking models"""
        from helpers.anthropic_llm import AnthropicLLM

        llm = AnthropicLLM(model_name='claude-3-opus', api_key='test-key')
        self.assertFalse(llm._supports_thinking())

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.anthropic_llm.anthropic.Anthropic')
    @patch('helpers.anthropic_llm.broadcast_message')
    @patch('helpers.anthropic_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.anthropic_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.anthropic_llm.LOG')
    def test_thinking_level_with_thinking_model(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_anthropic, mock_ws):
        """Test thinking_level with a model that supports thinking"""
        from helpers.anthropic_llm import AnthropicLLM

        mock_start = MagicMock()
        mock_start.type = 'message_start'
        mock_start.message.usage.input_tokens = 10

        mock_end = MagicMock()
        mock_end.type = 'message_delta'
        mock_end.usage.output_tokens = 5

        mock_client = MagicMock()
        mock_client.messages.create.return_value = iter([mock_start, mock_end])
        mock_anthropic.return_value = mock_client

        llm = AnthropicLLM(model_name='claude-opus-4', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, thinking_level='medium')

        call_kwargs = mock_client.messages.create.call_args[1]
        self.assertIn('thinking', call_kwargs)
        self.assertEqual(call_kwargs['thinking']['type'], 'enabled')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.anthropic_llm.anthropic.Anthropic')
    @patch('helpers.anthropic_llm.broadcast_message')
    @patch('helpers.anthropic_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.anthropic_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.anthropic_llm.LOG')
    def test_thinking_level_invalid(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_anthropic, mock_ws):
        """Test invalid thinking_level with thinking model - thinking disabled"""
        from helpers.anthropic_llm import AnthropicLLM

        mock_start = MagicMock()
        mock_start.type = 'message_start'
        mock_start.message.usage.input_tokens = 10

        mock_end = MagicMock()
        mock_end.type = 'message_delta'
        mock_end.usage.output_tokens = 5

        mock_client = MagicMock()
        mock_client.messages.create.return_value = iter([mock_start, mock_end])
        mock_anthropic.return_value = mock_client

        llm = AnthropicLLM(model_name='claude-opus-4', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, thinking_level='invalid')

        call_kwargs = mock_client.messages.create.call_args[1]
        self.assertNotIn('thinking', call_kwargs)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.anthropic_llm.anthropic.Anthropic')
    @patch('helpers.anthropic_llm.broadcast_message')
    @patch('helpers.anthropic_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.anthropic_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.anthropic_llm.LOG')
    def test_thinking_level_non_thinking_model(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_anthropic, mock_ws):
        """Test thinking_level with a model that doesn't support thinking"""
        from helpers.anthropic_llm import AnthropicLLM

        mock_start = MagicMock()
        mock_start.type = 'message_start'
        mock_start.message.usage.input_tokens = 10

        mock_end = MagicMock()
        mock_end.type = 'message_delta'
        mock_end.usage.output_tokens = 5

        mock_client = MagicMock()
        mock_client.messages.create.return_value = iter([mock_start, mock_end])
        mock_anthropic.return_value = mock_client

        llm = AnthropicLLM(model_name='claude-3-opus', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, thinking_level='high')

        call_kwargs = mock_client.messages.create.call_args[1]
        self.assertNotIn('thinking', call_kwargs)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.anthropic_llm.anthropic.Anthropic')
    @patch('helpers.anthropic_llm.broadcast_message')
    @patch('helpers.anthropic_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.anthropic_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.anthropic_llm.LOG')
    def test_thinking_delta(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_anthropic, mock_ws):
        """Test handling of thinking_delta chunks"""
        from helpers.anthropic_llm import AnthropicLLM

        mock_start = MagicMock()
        mock_start.type = 'message_start'
        mock_start.message.usage.input_tokens = 10

        mock_block_start = MagicMock()
        mock_block_start.type = 'content_block_start'
        mock_block_start.content_block.type = 'thinking'

        mock_thinking_delta = MagicMock()
        mock_thinking_delta.type = 'content_block_delta'
        mock_thinking_delta.delta.type = 'thinking_delta'
        mock_thinking_delta.delta.thinking = 'Let me think...'

        mock_text_delta = MagicMock()
        mock_text_delta.type = 'content_block_delta'
        mock_text_delta.delta.text = 'The answer is 42'
        mock_text_delta.delta.type = 'text_delta'

        mock_end = MagicMock()
        mock_end.type = 'message_delta'
        mock_end.usage.output_tokens = 5

        mock_client = MagicMock()
        mock_client.messages.create.return_value = iter([mock_start, mock_block_start, mock_thinking_delta, mock_text_delta, mock_end])
        mock_anthropic.return_value = mock_client

        llm = AnthropicLLM(model_name='claude-opus-4', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, thinking_level='medium')

        self.assertIn('Let me think', result)
        self.assertIn('The answer is 42', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.anthropic_llm.anthropic.Anthropic')
    @patch('helpers.anthropic_llm.broadcast_message')
    @patch('helpers.anthropic_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.anthropic_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.anthropic_llm.LOG')
    def test_max_tokens_adjusted_for_thinking(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_anthropic, mock_ws):
        """Test that max_tokens is adjusted when it's less than budget_tokens"""
        from helpers.anthropic_llm import AnthropicLLM

        mock_start = MagicMock()
        mock_start.type = 'message_start'
        mock_start.message.usage.input_tokens = 10

        mock_end = MagicMock()
        mock_end.type = 'message_delta'
        mock_end.usage.output_tokens = 5

        mock_client = MagicMock()
        mock_client.messages.create.return_value = iter([mock_start, mock_end])
        mock_anthropic.return_value = mock_client

        llm = AnthropicLLM(model_name='claude-opus-4', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        # Pass a small max_tokens that will need to be adjusted
        result, usage = llm.get_completion_text(messages, thinking_level='high', max_tokens=100)

        call_kwargs = mock_client.messages.create.call_args[1]
        # max_tokens should have been adjusted to budget_tokens + 4096
        self.assertGreater(call_kwargs['max_tokens'], 100)


if __name__ == '__main__':
    unittest.main()
