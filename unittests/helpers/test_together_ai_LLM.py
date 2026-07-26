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
        mock_chunk.choices[0].delta.reasoning = None
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


    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.together_ai_LLM.Together')
    @patch('helpers.together_ai_LLM.broadcast_message')
    @patch('helpers.together_ai_LLM.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.together_ai_LLM.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.together_ai_LLM.get_together_ai_bearer_token', return_value='test-token')
    @patch('helpers.together_ai_LLM.LOG')
    @patch('helpers.together_ai_LLM.LLMInterface.check_stop_generation', return_value=True)
    def test_get_completion_text_stop_generation(self, mock_stop, mock_log, mock_get_token, mock_sender, mock_channel, mock_broadcast, mock_together, mock_ws):
        """Test completion stops when stop file is detected"""
        from helpers.together_ai_LLM import TogetherAILLM
        
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = 'Hello'
        mock_chunk.usage = None
        
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
        
        # Should have stopped early
        self.assertEqual(result, '')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.together_ai_LLM.Together')
    @patch('helpers.together_ai_LLM.broadcast_message')
    @patch('helpers.together_ai_LLM.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.together_ai_LLM.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.together_ai_LLM.get_together_ai_bearer_token', return_value='test-token')
    @patch('helpers.together_ai_LLM.LOG')
    def test_get_completion_text_empty_choices(self, mock_log, mock_get_token, mock_sender, mock_channel, mock_broadcast, mock_together, mock_ws):
        """Test completion handles empty choices"""
        from helpers.together_ai_LLM import TogetherAILLM
        
        mock_chunk = MagicMock()
        mock_chunk.choices = []
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
        
        self.assertEqual(result, '')
        self.assertEqual(usage['prompt_tokens'], 10)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.together_ai_LLM.Together')
    @patch('helpers.together_ai_LLM.broadcast_message')
    @patch('helpers.together_ai_LLM.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.together_ai_LLM.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.together_ai_LLM.get_together_ai_bearer_token', return_value='test-token')
    @patch('helpers.together_ai_LLM.LOG')
    def test_get_completion_text_with_stop_sequences(self, mock_log, mock_get_token, mock_sender, mock_channel, mock_broadcast, mock_together, mock_ws):
        """Test completion with stop sequences - covering line 48"""
        from helpers.together_ai_LLM import TogetherAILLM
        
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
        mock_together.return_value = mock_client
        
        llm = TogetherAILLM(model_name='mistralai/Mixtral-8x7B', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, stop=['\n', 'END'])
        
        self.assertEqual(result, 'Hello!')
        # Verify stop was passed to the API
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs['stop'], ['\n', 'END'])

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.together_ai_LLM.Together')
    @patch('helpers.together_ai_LLM.broadcast_message')
    @patch('helpers.together_ai_LLM.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.together_ai_LLM.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.together_ai_LLM.get_together_ai_bearer_token', return_value='test-token')
    @patch('helpers.together_ai_LLM.LOG')
    def test_get_completion_text_with_extra_kwargs(self, mock_log, mock_get_token, mock_sender, mock_channel, mock_broadcast, mock_together, mock_ws):
        """Test completion with extra kwargs - covering lines 53-54"""
        from helpers.together_ai_LLM import TogetherAILLM
        
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
        mock_together.return_value = mock_client
        
        llm = TogetherAILLM(model_name='mistralai/Mixtral-8x7B', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, top_p=0.9, presence_penalty=0.5)
        
        self.assertEqual(result, 'Hello!')
        # Verify extra kwargs were passed
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs['top_p'], 0.9)
        self.assertEqual(call_kwargs['presence_penalty'], 0.5)


