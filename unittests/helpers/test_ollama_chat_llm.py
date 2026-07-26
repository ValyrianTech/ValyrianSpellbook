#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
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

    @patch('helpers.ollama_chat_llm.requests.post')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_get_completion_text_error(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_post):
        """Test get_completion_text handles errors"""
        import requests as req_module
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        mock_post.side_effect = req_module.exceptions.RequestException("Connection Error")
        
        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
        messages = [{'role': 'user', 'content': 'Hello'}]
        
        result = llm.get_completion_text(messages)
        
        self.assertIn('Error', result[0])

    @patch('helpers.ollama_chat_llm.requests.post')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_get_completion_text_success(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_post):
        """Test successful completion"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        # Build Ollama native API streaming response lines
        lines = [
            json.dumps({'message': {'content': 'Hello!', 'thinking': ''}, 'done': False}).encode('utf-8'),
            json.dumps({'done': True, 'prompt_eval_count': 10, 'eval_count': 5}).encode('utf-8'),
        ]
        
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(lines)
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_post.return_value.__exit__ = MagicMock(return_value=False)
        
        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)
        
        self.assertEqual(result, 'Hello!')
        self.assertEqual(usage['prompt_tokens'], 10)


    @patch('helpers.ollama_chat_llm.requests.post')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_get_completion_text_with_reasoning(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_post):
        """Test completion with reasoning content"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        # Build Ollama native API streaming response lines with thinking content
        lines = [
            json.dumps({'message': {'content': '', 'thinking': 'Let me think...'}, 'done': False}).encode('utf-8'),
            json.dumps({'message': {'content': 'The answer is 42', 'thinking': ''}, 'done': False}).encode('utf-8'),
            json.dumps({'done': True, 'prompt_eval_count': 10, 'eval_count': 5}).encode('utf-8'),
        ]
        
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(lines)
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_post.return_value.__exit__ = MagicMock(return_value=False)
        
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

    @patch('helpers.ollama_chat_llm.requests.post')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_get_completion_text_multimodal(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_post):
        """Test completion with multimodal messages"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        lines = [
            json.dumps({'message': {'content': 'I see an image', 'thinking': ''}, 'done': False}).encode('utf-8'),
            json.dumps({'done': True, 'prompt_eval_count': 10, 'eval_count': 5}).encode('utf-8'),
        ]
        
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(lines)
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_post.return_value.__exit__ = MagicMock(return_value=False)
        
        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        # Test with multimodal content
        messages = [{'role': 'user', 'content': [{'text': 'Describe this'}, {'image_url': 'data:image/jpeg;base64,...'}]}]
        result, usage = llm.get_completion_text(messages)
        
        self.assertEqual(result, 'I see an image')

    @patch('helpers.ollama_chat_llm.requests.post')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    @patch('helpers.ollama_chat_llm.LLMInterface.check_stop_generation', return_value=True)
    def test_get_completion_text_stop_generation(self, mock_stop, mock_log, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_post):
        """Test completion stops when stop file is detected"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        lines = [
            json.dumps({'message': {'content': 'Hello', 'thinking': ''}, 'done': False}).encode('utf-8'),
        ]
        
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(lines)
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_post.return_value.__exit__ = MagicMock(return_value=False)
        
        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)
        
        # Should have stopped early
        self.assertEqual(result, '')

    @patch('helpers.ollama_chat_llm.requests.post')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_get_completion_text_reasoning_on_delta(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_post):
        """Test completion with reasoning content via message.thinking"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        lines = [
            json.dumps({'message': {'content': '', 'thinking': 'Thinking via message.thinking...'}, 'done': False}).encode('utf-8'),
            json.dumps({'done': True, 'prompt_eval_count': 10, 'eval_count': 5}).encode('utf-8'),
        ]
        
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(lines)
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_post.return_value.__exit__ = MagicMock(return_value=False)
        
        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)
        
        self.assertIn('think', result)

    @patch('helpers.ollama_chat_llm.requests.post')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_get_completion_text_reasoning_on_message(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_post):
        """Test completion with reasoning content via message.thinking"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        lines = [
            json.dumps({'message': {'content': '', 'thinking': 'Thinking via message.thinking...'}, 'done': False}).encode('utf-8'),
            json.dumps({'done': True, 'prompt_eval_count': 10, 'eval_count': 5}).encode('utf-8'),
        ]
        
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(lines)
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_post.return_value.__exit__ = MagicMock(return_value=False)
        
        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)
        
        self.assertIn('think', result)

    @patch('helpers.ollama_chat_llm.requests.post')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_get_completion_text_reasoning_on_choice(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_post):
        """Test completion with reasoning content via message.thinking"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        lines = [
            json.dumps({'message': {'content': '', 'thinking': 'Thinking via message.thinking...'}, 'done': False}).encode('utf-8'),
            json.dumps({'done': True, 'prompt_eval_count': 10, 'eval_count': 5}).encode('utf-8'),
        ]
        
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(lines)
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_post.return_value.__exit__ = MagicMock(return_value=False)
        
        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)
        
        self.assertIn('think', result)

    @patch('helpers.ollama_chat_llm.requests.post')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_get_completion_text_reasoning_on_message_reasoning(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_post):
        """Test completion with reasoning content via message.thinking"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        lines = [
            json.dumps({'message': {'content': '', 'thinking': 'Thinking via message.thinking...'}, 'done': False}).encode('utf-8'),
            json.dumps({'done': True, 'prompt_eval_count': 10, 'eval_count': 5}).encode('utf-8'),
        ]
        
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(lines)
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_post.return_value.__exit__ = MagicMock(return_value=False)
        
        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)
        
        self.assertIn('think', result)
        self.assertIn('message.thinking', result)

    @patch('helpers.ollama_chat_llm.requests.post')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_get_completion_text_reasoning_on_choice_reasoning(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_post):
        """Test completion with reasoning content via message.thinking"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        lines = [
            json.dumps({'message': {'content': '', 'thinking': 'Thinking via message.thinking...'}, 'done': False}).encode('utf-8'),
            json.dumps({'done': True, 'prompt_eval_count': 10, 'eval_count': 5}).encode('utf-8'),
        ]
        
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(lines)
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_post.return_value.__exit__ = MagicMock(return_value=False)
        
        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)
        
        self.assertIn('think', result)
        self.assertIn('message.thinking', result)


class TestOllamaChatLLMAdvanced(unittest.TestCase):
    """Advanced tests for uncovered ollama_chat_llm paths"""

    @patch('helpers.ollama_chat_llm.requests.post')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_stop_sequences(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_post):
        """Test that stop sequences are passed in options"""
        from helpers.ollama_chat_llm import OllamaChatLLM

        lines = [
            json.dumps({'message': {'content': 'Hello!', 'thinking': ''}, 'done': False}).encode('utf-8'),
            json.dumps({'done': True, 'prompt_eval_count': 10, 'eval_count': 5}).encode('utf-8'),
        ]

        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(lines)
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_post.return_value.__exit__ = MagicMock(return_value=False)

        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, stop=['END'], temperature=0.5, max_tokens=100)

        call_kwargs = mock_post.call_args[1]
        self.assertEqual(call_kwargs['json']['options']['stop'], ['END'])
        self.assertEqual(call_kwargs['json']['options']['temperature'], 0.5)
        self.assertEqual(call_kwargs['json']['options']['num_predict'], 100)

    @patch('helpers.ollama_chat_llm.requests.post')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_empty_lines_skipped(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_post):
        """Test that empty lines in response are skipped"""
        from helpers.ollama_chat_llm import OllamaChatLLM

        lines = [
            b'',
            json.dumps({'message': {'content': 'Hello!', 'thinking': ''}, 'done': False}).encode('utf-8'),
            b'',
            json.dumps({'done': True, 'prompt_eval_count': 10, 'eval_count': 5}).encode('utf-8'),
        ]

        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(lines)
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_post.return_value.__exit__ = MagicMock(return_value=False)

        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)

        self.assertEqual(result, 'Hello!')

    @patch('helpers.ollama_chat_llm.requests.post')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_json_decode_error_skipped(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_post):
        """Test that invalid JSON lines are skipped"""
        from helpers.ollama_chat_llm import OllamaChatLLM

        lines = [
            b'invalid json',
            json.dumps({'message': {'content': 'Hello!', 'thinking': ''}, 'done': False}).encode('utf-8'),
            json.dumps({'done': True, 'prompt_eval_count': 10, 'eval_count': 5}).encode('utf-8'),
        ]

        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(lines)
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_post.return_value.__exit__ = MagicMock(return_value=False)

        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)

        self.assertEqual(result, 'Hello!')

    @patch('helpers.ollama_chat_llm.requests.post')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_inline_think_tags_in_content(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_post):
        """Test handling of inline think tags in content"""
        from helpers.ollama_chat_llm import OllamaChatLLM

        lines = [
            json.dumps({'message': {'content': '\x3cthink\x3eThinking about this', 'thinking': ''}, 'done': False}).encode('utf-8'),
            json.dumps({'message': {'content': ' more thinking\x3c/think\x3e', 'thinking': ''}, 'done': False}).encode('utf-8'),
            json.dumps({'message': {'content': 'Final answer!', 'thinking': ''}, 'done': False}).encode('utf-8'),
            json.dumps({'done': True, 'prompt_eval_count': 10, 'eval_count': 5}).encode('utf-8'),
        ]

        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(lines)
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_post.return_value.__exit__ = MagicMock(return_value=False)

        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)

        self.assertIn('Final answer!', result)

    @patch('helpers.ollama_chat_llm.requests.post')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_no_usage_info(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_post):
        """Test completion when no usage info is provided"""
        from helpers.ollama_chat_llm import OllamaChatLLM

        lines = [
            json.dumps({'message': {'content': 'Hello!', 'thinking': ''}, 'done': False}).encode('utf-8'),
            json.dumps({'done': True}).encode('utf-8'),
        ]

        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(lines)
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_post.return_value.__exit__ = MagicMock(return_value=False)

        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)

        self.assertEqual(usage['prompt_tokens'], 0)
        self.assertEqual(usage['completion_tokens'], 0)

    @patch('helpers.ollama_chat_llm.requests.post')
    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.ollama_chat_llm.broadcast_message')
    @patch('helpers.ollama_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.ollama_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.ollama_chat_llm.LOG')
    def test_get_completion_text_with_thinking_level(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_ws, mock_post):
        """Test completion with thinking_level - covering lines 54-55"""
        from helpers.ollama_chat_llm import OllamaChatLLM
        
        lines = [
            json.dumps({'message': {'content': 'Hello!', 'thinking': ''}, 'done': False}).encode('utf-8'),
            json.dumps({'done': True, 'prompt_eval_count': 10, 'eval_count': 5}).encode('utf-8'),
        ]
        
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(lines)
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_post.return_value.__exit__ = MagicMock(return_value=False)
        
        llm = OllamaChatLLM(model_name='llama2', host='http://localhost', port=11434)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, thinking_level='high')
        
        mock_log.info.assert_any_call('Thinking level: high -> Ollama think: high')


if __name__ == '__main__':
    unittest.main()
