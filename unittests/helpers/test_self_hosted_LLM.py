#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock


class TestSelfHostedLLM(unittest.TestCase):
    """Test cases for helpers/self_hosted_LLM.py"""

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.self_hosted_LLM.get_default_llm_host', return_value='http://localhost:7860')
    @patch('helpers.self_hosted_LLM.LOG')
    def test_init_with_host(self, mock_log, mock_get_host, mock_ws):
        """Test SelfHostedLLM initialization with provided host"""
        from helpers.self_hosted_LLM import SelfHostedLLM
        
        llm = SelfHostedLLM(host='http://myhost', port=8080, model_name='test-model')
        
        self.assertEqual(llm.host, 'http://myhost')
        self.assertEqual(llm.port, 8080)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.self_hosted_LLM.get_default_llm_host', return_value='http://localhost:7860')
    @patch('helpers.self_hosted_LLM.LOG')
    def test_init_without_host(self, mock_log, mock_get_host, mock_ws):
        """Test SelfHostedLLM initialization without host uses default"""
        from helpers.self_hosted_LLM import SelfHostedLLM
        
        llm = SelfHostedLLM(model_name='test-model')
        
        self.assertEqual(llm.host, 'http://localhost:7860')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.self_hosted_LLM.get_default_llm_host', return_value='http://localhost:7860')
    @patch('helpers.self_hosted_LLM.LOG')
    def test_init_mixture_of_experts(self, mock_log, mock_get_host, mock_ws):
        """Test SelfHostedLLM initialization with mixture of experts"""
        from helpers.self_hosted_LLM import SelfHostedLLM
        
        llm = SelfHostedLLM(mixture_of_experts=True, model_name='test-model')
        
        self.assertTrue(llm.mixture_of_experts)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.self_hosted_LLM.requests.post')
    @patch('helpers.self_hosted_LLM.sseclient.SSEClient')
    @patch('helpers.self_hosted_LLM.broadcast_message')
    @patch('helpers.self_hosted_LLM.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.self_hosted_LLM.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.self_hosted_LLM.get_default_llm_host', return_value='http://localhost:7860')
    @patch('helpers.self_hosted_LLM.LOG')
    def test_get_completion_text_error(self, mock_log, mock_get_host, mock_sender, mock_channel, mock_broadcast, mock_sse, mock_post, mock_ws):
        """Test get_completion_text handles errors"""
        from helpers.self_hosted_LLM import SelfHostedLLM
        
        mock_post.side_effect = Exception("Connection Error")
        
        llm = SelfHostedLLM(host='http://localhost', port=7860, model_name='test-model')
        messages = [{'role': 'user', 'content': 'Hello'}]
        
        result = llm.get_completion_text(messages)
        
        self.assertIn('Error', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.self_hosted_LLM.requests.post')
    @patch('helpers.self_hosted_LLM.sseclient.SSEClient')
    @patch('helpers.self_hosted_LLM.broadcast_message')
    @patch('helpers.self_hosted_LLM.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.self_hosted_LLM.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.self_hosted_LLM.get_default_llm_host', return_value='http://localhost:7860')
    @patch('helpers.self_hosted_LLM.LOG')
    def test_get_completion_text_success(self, mock_log, mock_get_host, mock_sender, mock_channel, mock_broadcast, mock_sse, mock_post, mock_ws):
        """Test successful completion"""
        from helpers.self_hosted_LLM import SelfHostedLLM
        
        mock_event = MagicMock()
        mock_event.data = '{"choices": [{"text": "Hello!"}], "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}}'
        
        mock_sse_client = MagicMock()
        mock_sse_client.events.return_value = iter([mock_event])
        mock_sse.return_value = mock_sse_client
        
        llm = SelfHostedLLM(host='http://localhost', port=7860, model_name='test-model')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)
        
        self.assertEqual(result, 'Hello!')
        self.assertEqual(usage['prompt_tokens'], 10)