class TestTogetherAILLMAdvanced(unittest.TestCase):
    """Advanced tests covering reasoning content, inline think tags, and thinking_level"""

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.together_ai_LLM.Together')
    @patch('helpers.together_ai_LLM.broadcast_message')
    @patch('helpers.together_ai_LLM.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.together_ai_LLM.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.together_ai_LLM.get_together_ai_bearer_token', return_value='test-token')
    @patch('helpers.together_ai_LLM.LOG')
    def test_thinking_level_mapped(self, mock_log, mock_get_token, mock_sender, mock_channel, mock_broadcast, mock_together, mock_ws):
        """Test thinking_level is mapped to reasoning_effort"""
        from helpers.together_ai_LLM import TogetherAILLM

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = 'Hello!'
        mock_chunk.choices[0].delta.reasoning = None
        mock_chunk.usage = None

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk])
        mock_together.return_value = mock_client

        llm = TogetherAILLM(model_name='mistralai/Mixtral-8x7B', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, thinking_level='medium')

        call_kwargs = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs['reasoning_effort'], 'medium')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.together_ai_LLM.Together')
    @patch('helpers.together_ai_LLM.broadcast_message')
    @patch('helpers.together_ai_LLM.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.together_ai_LLM.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.together_ai_LLM.get_together_ai_bearer_token', return_value='test-token')
    @patch('helpers.together_ai_LLM.LOG')
    def test_thinking_level_invalid(self, mock_log, mock_get_token, mock_sender, mock_channel, mock_broadcast, mock_together, mock_ws):
        """Test invalid thinking_level is logged but not mapped"""
        from helpers.together_ai_LLM import TogetherAILLM

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = 'Hello!'
        mock_chunk.choices[0].delta.reasoning = None
        mock_chunk.usage = None

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk])
        mock_together.return_value = mock_client

        llm = TogetherAILLM(model_name='mistralai/Mixtral-8x7B', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, thinking_level='invalid_level')

        call_kwargs = mock_client.chat.completions.create.call_args[1]
        self.assertNotIn('reasoning_effort', call_kwargs)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.together_ai_LLM.Together')
    @patch('helpers.together_ai_LLM.broadcast_message')
    @patch('helpers.together_ai_LLM.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.together_ai_LLM.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.together_ai_LLM.get_together_ai_bearer_token', return_value='test-token')
    @patch('helpers.together_ai_LLM.LOG')
    def test_reasoning_content(self, mock_log, mock_get_token, mock_sender, mock_channel, mock_broadcast, mock_together, mock_ws):
        """Test handling of reasoning content from delta.reasoning"""
        from helpers.together_ai_LLM import TogetherAILLM

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.reasoning = 'Thinking deeply...'
        mock_chunk.choices[0].delta.content = None
        mock_chunk.usage = None

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

        self.assertIn('Thinking deeply...', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.together_ai_LLM.Together')
    @patch('helpers.together_ai_LLM.broadcast_message')
    @patch('helpers.together_ai_LLM.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.together_ai_LLM.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.together_ai_LLM.get_together_ai_bearer_token', return_value='test-token')
    @patch('helpers.together_ai_LLM.LOG')
    def test_inline_think_tags(self, mock_log, mock_get_token, mock_sender, mock_channel, mock_broadcast, mock_together, mock_ws):
        """Test handling of inline think tags in content"""
        from helpers.together_ai_LLM import TogetherAILLM

        chunk1 = MagicMock()
        chunk1.choices = [MagicMock()]
        chunk1.choices[0].delta.content = '<think>Thinking about this'
        chunk1.choices[0].delta.reasoning = None
        chunk1.usage = None

        chunk2 = MagicMock()
        chunk2.choices = [MagicMock()]
        chunk2.choices[0].delta.content = ' more thinking</think>'
        chunk2.choices[0].delta.reasoning = None
        chunk2.usage = None

        chunk3 = MagicMock()
        chunk3.choices = [MagicMock()]
        chunk3.choices[0].delta.content = 'Final answer!'
        chunk3.choices[0].delta.reasoning = None
        chunk3.usage = None

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([chunk1, chunk2, chunk3])
        mock_together.return_value = mock_client

        llm = TogetherAILLM(model_name='mistralai/Mixtral-8x7B', api_key='test-key')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)

        self.assertIn('Final answer!', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.together_ai_LLM.Together')
    @patch('helpers.together_ai_LLM.broadcast_message')
    @patch('helpers.together_ai_LLM.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.together_ai_LLM.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.together_ai_LLM.get_together_ai_bearer_token', return_value='test-token')
    @patch('helpers.together_ai_LLM.LOG')
    def test_no_usage_info(self, mock_log, mock_get_token, mock_sender, mock_channel, mock_broadcast, mock_together, mock_ws):
        """Test completion when no usage info is provided"""
        from helpers.together_ai_LLM import TogetherAILLM

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = 'Hello!'
        mock_chunk.choices[0].delta.reasoning = None
        mock_chunk.usage = None

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

        self.assertEqual(usage['prompt_tokens'], 0)
        self.assertEqual(usage['completion_tokens'], 0)


if __name__ == '__main__':
    unittest.main()
