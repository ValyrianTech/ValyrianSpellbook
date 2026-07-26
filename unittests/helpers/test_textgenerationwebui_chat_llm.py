#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock


class TestTextGenerationWebuiChatLLM(unittest.TestCase):
    """Test cases for helpers/textgenerationwebui_chat_llm.py"""

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_init(self, mock_log, mock_ws):
        """Test TextGenerationWebuiChatLLM initialization"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        llm = TextGenerationWebuiChatLLM(model_name='test-model', host='http://localhost', port=5000)

        self.assertEqual(llm.model_name, 'test-model')
        self.assertEqual(llm.host, 'http://localhost')
        self.assertEqual(llm.port, 5000)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.OpenAI')
    @patch('helpers.textgenerationwebui_chat_llm.broadcast_message')
    @patch('helpers.textgenerationwebui_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.textgenerationwebui_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_get_completion_text_error(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test get_completion_text handles errors"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Connection Error")
        mock_openai.return_value = mock_client

        llm = TextGenerationWebuiChatLLM(model_name='test-model', host='http://localhost', port=5000)
        messages = [{'role': 'user', 'content': 'Hello'}]

        result, usage = llm.get_completion_text(messages)

        self.assertIn('Error', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.OpenAI')
    @patch('helpers.textgenerationwebui_chat_llm.broadcast_message')
    @patch('helpers.textgenerationwebui_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.textgenerationwebui_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_get_completion_text_success(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test successful completion"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = 'Hello!'
        mock_chunk.usage = MagicMock()
        mock_chunk.usage.prompt_tokens = 10
        mock_chunk.usage.completion_tokens = 5
        mock_chunk.usage.total_tokens = 15

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk])
        mock_openai.return_value = mock_client

        llm = TextGenerationWebuiChatLLM(model_name='test-model', host='http://localhost', port=5000)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)

        self.assertEqual(result, 'Hello!')
        self.assertEqual(usage['prompt_tokens'], 10)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.OpenAI')
    @patch('helpers.textgenerationwebui_chat_llm.broadcast_message')
    @patch('helpers.textgenerationwebui_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.textgenerationwebui_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    @patch('helpers.textgenerationwebui_chat_llm.LLMInterface.check_stop_generation', return_value=True)
    def test_get_completion_text_stop_generation(self, mock_stop, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion stops when stop file is detected"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = 'Hello'
        mock_chunk.usage = None

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk])
        mock_openai.return_value = mock_client

        llm = TextGenerationWebuiChatLLM(model_name='test-model', host='http://localhost', port=5000)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)

        self.assertEqual(result, '')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.OpenAI')
    @patch('helpers.textgenerationwebui_chat_llm.broadcast_message')
    @patch('helpers.textgenerationwebui_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.textgenerationwebui_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_get_completion_text_with_thinking_level(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion with thinking_level parameter"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = 'Hello!'
        mock_chunk.usage = MagicMock()
        mock_chunk.usage.prompt_tokens = 10
        mock_chunk.usage.completion_tokens = 5
        mock_chunk.usage.total_tokens = 15

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk])
        mock_openai.return_value = mock_client

        llm = TextGenerationWebuiChatLLM(model_name='gpt-oss-120b', host='http://localhost', port=5000)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, thinking_level='high')

        self.assertEqual(result, 'Hello!')
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs['reasoning_effort'], 'high')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.OpenAI')
    @patch('helpers.textgenerationwebui_chat_llm.broadcast_message')
    @patch('helpers.textgenerationwebui_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.textgenerationwebui_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_get_completion_text_empty_choices(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion with usage-only chunk (empty choices)"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        mock_chunk_usage = MagicMock()
        mock_chunk_usage.choices = []
        mock_chunk_usage.usage = MagicMock()
        mock_chunk_usage.usage.prompt_tokens = 10
        mock_chunk_usage.usage.completion_tokens = 5
        mock_chunk_usage.usage.total_tokens = 15

        mock_chunk_content = MagicMock()
        mock_chunk_content.choices = [MagicMock()]
        mock_chunk_content.choices[0].delta.content = 'Hello!'
        mock_chunk_content.usage = None

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk_usage, mock_chunk_content])
        mock_openai.return_value = mock_client

        llm = TextGenerationWebuiChatLLM(model_name='test-model', host='http://localhost', port=5000)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)

        self.assertEqual(result, 'Hello!')
        self.assertEqual(usage['prompt_tokens'], 10)


class TestExtractThinkingContentRealtime(unittest.TestCase):
    """Test cases for _extract_thinking_content_realtime method"""

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_plain_text(self, mock_log, mock_ws):
        """Test with plain text (no special format)"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        llm = TextGenerationWebuiChatLLM(model_name='test', host='http://localhost', port=5000)
        reasoning, final = llm._extract_thinking_content_realtime("Just plain text")

        self.assertEqual(reasoning, '')
        self.assertEqual(final, '')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_deepseek_r1_complete(self, mock_log, mock_ws):
        """Test with complete DeepSeek R1 style"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        llm = TextGenerationWebuiChatLLM(model_name='test', host='http://localhost', port=5000)
        raw = "<think>Thinking about this...</think>The answer is 42"
        reasoning, final = llm._extract_thinking_content_realtime(raw)

        self.assertIn('Thinking about this', reasoning)
        self.assertIn('The answer is 42', final)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_deepseek_r1_incomplete(self, mock_log, mock_ws):
        """Test with incomplete DeepSeek R1 style (still thinking)"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        llm = TextGenerationWebuiChatLLM(model_name='test', host='http://localhost', port=5000)
        raw = "<think>Thinking about this..."
        reasoning, final = llm._extract_thinking_content_realtime(raw)

        self.assertIn('Thinking about this', reasoning)
        self.assertEqual(final, '')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_gpt_oss_complete(self, mock_log, mock_ws):
        """Test with complete GPT-OSS style"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        llm = TextGenerationWebuiChatLLM(model_name='test', host='http://localhost', port=5000)
        raw = "<|channel|>analysis<|message|>Let me think<|end|><|start|>assistant<|channel|>final<|message|>The answer"
        reasoning, final = llm._extract_thinking_content_realtime(raw)

        self.assertIn('Let me think', reasoning)
        self.assertIn('The answer', final)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_gpt_oss_incomplete(self, mock_log, mock_ws):
        """Test with incomplete GPT-OSS style (still in analysis)"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        llm = TextGenerationWebuiChatLLM(model_name='test', host='http://localhost', port=5000)
        raw = "<|channel|>analysis<|message|>Let me think..."
        reasoning, final = llm._extract_thinking_content_realtime(raw)

        self.assertIn('Let me think', reasoning)
        self.assertEqual(final, '')