class TestGetDefaultLLMHost(unittest.TestCase):
    """Test cases for get_default_llm_host function"""

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.self_hosted_LLM.load_llms')
    @patch('helpers.self_hosted_LLM.get_llms_default_model', return_value='self-hosted:test-model')
    @patch('helpers.self_hosted_LLM.LOG')
    def test_get_default_llm_host(self, mock_log, mock_get_default, mock_load_llms, mock_ws):
        """Test get_default_llm_host returns correct host"""
        from helpers.self_hosted_LLM import get_default_llm_host
        
        mock_load_llms.return_value = {'test-model': {'host': 'http://myhost:8080'}}
        
        result = get_default_llm_host()
        
        self.assertEqual(result, 'http://myhost:8080')


    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.self_hosted_LLM.requests.post')
    @patch('helpers.self_hosted_LLM.sseclient.SSEClient')
    @patch('helpers.self_hosted_LLM.broadcast_message')
    @patch('helpers.self_hosted_LLM.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.self_hosted_LLM.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.self_hosted_LLM.get_default_llm_host', return_value='http://localhost:7860')
    @patch('helpers.self_hosted_LLM.LOG')
    def test_get_completion_text_multimodal(self, mock_log, mock_get_host, mock_sender, mock_channel, mock_broadcast, mock_sse, mock_post, mock_ws):
        """Test completion with multimodal messages"""
        from helpers.self_hosted_LLM import SelfHostedLLM
        
        mock_event = MagicMock()
        mock_event.data = '{"choices": [{"text": "I see an image"}], "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}}'
        
        mock_sse_client = MagicMock()
        mock_sse_client.events.return_value = iter([mock_event])
        mock_sse.return_value = mock_sse_client
        
        llm = SelfHostedLLM(host='http://localhost', port=7860, model_name='test-model')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        # Test with multimodal content
        messages = [
            {'role': 'user', 'content': [{'text': 'Describe this'}, {'image_url': 'data:image/jpeg;base64,...'}]}
        ]
        result, usage = llm.get_completion_text(messages)
        
        self.assertEqual(result, 'I see an image')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.self_hosted_LLM.requests.post')
    @patch('helpers.self_hosted_LLM.sseclient.SSEClient')
    @patch('helpers.self_hosted_LLM.broadcast_message')
    @patch('helpers.self_hosted_LLM.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.self_hosted_LLM.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.self_hosted_LLM.get_default_llm_host', return_value='http://localhost:7860')
    @patch('helpers.self_hosted_LLM.LOG')
    def test_get_completion_text_no_port(self, mock_log, mock_get_host, mock_sender, mock_channel, mock_broadcast, mock_sse, mock_post, mock_ws):
        """Test completion without port (uses host only)"""
        from helpers.self_hosted_LLM import SelfHostedLLM
        
        mock_event = MagicMock()
        mock_event.data = '{"choices": [{"text": "Hello!"}], "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}}'
        
        mock_sse_client = MagicMock()
        mock_sse_client.events.return_value = iter([mock_event])
        mock_sse.return_value = mock_sse_client
        
        llm = SelfHostedLLM(host='http://localhost:7860', port=None, model_name='test-model')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)
        
        self.assertEqual(result, 'Hello!')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.self_hosted_LLM.requests.post')
    @patch('helpers.self_hosted_LLM.sseclient.SSEClient')
    @patch('helpers.self_hosted_LLM.broadcast_message')
    @patch('helpers.self_hosted_LLM.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.self_hosted_LLM.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.self_hosted_LLM.get_default_llm_host', return_value='http://localhost:7860')
    @patch('helpers.self_hosted_LLM.LOG')
    @patch('helpers.self_hosted_LLM.LLMInterface.check_stop_generation', return_value=True)
    def test_get_completion_text_stop_generation(self, mock_stop, mock_log, mock_get_host, mock_sender, mock_channel, mock_broadcast, mock_sse, mock_post, mock_ws):
        """Test completion stops when stop file is detected"""
        from helpers.self_hosted_LLM import SelfHostedLLM
        
        mock_event = MagicMock()
        mock_event.data = '{"choices": [{"text": "Hello!"}]}'
        
        mock_sse_client = MagicMock()
        mock_sse_client.events.return_value = iter([mock_event])
        mock_sse.return_value = mock_sse_client
        
        llm = SelfHostedLLM(host='http://localhost', port=7860, model_name='test-model')
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)
        
        # Should have stopped early
        self.assertEqual(result, '')


if __name__ == '__main__':
    unittest.main()
