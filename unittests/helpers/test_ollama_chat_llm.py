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


    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.OpenAI')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_get_completion_text_with_reasoning(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion with reasoning content"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        # Create mock chunk with reasoning content
        mock_chunk1 = MagicMock()
        mock_choice1 = MagicMock()
        mock_choice1.delta = MagicMock()
        mock_choice1.delta.content = None
        mock_choice1.delta.reasoning_content = 'Let me think...'
        mock_choice1.delta.reasoning = None
        mock_choice1.message = None
        mock_choice1.reasoning_content = None
        mock_choice1.reasoning = None
        mock_chunk1.choices = [mock_choice1]
        mock_chunk1.usage = None
        
        # Create mock chunk with actual content
        mock_chunk2 = MagicMock()
        mock_choice2 = MagicMock()
        mock_choice2.delta = MagicMock()
        mock_choice2.delta.content = 'The answer is 42'
        mock_choice2.delta.reasoning_content = None
        mock_choice2.delta.reasoning = None
        mock_choice2.message = None
        mock_choice2.reasoning_content = None
        mock_choice2.reasoning = None
        mock_chunk2.choices = [mock_choice2]
        mock_chunk2.usage = None
        
        # Create mock chunk with usage (final chunk)
        mock_chunk3 = MagicMock()
        mock_chunk3.choices = []
        mock_chunk3.usage = MagicMock()
        mock_chunk3.usage.prompt_tokens = 10
        mock_chunk3.usage.completion_tokens = 5
        mock_chunk3.usage.total_tokens = 15
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk1, mock_chunk2, mock_chunk3])
        mock_openai.return_value = mock_client
        
        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'What is the meaning of life?'}]
        result, usage = llm.get_completion_text(messages)
        
        # Result should contain both reasoning and answer
        self.assertIn('think', result)
        self.assertIn('The answer is 42', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.OpenAI')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_get_completion_text_multimodal(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion with multimodal messages"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        mock_chunk1 = MagicMock()
        mock_choice = MagicMock()
        mock_choice.delta = MagicMock()
        mock_choice.delta.content = 'I see an image'
        mock_choice.delta.reasoning_content = None
        mock_choice.delta.reasoning = None
        mock_choice.message = None
        mock_choice.reasoning_content = None
        mock_choice.reasoning = None
        mock_chunk1.choices = [mock_choice]
        mock_chunk1.usage = None
        
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
        
        # Test with multimodal content
        messages = [{'role': 'user', 'content': [{'text': 'Describe this'}, {'image_url': 'data:image/jpeg;base64,...'}]}]
        result, usage = llm.get_completion_text(messages)
        
        self.assertEqual(result, 'I see an image')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.OpenAI')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    @patch('helpers.ollama_chat_llm.LLMInterface.check_stop_generation', return_value=True)
    def test_get_completion_text_stop_generation(self, mock_stop, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion stops when stop file is detected"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        mock_chunk = MagicMock()
        mock_choice = MagicMock()
        mock_choice.delta = MagicMock()
        mock_choice.delta.content = 'Hello'
        mock_choice.delta.reasoning_content = None
        mock_choice.delta.reasoning = None
        mock_choice.message = None
        mock_choice.reasoning_content = None
        mock_choice.reasoning = None
        mock_chunk.choices = [mock_choice]
        mock_chunk.usage = None
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk])
        mock_openai.return_value = mock_client
        
        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)
        
        # Should have stopped early
        self.assertEqual(result, '')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.OpenAI')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_get_completion_text_reasoning_on_delta(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion with reasoning on delta.reasoning - covering line 92"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        # Create mock chunk with reasoning on delta.reasoning (not reasoning_content)
        mock_chunk1 = MagicMock()
        mock_choice1 = MagicMock()
        mock_choice1.delta = MagicMock()
        mock_choice1.delta.content = None
        mock_choice1.delta.reasoning_content = None
        mock_choice1.delta.reasoning = 'Thinking via delta.reasoning...'
        mock_choice1.message = None
        mock_choice1.reasoning_content = None
        mock_choice1.reasoning = None
        mock_chunk1.choices = [mock_choice1]
        mock_chunk1.usage = None
        
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
        
        self.assertIn('think', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.OpenAI')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_get_completion_text_reasoning_on_message(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion with reasoning on message - covering lines 96-99"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        # Create mock chunk with reasoning on message.reasoning_content
        mock_chunk1 = MagicMock()
        mock_choice1 = MagicMock()
        mock_choice1.delta = MagicMock()
        mock_choice1.delta.content = None
        mock_choice1.delta.reasoning_content = None
        mock_choice1.delta.reasoning = None
        mock_choice1.message = MagicMock()
        mock_choice1.message.reasoning_content = 'Thinking via message.reasoning_content...'
        mock_choice1.message.reasoning = None
        mock_choice1.reasoning_content = None
        mock_choice1.reasoning = None
        mock_chunk1.choices = [mock_choice1]
        mock_chunk1.usage = None
        
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
        
        self.assertIn('think', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.OpenAI')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_get_completion_text_reasoning_on_choice(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion with reasoning directly on choice - covering lines 103, 105"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        # Create mock chunk with reasoning directly on choice
        mock_chunk1 = MagicMock()
        mock_choice1 = MagicMock()
        mock_choice1.delta = MagicMock()
        mock_choice1.delta.content = None
        mock_choice1.delta.reasoning_content = None
        mock_choice1.delta.reasoning = None
        mock_choice1.message = None
        mock_choice1.reasoning_content = 'Thinking via choice.reasoning_content...'
        mock_choice1.reasoning = None
        mock_chunk1.choices = [mock_choice1]
        mock_chunk1.usage = None
        
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
        
        self.assertIn('think', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.OpenAI')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_get_completion_text_reasoning_on_message_reasoning(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion with reasoning on message.reasoning (not reasoning_content) - covering lines 98-99"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        # Create mock chunk with reasoning on message.reasoning
        mock_chunk1 = MagicMock()
        mock_choice1 = MagicMock()
        mock_choice1.delta = MagicMock()
        mock_choice1.delta.content = None
        mock_choice1.delta.reasoning_content = None
        mock_choice1.delta.reasoning = None
        mock_choice1.message = MagicMock()
        mock_choice1.message.reasoning_content = None
        mock_choice1.message.reasoning = 'Thinking via message.reasoning...'
        mock_choice1.reasoning_content = None
        mock_choice1.reasoning = None
        mock_chunk1.choices = [mock_choice1]
        mock_chunk1.usage = None
        
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
        
        self.assertIn('think', result)
        self.assertIn('message.reasoning', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.OpenAI')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_get_completion_text_reasoning_on_choice_reasoning(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion with reasoning on choice.reasoning (not reasoning_content) - covering line 105"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        # Create mock chunk with reasoning directly on choice.reasoning
        mock_chunk1 = MagicMock()
        mock_choice1 = MagicMock()
        mock_choice1.delta = MagicMock()
        mock_choice1.delta.content = None
        mock_choice1.delta.reasoning_content = None
        mock_choice1.delta.reasoning = None
        mock_choice1.message = None
        mock_choice1.reasoning_content = None
        mock_choice1.reasoning = 'Thinking via choice.reasoning...'
        mock_chunk1.choices = [mock_choice1]
        mock_chunk1.usage = None
        
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
        
        self.assertIn('think', result)
        self.assertIn('choice.reasoning', result)


if __name__ == '__main__':
    unittest.main()