class TestExtractThinkingContent(unittest.TestCase):
    """Test cases for _extract_thinking_content method"""

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_plain_text(self, mock_log, mock_ws):
        """Test with plain text (no special format)"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        llm = TextGenerationWebuiChatLLM(model_name='test', host='http://localhost', port=5000)
        result = llm._extract_thinking_content("Just plain text")

        self.assertEqual(result, "Just plain text")

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_deepseek_r1_with_final(self, mock_log, mock_ws):
        """Test DeepSeek R1 style with final content"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        llm = TextGenerationWebuiChatLLM(model_name='test', host='http://localhost', port=5000)
        raw = "<think>Thinking...</think>The answer is 42"
        result = llm._extract_thinking_content(raw)

        self.assertIn('Thinking', result)
        self.assertIn('The answer is 42', result)
        self.assertIn('</think>', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_deepseek_r1_no_final(self, mock_log, mock_ws):
        """Test DeepSeek R1 style without final content"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        llm = TextGenerationWebuiChatLLM(model_name='test', host='http://localhost', port=5000)
        raw = "<think>Thinking...</think>"
        result = llm._extract_thinking_content(raw)

        self.assertIn('Thinking', result)
        self.assertIn('</think>', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_gpt_oss_with_both(self, mock_log, mock_ws):
        """Test GPT-OSS style with both reasoning and final"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        llm = TextGenerationWebuiChatLLM(model_name='test', host='http://localhost', port=5000)
        raw = "<|channel|>analysis<|message|>Let me think<|end|><|start|>assistant<|channel|>final<|message|>The answer"
        result = llm._extract_thinking_content(raw)

        self.assertIn('Let me think', result)
        self.assertIn('The answer', result)
        self.assertIn('', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_gpt_oss_final_only(self, mock_log, mock_ws):
        """Test GPT-OSS style with only final content"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        llm = TextGenerationWebuiChatLLM(model_name='test', host='http://localhost', port=5000)
        raw = "<|channel|>final<|message|>The answer"
        result = llm._extract_thinking_content(raw)

        self.assertEqual(result, 'The answer')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_gpt_oss_reasoning_only(self, mock_log, mock_ws):
        """Test GPT-OSS style with only reasoning content"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        llm = TextGenerationWebuiChatLLM(model_name='test', host='http://localhost', port=5000)
        raw = "<|channel|>analysis<|message|>Just thinking<|end|>"
        result = llm._extract_thinking_content(raw)

        self.assertIn('Just thinking', result)
        self.assertIn('', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.OpenAI')
    @patch('helpers.textgenerationwebui_chat_llm.broadcast_message')
    @patch('helpers.textgenerationwebui_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.textgenerationwebui_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_get_completion_text_thinking_level_off(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test completion with thinking_level='off' - covers line 46"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = 'Hello!'
        mock_chunk.usage = MagicMock()
        mock_chunk.usage.prompt_tokens = 10
        mock_chunk.usage.completion_tokens = 5
        mock_chunk.usage.total_tokens = 15

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([mock_chunk])
        mock_openai.return_value = mock_client

        llm = TextGenerationWebuiChatLLM(model_name='test-model', host='http://localhost', port=5000)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages, thinking_level='off')

        self.assertEqual(result, 'Hello!')
        mock_log.info.assert_any_call('Thinking level: off -> Disabled (no reasoning_effort)')

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.OpenAI')
    @patch('helpers.textgenerationwebui_chat_llm.broadcast_message')
    @patch('helpers.textgenerationwebui_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.textgenerationwebui_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_get_completion_text_reasoning_and_final(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test streaming with both reasoning and final content - covers line 88"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.content = '<|channel|>analysis<|message|>Just thinking<|end|><|start|>assistant<|channel|>final<|message|>The answer'
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

        llm = TextGenerationWebuiChatLLM(model_name='gpt-oss-120b', host='http://localhost', port=5000)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)

        self.assertIn('Just thinking', result)
        self.assertIn('The answer', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.OpenAI')
    @patch('helpers.textgenerationwebui_chat_llm.broadcast_message')
    @patch('helpers.textgenerationwebui_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.textgenerationwebui_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_get_completion_text_reasoning_only(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test streaming with only reasoning content (no final yet) - covers line 90"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.content = '<|channel|>analysis<|message|>Still thinking'
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

        llm = TextGenerationWebuiChatLLM(model_name='gpt-oss-120b', host='http://localhost', port=5000)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)

        self.assertIn('Still thinking', result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.textgenerationwebui_chat_llm.OpenAI')
    @patch('helpers.textgenerationwebui_chat_llm.broadcast_message')
    @patch('helpers.textgenerationwebui_chat_llm.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.textgenerationwebui_chat_llm.get_broadcast_sender', return_value='test-sender')
    @patch('helpers.textgenerationwebui_chat_llm.LOG')
    def test_get_completion_text_final_only(self, mock_log, mock_sender, mock_channel, mock_broadcast, mock_openai, mock_ws):
        """Test streaming with only final content (no reasoning) - covers line 92"""
        from helpers.textgenerationwebui_chat_llm import TextGenerationWebuiChatLLM

        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.content = '<|channel|>final<|message|>Just the answer'
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

        llm = TextGenerationWebuiChatLLM(model_name='gpt-oss-120b', host='http://localhost', port=5000)
        llm.prompt_tokens_cost = 0
        llm.completion_tokens_cost = 0
        llm.prompt_tokens_multiplier = 1
        llm.completion_tokens_multiplier = 1

        messages = [{'role': 'user', 'content': 'Hello'}]
        result, usage = llm.get_completion_text(messages)

        self.assertIn('Just the answer', result)


if __name__ == '__main__':
    unittest.main()
