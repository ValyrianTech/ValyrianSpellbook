#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock


class TestOpenRouterLLM(unittest.TestCase):
    """Test cases for helpers/openrouter_llm.py"""

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openrouter_llm.OpenAI')
    @patch('helpers.openrouter_llm.get_openrouter_api_key', return_value='default-key')
    @patch('helpers.openrouter_llm.LOG')
    def test_init_with_api_key(self, mock_log, mock_get_key, mock_openai, mock_ws):
        """Test OpenRouterLLM initialization with provided API key"""
        from helpers.openrouter_llm import OpenRouterLLM

        llm = OpenRouterLLM(model_name='openai/gpt-4o', api_key='test-key')

        self.assertEqual(llm.model_name, 'openai/gpt-4o')
        self.assertEqual(llm.api_key, 'test-key')
        mock_openai.assert_called_once_with(api_key='test-key', base_url="https://openrouter.ai/api/v1")

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openrouter_llm.OpenAI')
    @patch('helpers.openrouter_llm.get_openrouter_api_key', return_value='default-key')
    @patch('helpers.openrouter_llm.LOG')
    def test_init_without_api_key(self, mock_log, mock_get_key, mock_openai, mock_ws):
        """Test OpenRouterLLM initialization without API key uses default"""
        from helpers.openrouter_llm import OpenRouterLLM

        llm = OpenRouterLLM(model_name='openai/gpt-4o')

        self.assertEqual(llm.api_key, 'default-key')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openrouter_llm.OpenAI')
    @patch('helpers.openrouter_llm.broadcast_message')
    @patch('helpers.openrouter_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.openrouter_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.openrouter_llm.get_openrouter_api_key', return_value='test-key')
    @patch('helpers.openrouter_llm.LOG')
    def test_get_completion_text_error(self, mock_log, mock_get_key, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test get_completion_text handles errors"""
        from helpers.openrouter_llm import OpenRouterLLM

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client

        llm = OpenRouterLLM(model_name='openai/gpt-4o', api_key='test-key')
        messages = [{'role': 'user', 'content': 'Hello'}]

        result = llm.get_completion_text(messages)

        self.assertIn('Error', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openrouter_llm.OpenAI')
    @patch('helpers.openrouter_llm.broadcast_message')
    @patch('helpers.openrouter_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.openrouter_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.openrouter_llm.get_openrouter_api_key', return_value='test-key')
    @patch('helpers.openrouter_llm.LOG')
    def test_get_completion_text_success(self, mock_log, mock_get_key, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test successful completion"""
        from helpers.openrouter_llm import OpenRouterLLM

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = 'Hello!'
        mock_chunk.choices[0].delta.reasoning = None
        mock_chunk.usage = MagicMock()
        mock_chunk.usage.prompt_tokens = 10
        mock_chunk.usage.completion_tokens = 5
        mock_chunk.usage.total_tokens = 15

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk])
        mock_openai.return_value = mock_client

        llm = OpenRouterLLM(model_name='openai/gpt-4o', api_key='test-key')
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
    @patch('helpers.openrouter_llm.OpenAI')
    @patch('helpers.openrouter_llm.broadcast_message')
    @patch('helpers.openrouter_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.openrouter_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.openrouter_llm.get_openrouter_api_key', return_value='test-key')
    @patch('helpers.openrouter_llm.LOG')
    def test_get_completion_text_with_reasoning(self, mock_log, mock_get_key, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion with reasoning content via delta.reasoning"""
        from helpers.openrouter_llm import OpenRouterLLM

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.reasoning = 'Thinking about this...'
        mock_chunk.choices[0].delta.content = None
        mock_chunk.usage = None

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk])
        mock_openai.return_value = mock_client

        llm = OpenRouterLLM(model_name='openai/o1', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)

        self.assertIn('Thinking about this', result)
        self.assertIn('', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openrouter_llm.OpenAI')
    @patch('helpers.openrouter_llm.broadcast_message')
    @patch('helpers.openrouter_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.openrouter_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.openrouter_llm.get_openrouter_api_key', return_value='test-key')
    @patch('helpers.openrouter_llm.LOG')
    def test_get_completion_text_with_inline_think_tags(self, mock_log, mock_get_key, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion with inline think tags in content"""
        from helpers.openrouter_llm import OpenRouterLLM

        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.content = 'The answer is 42'
        mock_chunk1.choices[0].delta.reasoning = None
        mock_chunk1.usage = None

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk1])
        mock_openai.return_value = mock_client

        llm = OpenRouterLLM(model_name='openai/gpt-4o', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)

        self.assertIn('The answer is 42', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openrouter_llm.OpenAI')
    @patch('helpers.openrouter_llm.broadcast_message')
    @patch('helpers.openrouter_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.openrouter_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.openrouter_llm.get_openrouter_api_key', return_value='test-key')
    @patch('helpers.openrouter_llm.LOG')
    @patch('helpers.openrouter_llm.LLMInterface.check_stop_generation', return_value=True)
    def test_get_completion_text_stop_generation(self, mock_stop, mock_log, mock_get_key, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion stops when stop file is detected"""
        from helpers.openrouter_llm import OpenRouterLLM

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = 'Hello'
        mock_chunk.choices[0].delta.reasoning = None
        mock_chunk.usage = None

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk])
        mock_openai.return_value = mock_client

        llm = OpenRouterLLM(model_name='openai/gpt-4o', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)

        self.assertEqual(result, '')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openrouter_llm.OpenAI')
    @patch('helpers.openrouter_llm.broadcast_message')
    @patch('helpers.openrouter_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.openrouter_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.openrouter_llm.get_openrouter_api_key', return_value='test-key')
    @patch('helpers.openrouter_llm.LOG')
    def test_get_completion_text_with_thinking_level(self, mock_log, mock_get_key, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion with thinking_level parameter"""
        from helpers.openrouter_llm import OpenRouterLLM

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = 'Hello!'
        mock_chunk.choices[0].delta.reasoning = None
        mock_chunk.usage = MagicMock()
        mock_chunk.usage.prompt_tokens = 10
        mock_chunk.usage.completion_tokens = 5
        mock_chunk.usage.total_tokens = 15

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk])
        mock_openai.return_value = mock_client

        llm = OpenRouterLLM(model_name='openai/o1', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, thinking_level='high')

        self.assertEqual(result, 'Hello!')
        # Verify extra_body was passed with reasoning effort
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        self.assertIn('extra_body', call_kwargs)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openrouter_llm.OpenAI')
    @patch('helpers.openrouter_llm.broadcast_message')
    @patch('helpers.openrouter_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.openrouter_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.openrouter_llm.get_openrouter_api_key', return_value='test-key')
    @patch('helpers.openrouter_llm.LOG')
    def test_get_completion_text_empty_choices(self, mock_log, mock_get_key, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion with chunk that has empty choices (usage-only chunk)"""
        from helpers.openrouter_llm import OpenRouterLLM

        mock_chunk_usage = MagicMock()
        mock_chunk_usage.choices = []
        mock_chunk_usage.usage = MagicMock()
        mock_chunk_usage.usage.prompt_tokens = 10
        mock_chunk_usage.usage.completion_tokens = 5
        mock_chunk_usage.usage.total_tokens = 15

        mock_chunk_content = MagicMock()
        mock_chunk_content.choices = [MagicMock()]
        mock_chunk_content.choices[0].delta.content = 'Hello!'
        mock_chunk_content.choices[0].delta.reasoning = None
        mock_chunk_content.usage = None

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk_usage, mock_chunk_content])
        mock_openai.return_value = mock_client

        llm = OpenRouterLLM(model_name='openai/gpt-4o', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)

        self.assertEqual(result, 'Hello!')
        self.assertEqual(usage['prompt_tokens'], 10)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openrouter_llm.OpenAI')
    @patch('helpers.openrouter_llm.get_openrouter_api_key', return_value='default-key')
    @patch('helpers.openrouter_llm.LOG')
    def test_get_completion_text_error_connection(self, mock_log, mock_get_key, mock_openai, mock_ws):
        """Test get_completion_text when connection raises an error"""
        from helpers.openrouter_llm import OpenRouterLLM

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception('Connection refused')
        mock_openai.return_value = mock_client

        llm = OpenRouterLLM(model_name='openai/gpt-4o', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result = llm.get_completion_text(messages)

        # Error path returns just a string, not a tuple
        if isinstance(result, tuple):
            result = result[0]
        self.assertIn('Error: Unable to connect to OpenRouter', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openrouter_llm.OpenAI')
    @patch('helpers.openrouter_llm.broadcast_message')
    @patch('helpers.openrouter_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.openrouter_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.openrouter_llm.get_openrouter_api_key', return_value='default-key')
    @patch('helpers.openrouter_llm.LOG')
    def test_get_completion_text_thinking_level_off(self, mock_log, mock_get_key, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test get_completion_text with thinking_level='off' - should not add reasoning effort"""
        from helpers.openrouter_llm import OpenRouterLLM

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = 'Hello!'
        mock_chunk.choices[0].delta.reasoning = None
        mock_chunk.usage = MagicMock()
        mock_chunk.usage.prompt_tokens = 10
        mock_chunk.usage.completion_tokens = 5
        mock_chunk.usage.total_tokens = 15

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk])
        mock_openai.return_value = mock_client

        llm = OpenRouterLLM(model_name='openai/gpt-4o', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, thinking_level='off')

        # thinking_level='off' maps to 'none' in THINKING_LEVEL_OPENROUTER, so extra_body IS set with effort='none'
        call_kwargs = mock_client.chat.completions.create.call_args
        self.assertIn('extra_body', call_kwargs.kwargs)
        self.assertEqual(call_kwargs.kwargs['extra_body']['reasoning']['effort'], 'none')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.openrouter_llm.OpenAI')
    @patch('helpers.openrouter_llm.broadcast_message')
    @patch('helpers.openrouter_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.openrouter_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.openrouter_llm.get_openrouter_api_key', return_value='default-key')
    @patch('helpers.openrouter_llm.LOG')
    def test_get_completion_text_with_reasoning_content(self, mock_log, mock_get_key, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test get_completion_text with reasoning content from OpenRouter"""
        from helpers.openrouter_llm import OpenRouterLLM

        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.content = None
        mock_chunk1.choices[0].delta.reasoning = 'Thinking about this...'
        mock_chunk1.usage = None

        mock_chunk2 = MagicMock()
        mock_chunk2.choices = [MagicMock()]
        mock_chunk2.choices[0].delta.content = 'Answer!'
        mock_chunk2.choices[0].delta.reasoning = None
        mock_chunk2.usage = MagicMock()
        mock_chunk2.usage.prompt_tokens = 10
        mock_chunk2.usage.completion_tokens = 5
        mock_chunk2.usage.total_tokens = 15

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk1, mock_chunk2])
        mock_openai.return_value = mock_client

        llm = OpenRouterLLM(model_name='openai/gpt-4o', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, thinking_level='medium')

        # Should contain reasoning wrapped in think tags and the content
        self.assertIn('Answer!', result)


if __name__ == '__main__':
    unittest.main()
