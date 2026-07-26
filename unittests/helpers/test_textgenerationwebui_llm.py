#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import unittest
from unittest.mock import patch, MagicMock


class TestTextGenerationWebuiLLM(unittest.TestCase):
    """Test cases for helpers/textgenerationwebui_llm.py"""

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_llm.LOG')
    def test_init(self, mock_log, mock_ws):
        """Test TextGenerationWebuiLLM initialization"""
        from helpers.textgenerationwebui_llm import TextGenerationWebuiLLM

        llm = TextGenerationWebuiLLM(model_name='test-model', host='http://localhost', port=5000)

        self.assertEqual(llm.model_name, 'test-model')
        self.assertEqual(llm.host, 'http://localhost')
        self.assertEqual(llm.port, 5000)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_llm.requests.post')
    @patch('helpers.textgenerationwebui_llm.sseclient.SSEClient')
    @patch('helpers.textgenerationwebui_llm.broadcast_message')
    @patch('helpers.textgenerationwebui_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.textgenerationwebui_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.textgenerationwebui_llm.LOG')
    def test_get_completion_text_error(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_sse, mock_post, mock_ws):
        """Test get_completion_text handles errors"""
        from helpers.textgenerationwebui_llm import TextGenerationWebuiLLM

        mock_post.side_effect = Exception("Connection Error")

        llm = TextGenerationWebuiLLM(model_name='test-model', host='http://localhost', port=5000)
        messages = [{'role': 'user', 'content': 'Hello'}]

        result = llm.get_completion_text(messages)

        self.assertIn('Error', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_llm.requests.post')
    @patch('helpers.textgenerationwebui_llm.sseclient.SSEClient')
    @patch('helpers.textgenerationwebui_llm.broadcast_message')
    @patch('helpers.textgenerationwebui_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.textgenerationwebui_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.textgenerationwebui_llm.LOG')
    def test_get_completion_text_success(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_sse, mock_post, mock_ws):
        """Test successful completion"""
        from helpers.textgenerationwebui_llm import TextGenerationWebuiLLM

        mock_event = MagicMock()
        mock_event.data = json.dumps({
            'choices': [{'text': 'Hello!'}],
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        })

        mock_sse_client = MagicMock()
        mock_sse_client.events.return_value = iter([mock_event])
        mock_sse.return_value = mock_sse_client

        llm = TextGenerationWebuiLLM(model_name='test-model', host='http://localhost', port=5000)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)

        self.assertEqual(result, 'Hello!')
        self.assertEqual(usage['prompt_tokens'], 10)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_llm.requests.post')
    @patch('helpers.textgenerationwebui_llm.sseclient.SSEClient')
    @patch('helpers.textgenerationwebui_llm.broadcast_message')
    @patch('helpers.textgenerationwebui_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.textgenerationwebui_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.textgenerationwebui_llm.LOG')
    def test_get_completion_text_multimodal(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_sse, mock_post, mock_ws):
        """Test completion with multimodal messages (list content)"""
        from helpers.textgenerationwebui_llm import TextGenerationWebuiLLM

        mock_event = MagicMock()
        mock_event.data = json.dumps({
            'choices': [{'text': 'I see an image'}],
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        })

        mock_sse_client = MagicMock()
        mock_sse_client.events.return_value = iter([mock_event])
        mock_sse.return_value = mock_sse_client

        llm = TextGenerationWebuiLLM(model_name='test-model', host='http://localhost', port=5000)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [
            {'role': 'user', 'content': [{'type': 'text', 'text': 'Describe this'}, {'type': 'image_url', 'image_url': 'data:image/jpeg;base64,...'}]}
        ]
        result, usage = llm.get_completion_text(messages)

        self.assertEqual(result, 'I see an image')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_llm.requests.post')
    @patch('helpers.textgenerationwebui_llm.sseclient.SSEClient')
    @patch('helpers.textgenerationwebui_llm.broadcast_message')
    @patch('helpers.textgenerationwebui_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.textgenerationwebui_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.textgenerationwebui_llm.LOG')
    @patch('helpers.textgenerationwebui_llm.LLMInterface.check_stop_generation', return_value=True)
    def test_get_completion_text_stop_generation(self, mock_stop, mock_log, mock_sender, mock_channel, mock_broadcast, mock_sse, mock_post, mock_ws):
        """Test completion stops when stop file is detected"""
        from helpers.textgenerationwebui_llm import TextGenerationWebuiLLM

        mock_event = MagicMock()
        mock_event.data = json.dumps({
            'choices': [{'text': 'Hello'}],
            'usage': None
        })

        mock_sse_client = MagicMock()
        mock_sse_client.events.return_value = iter([mock_event])
        mock_sse.return_value = mock_sse_client

        llm = TextGenerationWebuiLLM(model_name='test-model', host='http://localhost', port=5000)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)

        self.assertEqual(result, '')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_llm.requests.post')
    @patch('helpers.textgenerationwebui_llm.sseclient.SSEClient')
    @patch('helpers.textgenerationwebui_llm.broadcast_message')
    @patch('helpers.textgenerationwebui_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.textgenerationwebui_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.textgenerationwebui_llm.LOG')
    def test_get_completion_text_no_port(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_sse, mock_post, mock_ws):
        """Test completion with no port (URL construction)"""
        from helpers.textgenerationwebui_llm import TextGenerationWebuiLLM

        mock_event = MagicMock()
        mock_event.data = json.dumps({
            'choices': [{'text': 'Hello!'}],
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        })

        mock_sse_client = MagicMock()
        mock_sse_client.events.return_value = iter([mock_event])
        mock_sse.return_value = mock_sse_client

        llm = TextGenerationWebuiLLM(model_name='test-model', host='http://localhost', port=None)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)

        self.assertEqual(result, 'Hello!')
        # Verify URL was constructed without port
        called_url = mock_post.call_args[0][0]
        self.assertNotIn(':5000', called_url)
        self.assertIn('/v1/completions', called_url)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_llm.requests.post')
    @patch('helpers.textgenerationwebui_llm.sseclient.SSEClient')
    @patch('helpers.textgenerationwebui_llm.broadcast_message')
    @patch('helpers.textgenerationwebui_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.textgenerationwebui_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.textgenerationwebui_llm.LOG')
    def test_get_completion_text_with_thinking_level_ignored(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_sse, mock_post, mock_ws):
        """Test that thinking_level is ignored (logged but not used)"""
        from helpers.textgenerationwebui_llm import TextGenerationWebuiLLM

        mock_event = MagicMock()
        mock_event.data = json.dumps({
            'choices': [{'text': 'Hello!'}],
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        })

        mock_sse_client = MagicMock()
        mock_sse_client.events.return_value = iter([mock_event])
        mock_sse.return_value = mock_sse_client

        llm = TextGenerationWebuiLLM(model_name='test-model', host='http://localhost', port=5000)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, thinking_level='high')

        self.assertEqual(result, 'Hello!')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_llm.requests.post')
    @patch('helpers.textgenerationwebui_llm.sseclient.SSEClient')
    @patch('helpers.textgenerationwebui_llm.broadcast_message')
    @patch('helpers.textgenerationwebui_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.textgenerationwebui_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.textgenerationwebui_llm.LOG')
    def test_get_completion_text_multiple_messages(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_sse, mock_post, mock_ws):
        """Test completion with multiple messages (non-single-user-string format)"""
        from helpers.textgenerationwebui_llm import TextGenerationWebuiLLM

        mock_event = MagicMock()
        mock_event.data = json.dumps({
            'choices': [{'text': 'Response'}],
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        })

        mock_sse_client = MagicMock()
        mock_sse_client.events.return_value = iter([mock_event])
        mock_sse.return_value = mock_sse_client

        llm = TextGenerationWebuiLLM(model_name='test-model', host='http://localhost', port=5000)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [
            {'role': 'system', 'content': 'You are helpful'},
            {'role': 'user', 'content': 'Hello'}
        ]
        result, usage = llm.get_completion_text(messages)

        self.assertEqual(result, 'Response')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_llm.requests.post')
    @patch('helpers.textgenerationwebui_llm.sseclient.SSEClient')
    @patch('helpers.textgenerationwebui_llm.broadcast_message')
    @patch('helpers.textgenerationwebui_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.textgenerationwebui_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.textgenerationwebui_llm.LOG')
    def test_get_completion_text_no_usage(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_sse, mock_post, mock_ws):
        """Test completion with no usage information in response"""
        from helpers.textgenerationwebui_llm import TextGenerationWebuiLLM

        mock_event = MagicMock()
        mock_event.data = json.dumps({
            'choices': [{'text': 'Hello!'}],
            'usage': None
        })

        mock_sse_client = MagicMock()
        mock_sse_client.events.return_value = iter([mock_event])
        mock_sse.return_value = mock_sse_client

        llm = TextGenerationWebuiLLM(model_name='test-model', host='http://localhost', port=5000)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)

        self.assertEqual(result, 'Hello!')
        self.assertEqual(usage['prompt_tokens'], 0)


if __name__ == '__main__':
    unittest.main()
