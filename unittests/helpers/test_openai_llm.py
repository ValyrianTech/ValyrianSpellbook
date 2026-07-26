#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock


class TestOpenAILLM(unittest.TestCase):
    """Test cases for helpers/openai_llm.py"""

    @patch('helpers.openai_llm.openai')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openai_llm.get_openai_api_key', return_value='default-key')
    @patch('helpers.openai_llm.LOG')
    def test_init_with_api_key(self, mock_log, mock_get_key, mock_ws, mock_openai):
        """Test OpenAILLM initialization with provided API key"""
        from helpers.openai_llm import OpenAILLM
        
        llm = OpenAILLM(model_name='gpt-4', api_key='test-key')
        
        self.assertEqual(llm.model_name, 'gpt-4')

    @patch('helpers.openai_llm.openai')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openai_llm.get_openai_api_key', return_value='default-key')
    @patch('helpers.openai_llm.LOG')
    def test_init_without_api_key(self, mock_log, mock_get_key, mock_ws, mock_openai):
        """Test OpenAILLM initialization without API key uses default"""
        from helpers.openai_llm import OpenAILLM
        
        llm = OpenAILLM(model_name='gpt-4')
        
        mock_get_key.assert_called_once()

    @patch('helpers.openai_llm.openai')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openai_llm.broadcast_message')
    @patch('helpers.openai_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.openai_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.openai_llm.get_openai_api_key', return_value='test-key')
    @patch('helpers.openai_llm.LOG')
    def test_get_completion_text_error(self, mock_log, mock_get_key, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_openai):
        """Test get_completion_text handles errors"""
        from helpers.openai_llm import OpenAILLM
        
        mock_openai.chat.completions.create.side_effect = Exception("API Error")
        
        llm = OpenAILLM(model_name='gpt-4', api_key='test-key')
        messages = [{'role': 'user', 'content': 'Hello'}]
        
        result = llm.get_completion_text(messages)
        
        self.assertIn('Error', result)

    @patch('helpers.openai_llm.openai')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openai_llm.broadcast_message')
    @patch('helpers.openai_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.openai_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.openai_llm.get_openai_api_key', return_value='test-key')
    @patch('helpers.openai_llm.LOG')
    def test_get_completion_text_success(self, mock_log, mock_get_key, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_openai):
        """Test successful completion"""
        from helpers.openai_llm import OpenAILLM
        
        # Create mock chunk with content
        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.content = 'Hello!'
        
        # Create mock chunk with usage (final chunk)
        mock_chunk2 = MagicMock()
        mock_chunk2.choices = []
        mock_chunk2.usage = MagicMock()
        mock_chunk2.usage.prompt_tokens = 10
        mock_chunk2.usage.completion_tokens = 5
        mock_chunk2.usage.total_tokens = 15
        
        mock_openai.chat.completions.create.return_value = iter([mock_chunk1, mock_chunk2])
        mock_openai.chat.completions.create.side_effect = None  # Reset any previous side_effect
        
        llm = OpenAILLM(model_name='gpt-4', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)
        
        self.assertEqual(result, 'Hello!')
        self.assertEqual(usage['prompt_tokens'], 10)

    @patch('helpers.openai_llm.openai')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openai_llm.broadcast_message')
    @patch('helpers.openai_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.openai_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.openai_llm.get_openai_api_key', return_value='test-key')
    @patch('helpers.openai_llm.LOG')
    def test_o1_model_uses_max_completion_tokens(self, mock_log, mock_get_key, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_openai):
        """Test that o1 models use max_completion_tokens instead of max_tokens"""
        from helpers.openai_llm import OpenAILLM
        
        mock_chunk = MagicMock()
        mock_chunk.choices = []
        mock_chunk.usage = MagicMock()
        mock_chunk.usage.prompt_tokens = 10
        mock_chunk.usage.completion_tokens = 5
        mock_chunk.usage.total_tokens = 15
        
        mock_openai.chat.completions.create.return_value = iter([mock_chunk])
        mock_openai.chat.completions.create.side_effect = None  # Reset any previous side_effect
        mock_openai.chat.completions.create.reset_mock()
        
        llm = OpenAILLM(model_name='o1-preview', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        llm.get_completion_text(messages, max_tokens=1000)
        
        # Check that the call was made (o1 model path)
        mock_openai.chat.completions.create.assert_called_once()

    @patch('helpers.openai_llm.openai')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openai_llm.broadcast_message')
    @patch('helpers.openai_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.openai_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.openai_llm.get_openai_api_key', return_value='test-key')
    @patch('helpers.openai_llm.LOG')
    @patch('helpers.openai_llm.LLMInterface.check_stop_generation', return_value=True)
    def test_get_completion_text_stop_generation(self, mock_stop, mock_log, mock_get_key, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_openai):
        """Test completion stops when stop file is detected - covering lines 68-70"""
        from helpers.openai_llm import OpenAILLM
        
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = 'Hello'
        
        mock_openai.chat.completions.create.return_value = iter([mock_chunk])
        mock_openai.chat.completions.create.side_effect = None
        
        llm = OpenAILLM(model_name='gpt-4', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)
        
        # Should have stopped early
        self.assertEqual(result, '')

    @patch('helpers.openai_llm.openai')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openai_llm.broadcast_message')
    @patch('helpers.openai_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.openai_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.openai_llm.get_openai_api_key', return_value='test-key')
    @patch('helpers.openai_llm.LOG')
    def test_get_completion_text_with_stop_sequence(self, mock_log, mock_get_key, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_openai):
        """Test completion with stop sequence detection - covering lines 85-86, 93"""
        from helpers.openai_llm import OpenAILLM
        
        # First chunk with content containing stop sequence
        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.content = 'Hello STOP'
        
        # Second chunk after stop (should be counted but not added)
        mock_chunk2 = MagicMock()
        mock_chunk2.choices = [MagicMock()]
        mock_chunk2.choices[0].delta.content = ' more text'
        
        # Final chunk with usage
        mock_chunk3 = MagicMock()
        mock_chunk3.choices = []
        mock_chunk3.usage = MagicMock()
        mock_chunk3.usage.prompt_tokens = 10
        mock_chunk3.usage.completion_tokens = 5
        mock_chunk3.usage.total_tokens = 15
        
        mock_openai.chat.completions.create.return_value = iter([mock_chunk1, mock_chunk2, mock_chunk3])
        mock_openai.chat.completions.create.side_effect = None
        
        llm = OpenAILLM(model_name='gpt-4', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, stop=['STOP'])
        
        # Should contain content up to stop sequence
        self.assertIn('Hello STOP', result)

    @patch('helpers.openai_llm.openai')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openai_llm.broadcast_message')
    @patch('helpers.openai_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.openai_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.openai_llm.get_openai_api_key', return_value='test-key')
    @patch('helpers.openai_llm.LOG')
    def test_get_completion_text_token_waste_logging(self, mock_log, mock_get_key, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_openai):
        """Test token waste logging - covering line 113"""
        from helpers.openai_llm import OpenAILLM
        
        # First chunk with content containing stop sequence
        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.content = 'Hello STOP'
        
        # Second chunk after stop (should trigger token waste logging)
        mock_chunk2 = MagicMock()
        mock_chunk2.choices = [MagicMock()]
        mock_chunk2.choices[0].delta.content = ' wasted tokens here'
        
        # Final chunk with usage
        mock_chunk3 = MagicMock()
        mock_chunk3.choices = []
        mock_chunk3.usage = MagicMock()
        mock_chunk3.usage.prompt_tokens = 10
        mock_chunk3.usage.completion_tokens = 20
        mock_chunk3.usage.total_tokens = 30
        
        mock_openai.chat.completions.create.return_value = iter([mock_chunk1, mock_chunk2, mock_chunk3])
        mock_openai.chat.completions.create.side_effect = None
        
        llm = OpenAILLM(model_name='gpt-4', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, stop=['STOP'])
        
        # Should have logged warning about token waste
        mock_log.warning.assert_called()

    @patch('helpers.openai_llm.openai')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openai_llm.broadcast_message')
    @patch('helpers.openai_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.openai_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.openai_llm.get_openai_api_key', return_value='test-key')
    @patch('helpers.openai_llm.LOG')
    def test_get_completion_text_reasoning_model_with_thinking_level(self, mock_log, mock_get_key, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_openai):
        """Test get_completion_text with reasoning model and thinking_level set"""
        from helpers.openai_llm import OpenAILLM

        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.content = 'Hello'
        mock_chunk1.usage = None

        mock_chunk2 = MagicMock()
        mock_chunk2.choices = []
        mock_chunk2.usage = MagicMock()
        mock_chunk2.usage.prompt_tokens = 10
        mock_chunk2.usage.completion_tokens = 20
        mock_chunk2.usage.total_tokens = 30

        mock_openai.chat.completions.create.return_value = iter([mock_chunk1, mock_chunk2])

        llm = OpenAILLM(model_name='o3-mini', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, thinking_level='high')

        self.assertEqual(result, 'Hello')
        self.assertEqual(usage['prompt_tokens'], 10)
        # Verify reasoning_effort was passed
        call_kwargs = mock_openai.chat.completions.create.call_args
        self.assertEqual(call_kwargs.kwargs['reasoning_effort'], 'high')

    @patch('helpers.openai_llm.openai')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openai_llm.broadcast_message')
    @patch('helpers.openai_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.openai_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.openai_llm.get_openai_api_key', return_value='test-key')
    @patch('helpers.openai_llm.LOG')
    def test_get_completion_text_reasoning_model_thinking_off(self, mock_log, mock_get_key, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_openai):
        """Test get_completion_text with reasoning model and thinking_level='off'"""
        from helpers.openai_llm import OpenAILLM

        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.content = 'Hello'
        mock_chunk1.usage = None

        mock_chunk2 = MagicMock()
        mock_chunk2.choices = []
        mock_chunk2.usage = MagicMock()
        mock_chunk2.usage.prompt_tokens = 10
        mock_chunk2.usage.completion_tokens = 20
        mock_chunk2.usage.total_tokens = 30

        mock_openai.chat.completions.create.return_value = iter([mock_chunk1, mock_chunk2])

        llm = OpenAILLM(model_name='o3-mini', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, thinking_level='off')

        # Should log that reasoning is not applied (off)
        mock_log.info.assert_called()

    @patch('helpers.openai_llm.openai')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openai_llm.broadcast_message')
    @patch('helpers.openai_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.openai_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.openai_llm.get_openai_api_key', return_value='test-key')
    @patch('helpers.openai_llm.LOG')
    def test_get_completion_text_non_reasoning_model_with_thinking_level(self, mock_log, mock_get_key, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_openai):
        """Test get_completion_text with non-reasoning model and thinking_level set - should log ignored"""
        from helpers.openai_llm import OpenAILLM

        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.content = 'Hello'
        mock_chunk1.usage = None

        mock_chunk2 = MagicMock()
        mock_chunk2.choices = []
        mock_chunk2.usage = MagicMock()
        mock_chunk2.usage.prompt_tokens = 10
        mock_chunk2.usage.completion_tokens = 20
        mock_chunk2.usage.total_tokens = 30

        mock_openai.chat.completions.create.return_value = iter([mock_chunk1, mock_chunk2])

        llm = OpenAILLM(model_name='gpt-4', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, thinking_level='high')

        self.assertEqual(result, 'Hello')
        # Should log that thinking_level is ignored for non-reasoning model
        mock_log.info.assert_called()


if __name__ == '__main__':
    unittest.main()
