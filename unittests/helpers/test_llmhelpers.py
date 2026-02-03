#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock


class TestGetLlmApiKey(unittest.TestCase):
    """Test cases for get_llm_api_key function"""

    @patch('helpers.llmhelpers.load_llms')
    @patch('helpers.llmhelpers._ensure_env_file_complete')
    @patch('helpers.llmhelpers.get_app_data_dir', return_value='/tmp/test')
    @patch('helpers.llmhelpers.LOG')
    def test_get_api_key_from_config(self, mock_log, mock_app_dir, mock_ensure, mock_load_llms):
        """Test getting API key from LLM configuration"""
        from helpers.llmhelpers import get_llm_api_key
        
        mock_load_llms.return_value = {
            'OpenAI:gpt-4': {'api_key': 'config-api-key'}
        }
        
        result = get_llm_api_key('OpenAI:gpt-4', 'OpenAI')
        
        self.assertEqual(result, 'config-api-key')

    @patch('helpers.llmhelpers.load_llms')
    @patch('helpers.llmhelpers._ensure_env_file_complete')
    @patch('helpers.llmhelpers.load_dotenv')
    @patch('helpers.llmhelpers.os.getenv', return_value='env-api-key')
    @patch('helpers.llmhelpers.get_app_data_dir', return_value='/tmp/test')
    @patch('helpers.llmhelpers.LOG')
    def test_get_api_key_from_env(self, mock_log, mock_app_dir, mock_getenv, mock_dotenv, mock_ensure, mock_load_llms):
        """Test getting API key from environment when not in config"""
        from helpers.llmhelpers import get_llm_api_key
        
        mock_load_llms.return_value = {}
        
        result = get_llm_api_key('OpenAI:gpt-4', 'OpenAI')
        
        self.assertEqual(result, 'env-api-key')

    @patch('helpers.llmhelpers.load_llms')
    @patch('helpers.llmhelpers._ensure_env_file_complete')
    @patch('helpers.llmhelpers.load_dotenv')
    @patch('helpers.llmhelpers.os.getenv', return_value=None)
    @patch('helpers.llmhelpers.get_app_data_dir', return_value='/tmp/test')
    @patch('helpers.llmhelpers.LOG')
    def test_get_api_key_not_found(self, mock_log, mock_app_dir, mock_getenv, mock_dotenv, mock_ensure, mock_load_llms):
        """Test returns None when API key not found"""
        from helpers.llmhelpers import get_llm_api_key
        
        mock_load_llms.return_value = {}
        
        result = get_llm_api_key('OpenAI:gpt-4', 'OpenAI')
        
        self.assertIsNone(result)

    @patch('helpers.llmhelpers.LOG')
    def test_get_api_key_unknown_server_type(self, mock_log):
        """Test returns None for unknown server type"""
        from helpers.llmhelpers import get_llm_api_key
        
        result = get_llm_api_key('Unknown:model', 'UnknownProvider')
        
        self.assertIsNone(result)


class TestEnsureEnvFileComplete(unittest.TestCase):
    """Test cases for _ensure_env_file_complete function"""

    def test_creates_env_file(self):
        """Test creates .env file if it doesn't exist"""
        from helpers.llmhelpers import _ensure_env_file_complete
        
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = os.path.join(temp_dir, '.env')
            env_mapping = {'OpenAI': 'OPENAI_API_KEY'}
            
            _ensure_env_file_complete(env_path, env_mapping)
            
            self.assertTrue(os.path.exists(env_path))

    def test_adds_missing_vars(self):
        """Test adds missing environment variables"""
        from helpers.llmhelpers import _ensure_env_file_complete
        
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = os.path.join(temp_dir, '.env')
            
            # Create initial file with one var
            with open(env_path, 'w') as f:
                f.write('OPENAI_API_KEY=existing\n')
            
            env_mapping = {
                'OpenAI': 'OPENAI_API_KEY',
                'Anthropic': 'ANTHROPIC_API_KEY'
            }
            
            _ensure_env_file_complete(env_path, env_mapping)
            
            with open(env_path, 'r') as f:
                content = f.read()
            
            self.assertIn('ANTHROPIC_API_KEY', content)


class TestGetRole(unittest.TestCase):
    """Test cases for get_role function"""

    def test_get_role_human(self):
        """Test get_role for HumanMessage"""
        from helpers.llmhelpers import get_role
        from langchain.schema import HumanMessage
        
        msg = HumanMessage(content="test")
        result = get_role(msg)
        
        self.assertEqual(result, 'user: ')

    def test_get_role_ai(self):
        """Test get_role for AIMessage"""
        from helpers.llmhelpers import get_role
        from langchain.schema import AIMessage
        
        msg = AIMessage(content="test")
        result = get_role(msg)
        
        self.assertEqual(result, 'assistant: ')

    def test_get_role_system(self):
        """Test get_role for SystemMessage"""
        from helpers.llmhelpers import get_role
        from langchain.schema import SystemMessage
        
        msg = SystemMessage(content="test")
        result = get_role(msg)
        
        self.assertEqual(result, 'system: ')


class TestLoadLlms(unittest.TestCase):
    """Test cases for load_llms function"""

    @patch('helpers.llmhelpers.load_from_json_file')
    @patch('helpers.llmhelpers.os.path.exists', return_value=True)
    def test_load_llms(self, mock_exists, mock_load_json):
        """Test load_llms loads from JSON file"""
        from helpers.llmhelpers import load_llms
        
        mock_load_json.return_value = {'model1': {'host': 'localhost'}}
        
        result = load_llms()
        
        self.assertEqual(result, {'model1': {'host': 'localhost'}})


class TestGetLlmConfig(unittest.TestCase):
    """Test cases for get_llm_config function"""

    @patch('helpers.llmhelpers.load_llms')
    def test_get_llm_config_exists(self, mock_load_llms):
        """Test get_llm_config returns config when exists"""
        from helpers.llmhelpers import get_llm_config
        
        mock_load_llms.return_value = {'model1': {'host': 'localhost'}}
        
        result = get_llm_config('model1')
        
        self.assertEqual(result, {'host': 'localhost'})

    @patch('helpers.llmhelpers.load_llms')
    def test_get_llm_config_not_exists(self, mock_load_llms):
        """Test get_llm_config returns empty dict when not exists"""
        from helpers.llmhelpers import get_llm_config
        
        mock_load_llms.return_value = {}
        
        result = get_llm_config('nonexistent')
        
        self.assertEqual(result, {})


class TestEncodeImage(unittest.TestCase):
    """Test cases for encode_image function"""

    def test_encode_image(self):
        """Test encode_image returns base64 string"""
        from helpers.llmhelpers import encode_image
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'test image data')
            temp_path = f.name
        
        try:
            result = encode_image(temp_path)
            
            self.assertIsInstance(result, str)
            # Base64 encoded 'test image data'
            import base64
            decoded = base64.b64decode(result)
            self.assertEqual(decoded, b'test image data')
        finally:
            os.unlink(temp_path)


class TestConstructUserMessages(unittest.TestCase):
    """Test cases for construct_user_messages function"""

    def test_construct_text_only(self):
        """Test construct_user_messages with text only"""
        from helpers.llmhelpers import construct_user_messages
        
        result = construct_user_messages("Hello world")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['role'], 'user')
        self.assertEqual(len(result[0]['content']), 1)
        self.assertEqual(result[0]['content'][0]['type'], 'text')

    def test_construct_empty_text(self):
        """Test construct_user_messages with empty text"""
        from helpers.llmhelpers import construct_user_messages
        
        result = construct_user_messages("")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['content'], [])

    @patch('helpers.llmhelpers.os.path.exists', return_value=True)
    @patch('helpers.llmhelpers.encode_image', return_value='base64data')
    def test_construct_with_image(self, mock_encode, mock_exists):
        """Test construct_user_messages with image"""
        from helpers.llmhelpers import construct_user_messages
        
        result = construct_user_messages("Hello", image_paths=['/path/to/image.jpg'])
        
        self.assertEqual(len(result[0]['content']), 2)
        self.assertEqual(result[0]['content'][0]['type'], 'image_url')
        self.assertEqual(result[0]['content'][1]['type'], 'text')

    @patch('helpers.llmhelpers.os.path.exists', return_value=False)
    @patch('helpers.llmhelpers.LOG')
    def test_construct_with_missing_image(self, mock_log, mock_exists):
        """Test construct_user_messages with missing image file"""
        from helpers.llmhelpers import construct_user_messages
        
        result = construct_user_messages("Hello", image_paths=['/path/to/missing.jpg'])
        
        # Should only have text, no image
        self.assertEqual(len(result[0]['content']), 1)
        self.assertEqual(result[0]['content'][0]['type'], 'text')
        mock_log.error.assert_called()


class TestDeleteLlm(unittest.TestCase):
    """Test cases for delete_llm function"""

    @patch('helpers.llmhelpers.save_to_json_file')
    @patch('helpers.llmhelpers.load_llms')
    def test_delete_llm_exists(self, mock_load, mock_save):
        """Test deleting an existing LLM"""
        from helpers.llmhelpers import delete_llm
        
        mock_load.return_value = {'model1': {'host': 'localhost'}, 'model2': {'host': 'remote'}}
        
        delete_llm('model1')
        
        mock_save.assert_called_once()
        saved_data = mock_save.call_args[1]['data']
        self.assertNotIn('model1', saved_data)
        self.assertIn('model2', saved_data)

    @patch('helpers.llmhelpers.save_to_json_file')
    @patch('helpers.llmhelpers.load_llms')
    def test_delete_llm_not_exists(self, mock_load, mock_save):
        """Test deleting a non-existing LLM"""
        from helpers.llmhelpers import delete_llm
        
        mock_load.return_value = {'model1': {'host': 'localhost'}}
        
        delete_llm('nonexistent')
        
        # Should not call save if LLM doesn't exist
        mock_save.assert_not_called()


class TestSaveLlmConfig(unittest.TestCase):
    """Test cases for save_llm_config function"""

    @patch('helpers.llmhelpers.save_to_json_file')
    @patch('helpers.llmhelpers.load_llms')
    def test_save_llm_config_new(self, mock_load, mock_save):
        """Test saving a new LLM config"""
        from helpers.llmhelpers import save_llm_config
        
        mock_load.return_value = {}
        
        config = {'host': 'localhost', 'port': 8080, 'api_key': 'test-key'}
        save_llm_config('new_model', config)
        
        mock_save.assert_called_once()
        saved_data = mock_save.call_args[1]['data']
        self.assertIn('new_model', saved_data)

    @patch('helpers.llmhelpers.save_to_json_file')
    @patch('helpers.llmhelpers.load_llms')
    def test_save_llm_config_masked_api_key(self, mock_load, mock_save):
        """Test saving config with masked API key preserves existing key"""
        from helpers.llmhelpers import save_llm_config
        
        mock_load.return_value = {'model1': {'host': 'localhost', 'api_key': 'real-key'}}
        
        config = {'host': 'localhost', 'api_key': '********'}
        save_llm_config('model1', config)
        
        mock_save.assert_called_once()
        saved_data = mock_save.call_args[1]['data']
        self.assertEqual(saved_data['model1']['api_key'], 'real-key')

    @patch('helpers.llmhelpers.save_to_json_file')
    @patch('helpers.llmhelpers.load_llms')
    def test_save_llm_config_trailing_slash(self, mock_load, mock_save):
        """Test saving config removes trailing slash from host"""
        from helpers.llmhelpers import save_llm_config
        
        mock_load.return_value = {}
        
        config = {'host': 'http://localhost:8080/', 'api_key': 'test'}
        save_llm_config('model1', config)
        
        mock_save.assert_called_once()
        saved_data = mock_save.call_args[1]['data']
        self.assertEqual(saved_data['model1']['host'], 'http://localhost:8080')


class TestSetDefaultLlm(unittest.TestCase):
    """Test cases for set_default_llm function"""

    @patch('builtins.open', unittest.mock.mock_open())
    @patch('helpers.llmhelpers.spellbook_config')
    def test_set_default_llm(self, mock_config):
        """Test setting default LLM"""
        from helpers.llmhelpers import set_default_llm
        
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        
        set_default_llm('gpt-4')
        
        mock_config_instance.set.assert_called_with(section='LLMs', option='default_model', value='gpt-4')


class TestComparisonPrompt(unittest.TestCase):
    """Test cases for comparison_prompt function"""

    def test_comparison_prompt(self):
        """Test comparison_prompt generates correct format"""
        from helpers.llmhelpers import comparison_prompt
        from langchain.schema import HumanMessage
        
        messages = [HumanMessage(content="Test prompt")]
        
        mock_generation = MagicMock()
        mock_generation.generations = [[MagicMock(text="Response 1")]]
        generations = [mock_generation]
        
        result = comparison_prompt(messages, generations)
        
        self.assertIn("Test prompt", result)
        self.assertIn("Response 1", result)
        self.assertIn("best_n", result)


class TestGetRoleUnknown(unittest.TestCase):
    """Test cases for get_role with unknown message types"""

    def test_get_role_chat_message(self):
        """Test get_role for ChatMessage"""
        from helpers.llmhelpers import get_role
        from langchain.schema import ChatMessage
        
        msg = ChatMessage(content="test", role="custom_role")
        result = get_role(msg)
        
        self.assertEqual(result, 'custom_role')

    def test_get_role_unknown_type(self):
        """Test get_role raises for unknown type"""
        from helpers.llmhelpers import get_role
        
        class UnknownMessage:
            content = "test"
        
        with self.assertRaises(Exception) as context:
            get_role(UnknownMessage())
        
        self.assertIn("Unknown message type", str(context.exception))


class TestCustomStreamingCallbackHandler(unittest.TestCase):
    """Test cases for CustomStreamingCallbackHandler"""

    @patch('helpers.llmhelpers.broadcast_message')
    @patch('helpers.llmhelpers.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.llmhelpers.get_broadcast_sender', return_value='test-sender')
    def test_on_llm_start(self, mock_sender, mock_channel, mock_broadcast):
        """Test on_llm_start resets completion"""
        from helpers.llmhelpers import CustomStreamingCallbackHandler
        
        handler = CustomStreamingCallbackHandler()
        handler.full_completion = "previous content"
        
        handler.on_llm_start({}, ["prompt"])
        
        self.assertEqual(handler.full_completion, "")

    @patch('helpers.llmhelpers.broadcast_message')
    @patch('helpers.llmhelpers.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.llmhelpers.get_broadcast_sender', return_value='test-sender')
    def test_on_llm_end(self, mock_sender, mock_channel, mock_broadcast):
        """Test on_llm_end broadcasts end message"""
        from helpers.llmhelpers import CustomStreamingCallbackHandler
        
        handler = CustomStreamingCallbackHandler()
        handler.full_completion = "some content"
        
        mock_response = MagicMock()
        handler.on_llm_end(mock_response)
        
        self.assertEqual(handler.full_completion, "")
        mock_broadcast.assert_called()

    @patch('helpers.llmhelpers.broadcast_message')
    @patch('helpers.llmhelpers.get_broadcast_channel', return_value='test-channel')
    @patch('helpers.llmhelpers.get_broadcast_sender', return_value='test-sender')
    @patch('sys.stdout')
    def test_on_llm_new_token(self, mock_stdout, mock_sender, mock_channel, mock_broadcast):
        """Test on_llm_new_token accumulates tokens"""
        from helpers.llmhelpers import CustomStreamingCallbackHandler
        
        handler = CustomStreamingCallbackHandler()
        
        handler.on_llm_new_token("Hello")
        handler.on_llm_new_token(" World")
        
        self.assertEqual(handler.full_completion, "Hello World")


class TestGetLlm(unittest.TestCase):
    """Test cases for get_llm function"""

    @patch('helpers.llmhelpers.get_llms_default_model', return_value='OpenAI:gpt-4')
    @patch('helpers.llmhelpers.get_llm_api_key', return_value='test-key')
    @patch('helpers.llmhelpers.OpenAILLM')
    @patch('helpers.llmhelpers.LOG')
    def test_get_llm_default_model(self, mock_log, mock_openai_llm, mock_api_key, mock_default):
        """Test get_llm with default_model resolves to configured default"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        mock_llm_instance = MagicMock()
        mock_openai_llm.return_value = mock_llm_instance
        
        result = get_llm('default_model', 0.5)
        
        mock_default.assert_called_once()
        mock_openai_llm.assert_called_once()

    @patch('helpers.llmhelpers.LLMInterface')
    @patch('helpers.llmhelpers.LOG')
    def test_get_llm_auto_routing(self, mock_log, mock_interface):
        """Test get_llm with auto routing"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        mock_llm_instance = MagicMock()
        mock_interface.return_value = mock_llm_instance
        
        result = get_llm('auto', 0.5)
        
        mock_interface.assert_called_once_with(model_name='auto', auto_routing=True)
        self.assertEqual(result, mock_llm_instance)

    @patch('helpers.llmhelpers.get_llm_api_key', return_value='test-key')
    @patch('helpers.llmhelpers.TogetherAILLM')
    @patch('helpers.llmhelpers.LOG')
    def test_get_llm_together_ai(self, mock_log, mock_together, mock_api_key):
        """Test get_llm with Together-ai provider"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        mock_llm_instance = MagicMock()
        mock_together.return_value = mock_llm_instance
        
        result = get_llm('Together-ai:model-name', 0.5)
        
        mock_together.assert_called_once_with(model_name='model-name', api_key='test-key')
        self.assertEqual(result, mock_llm_instance)

    @patch('helpers.llmhelpers.get_llm_api_key', return_value='test-key')
    @patch('helpers.llmhelpers.OpenAILLM')
    @patch('helpers.llmhelpers.LOG')
    def test_get_llm_openai(self, mock_log, mock_openai, mock_api_key):
        """Test get_llm with OpenAI provider"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        mock_llm_instance = MagicMock()
        mock_openai.return_value = mock_llm_instance
        
        result = get_llm('OpenAI:gpt-4', 0.5)
        
        mock_openai.assert_called_once_with(model_name='gpt-4', api_key='test-key')
        self.assertEqual(result, mock_llm_instance)

    @patch('helpers.llmhelpers.get_llm_api_key', return_value='test-key')
    @patch('helpers.llmhelpers.AnthropicLLM')
    @patch('helpers.llmhelpers.LOG')
    def test_get_llm_anthropic(self, mock_log, mock_anthropic, mock_api_key):
        """Test get_llm with Anthropic provider"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        mock_llm_instance = MagicMock()
        mock_anthropic.return_value = mock_llm_instance
        
        result = get_llm('Anthropic:claude-3', 0.5)
        
        mock_anthropic.assert_called_once_with(model_name='claude-3', api_key='test-key')
        self.assertEqual(result, mock_llm_instance)

    @patch('helpers.llmhelpers.get_llm_api_key', return_value='test-key')
    @patch('helpers.llmhelpers.GroqLLM')
    @patch('helpers.llmhelpers.LOG')
    def test_get_llm_groq(self, mock_log, mock_groq, mock_api_key):
        """Test get_llm with Groq provider"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        mock_llm_instance = MagicMock()
        mock_groq.return_value = mock_llm_instance
        
        result = get_llm('Groq:llama-3', 0.5)
        
        mock_groq.assert_called_once_with(model_name='llama-3', api_key='test-key')
        self.assertEqual(result, mock_llm_instance)

    @patch('helpers.llmhelpers.get_llm_api_key', return_value='test-key')
    @patch('helpers.llmhelpers.DeepSeekLLM')
    @patch('helpers.llmhelpers.LOG')
    def test_get_llm_deepseek(self, mock_log, mock_deepseek, mock_api_key):
        """Test get_llm with DeepSeek provider"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        mock_llm_instance = MagicMock()
        mock_deepseek.return_value = mock_llm_instance
        
        result = get_llm('DeepSeek:deepseek-chat', 0.5)
        
        mock_deepseek.assert_called_once_with(model_name='deepseek-chat', api_key='test-key')
        self.assertEqual(result, mock_llm_instance)

    @patch('helpers.llmhelpers.get_llm_api_key', return_value='test-key')
    @patch('helpers.llmhelpers.MistralLLM')
    @patch('helpers.llmhelpers.LOG')
    def test_get_llm_mistral(self, mock_log, mock_mistral, mock_api_key):
        """Test get_llm with Mistral provider"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        mock_llm_instance = MagicMock()
        mock_mistral.return_value = mock_llm_instance
        
        result = get_llm('Mistral:mistral-large', 0.5)
        
        mock_mistral.assert_called_once_with(model_name='mistral-large', api_key='test-key')
        self.assertEqual(result, mock_llm_instance)

    @patch('helpers.llmhelpers.get_llm_api_key', return_value='test-key')
    @patch('helpers.llmhelpers.GoogleLLM')
    @patch('helpers.llmhelpers.LOG')
    def test_get_llm_google(self, mock_log, mock_google, mock_api_key):
        """Test get_llm with Google provider"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        mock_llm_instance = MagicMock()
        mock_google.return_value = mock_llm_instance
        
        result = get_llm('Google:gemini-pro', 0.5)
        
        mock_google.assert_called_once_with(model_name='gemini-pro', api_key='test-key')
        self.assertEqual(result, mock_llm_instance)

    @patch('helpers.llmhelpers.load_from_json_file')
    @patch('helpers.llmhelpers.os.path.exists', return_value=True)
    @patch('helpers.llmhelpers.SelfHostedLLM')
    @patch('helpers.llmhelpers.LOG')
    def test_get_llm_self_hosted_auto(self, mock_log, mock_self_hosted, mock_exists, mock_load_json):
        """Test get_llm with self-hosted:auto"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        mock_load_json.return_value = {}
        mock_llm_instance = MagicMock()
        mock_self_hosted.return_value = mock_llm_instance
        
        result = get_llm('self-hosted:auto', 0.5)
        
        mock_self_hosted.assert_called_once_with(mixture_of_experts=True, model_name='auto')

    @patch('helpers.llmhelpers.load_from_json_file')
    @patch('helpers.llmhelpers.os.path.exists', return_value=True)
    @patch('helpers.llmhelpers.SelfHostedLLM')
    @patch('helpers.llmhelpers.LOG')
    def test_get_llm_self_hosted_oobabooga(self, mock_log, mock_self_hosted, mock_exists, mock_load_json):
        """Test get_llm with self-hosted Oobabooga server"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        mock_load_json.return_value = {
            'test-model': {'host': 'localhost', 'port': 5000, 'server_type': 'Oobabooga'}
        }
        mock_llm_instance = MagicMock()
        mock_self_hosted.return_value = mock_llm_instance
        
        result = get_llm('self-hosted:test-model', 0.5)
        
        mock_self_hosted.assert_called_once_with(host='localhost', port=5000, mixture_of_experts=False, model_name='test-model')

    @patch('helpers.llmhelpers.load_from_json_file')
    @patch('helpers.llmhelpers.os.path.exists', return_value=True)
    @patch('helpers.llmhelpers.OllamaLLM')
    @patch('helpers.llmhelpers.LOG')
    def test_get_llm_self_hosted_ollama(self, mock_log, mock_ollama, mock_exists, mock_load_json):
        """Test get_llm with self-hosted Ollama server"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        mock_load_json.return_value = {
            'test-model': {'host': 'localhost', 'port': 11434, 'server_type': 'Ollama', 'model_name': 'llama2'}
        }
        mock_llm_instance = MagicMock()
        mock_ollama.return_value = mock_llm_instance
        
        result = get_llm('self-hosted:test-model', 0.5)
        
        mock_ollama.assert_called_once_with(model_name='llama2', host='localhost', port=11434)

    @patch('helpers.llmhelpers.load_from_json_file')
    @patch('helpers.llmhelpers.os.path.exists', return_value=True)
    @patch('helpers.llmhelpers.OllamaChatLLM')
    @patch('helpers.llmhelpers.LOG')
    def test_get_llm_self_hosted_ollama_chat(self, mock_log, mock_ollama_chat, mock_exists, mock_load_json):
        """Test get_llm with self-hosted OllamaChat server"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        mock_load_json.return_value = {
            'test-model': {'host': 'localhost', 'port': 11434, 'server_type': 'OllamaChat', 'model_name': 'llama2'}
        }
        mock_llm_instance = MagicMock()
        mock_ollama_chat.return_value = mock_llm_instance
        
        result = get_llm('self-hosted:test-model', 0.5)
        
        mock_ollama_chat.assert_called_once_with(model_name='llama2', host='localhost', port=11434)

    @patch('helpers.llmhelpers.load_from_json_file')
    @patch('helpers.llmhelpers.os.path.exists', return_value=True)
    @patch('helpers.llmhelpers.VLLMLLM')
    @patch('helpers.llmhelpers.LOG')
    def test_get_llm_self_hosted_vllm(self, mock_log, mock_vllm, mock_exists, mock_load_json):
        """Test get_llm with self-hosted vLLM server"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        mock_load_json.return_value = {
            'test-model': {'host': 'localhost', 'port': 8000, 'server_type': 'vLLM', 'model_name': 'mistral'}
        }
        mock_llm_instance = MagicMock()
        mock_vllm.return_value = mock_llm_instance
        
        result = get_llm('self-hosted:test-model', 0.5)
        
        mock_vllm.assert_called_once_with(model_name='mistral', host='localhost', port=8000)

    @patch('helpers.llmhelpers.load_from_json_file')
    @patch('helpers.llmhelpers.os.path.exists', return_value=True)
    @patch('helpers.llmhelpers.VLLMchatLLM')
    @patch('helpers.llmhelpers.LOG')
    def test_get_llm_self_hosted_vllm_chat(self, mock_log, mock_vllm_chat, mock_exists, mock_load_json):
        """Test get_llm with self-hosted vLLMchat server"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        mock_load_json.return_value = {
            'test-model': {'host': 'localhost', 'port': 8000, 'server_type': 'vLLMchat', 'model_name': 'mistral'}
        }
        mock_llm_instance = MagicMock()
        mock_vllm_chat.return_value = mock_llm_instance
        
        result = get_llm('self-hosted:test-model', 0.5)
        
        mock_vllm_chat.assert_called_once_with(model_name='mistral', host='localhost', port=8000)

    @patch('helpers.llmhelpers.load_from_json_file')
    @patch('helpers.llmhelpers.os.path.exists', return_value=True)
    @patch('helpers.llmhelpers.SelfHostedLLM')
    @patch('helpers.llmhelpers.LOG')
    def test_get_llm_self_hosted_unknown_model(self, mock_log, mock_self_hosted, mock_exists, mock_load_json):
        """Test get_llm with self-hosted unknown model falls back to default"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        mock_load_json.return_value = {}
        mock_llm_instance = MagicMock()
        mock_self_hosted.return_value = mock_llm_instance
        
        result = get_llm('self-hosted:unknown-model', 0.5)
        
        mock_self_hosted.assert_called_once_with(mixture_of_experts=False, model_name='unknown-model')

    def test_get_llm_cached(self):
        """Test get_llm returns cached client"""
        from helpers.llmhelpers import get_llm, CLIENTS
        
        mock_llm = MagicMock()
        CLIENTS['cached-model'] = mock_llm
        
        result = get_llm('cached-model', 0.7)
        
        self.assertEqual(result, mock_llm)
        self.assertEqual(mock_llm.temperature, 0.7)
        
        # Cleanup
        del CLIENTS['cached-model']

    @patch('helpers.llmhelpers.get_enable_openai', return_value=True)
    @patch('helpers.llmhelpers.get_openai_api_key', return_value='test-key')
    @patch('helpers.llmhelpers.load_from_json_file', return_value={})
    @patch('helpers.llmhelpers.os.path.exists', return_value=False)
    @patch('helpers.llmhelpers.OpenAI')
    def test_get_llm_text_davinci(self, mock_openai, mock_exists, mock_load_json, mock_api_key, mock_enable):
        """Test get_llm with text-davinci-003 model"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        mock_llm_instance = MagicMock()
        mock_openai.return_value = mock_llm_instance
        
        result = get_llm('text-davinci-003', 0.5)
        
        mock_openai.assert_called_once()

    @patch('helpers.llmhelpers.get_enable_openai', return_value=True)
    @patch('helpers.llmhelpers.get_openai_api_key', return_value='test-key')
    @patch('helpers.llmhelpers.load_from_json_file', return_value={})
    @patch('helpers.llmhelpers.os.path.exists', return_value=False)
    @patch('helpers.llmhelpers.ChatOpenAI')
    def test_get_llm_chat_model(self, mock_chat_openai, mock_exists, mock_load_json, mock_api_key, mock_enable):
        """Test get_llm with chat model falls back to ChatOpenAI"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance
        
        result = get_llm('gpt-3.5-turbo', 0.5)
        
        mock_chat_openai.assert_called_once()

    @patch('helpers.llmhelpers.get_enable_openai', return_value=False)
    @patch('helpers.llmhelpers.load_from_json_file', return_value={})
    @patch('helpers.llmhelpers.os.path.exists', return_value=False)
    def test_get_llm_openai_disabled(self, mock_exists, mock_load_json, mock_enable):
        """Test get_llm raises when OpenAI is disabled"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        with self.assertRaises(Exception) as context:
            get_llm('unknown-model', 0.5)
        
        self.assertIn("OpenAI is not enabled", str(context.exception))

    @patch('helpers.llmhelpers.get_llm_api_key', return_value='test-key')
    @patch('helpers.llmhelpers.OpenAILLM')
    @patch('helpers.llmhelpers.LOG')
    def test_get_llm_auto_prefix_strips(self, mock_log, mock_openai, mock_api_key):
        """Test get_llm with auto: prefix strips it"""
        from helpers.llmhelpers import get_llm, CLIENTS
        CLIENTS.clear()
        
        mock_llm_instance = MagicMock()
        mock_openai.return_value = mock_llm_instance
        
        result = get_llm('auto:OpenAI:gpt-4', 0.5)
        
        mock_openai.assert_called_once_with(model_name='gpt-4', api_key='test-key')


class TestGetLlmApiKeyException(unittest.TestCase):
    """Test cases for get_llm_api_key exception handling"""

    @patch('helpers.llmhelpers.load_llms')
    @patch('helpers.llmhelpers._ensure_env_file_complete')
    @patch('helpers.llmhelpers.load_dotenv')
    @patch('helpers.llmhelpers.os.getenv', return_value=None)
    @patch('helpers.llmhelpers.get_app_data_dir', return_value='/tmp/test')
    @patch('helpers.llmhelpers.LOG')
    def test_get_api_key_config_exception(self, mock_log, mock_app_dir, mock_getenv, mock_dotenv, mock_ensure, mock_load_llms):
        """Test get_llm_api_key handles exception when loading config"""
        from helpers.llmhelpers import get_llm_api_key
        
        mock_load_llms.side_effect = Exception("Config load error")
        
        result = get_llm_api_key('OpenAI:gpt-4', 'OpenAI')
        
        self.assertIsNone(result)
        mock_log.warning.assert_called()


class TestLLMClass(unittest.TestCase):
    """Test cases for LLM class"""

    @patch('helpers.llmhelpers.get_llm_config', return_value={'chat': True})
    @patch('helpers.llmhelpers.get_llm')
    def test_llm_init(self, mock_get_llm, mock_get_config):
        """Test LLM class initialization"""
        from helpers.llmhelpers import LLM
        
        mock_llm_instance = MagicMock()
        mock_get_llm.return_value = mock_llm_instance
        
        llm = LLM('OpenAI:gpt-4', 0.5)
        
        self.assertEqual(llm.model_name, 'OpenAI:gpt-4')
        self.assertEqual(llm.temperature, 0.5)
        self.assertTrue(llm.chat)
        mock_get_llm.assert_called_once_with('OpenAI:gpt-4', 0.5)

    @patch('helpers.llmhelpers.get_llm_config', return_value={})
    @patch('helpers.llmhelpers.get_llm')
    def test_llm_init_no_colon(self, mock_get_llm, mock_get_config):
        """Test LLM class initialization with model name without colon"""
        from helpers.llmhelpers import LLM
        
        mock_llm_instance = MagicMock()
        mock_get_llm.return_value = mock_llm_instance
        
        llm = LLM('gpt-4', 0.5)
        
        self.assertFalse(llm.chat)

    @patch('helpers.llmhelpers.get_llm_config', return_value={})
    @patch('helpers.llmhelpers.get_llm')
    def test_llm_generate_text_davinci(self, mock_get_llm, mock_get_config):
        """Test LLM generate with text-davinci-003"""
        from helpers.llmhelpers import LLM
        from langchain.schema import HumanMessage
        
        mock_llm_instance = MagicMock()
        mock_result = MagicMock()
        mock_llm_instance.generate.return_value = mock_result
        mock_get_llm.return_value = mock_llm_instance
        
        llm = LLM('text-davinci-003', 0.5)
        messages = [HumanMessage(content="Hello")]
        
        result = llm.generate(messages)
        
        mock_llm_instance.generate.assert_called_once()
        # Check that prompts list was passed
        call_args = mock_llm_instance.generate.call_args
        self.assertIsInstance(call_args[0][0], list)

    @patch('helpers.llmhelpers.get_llm_config', return_value={})
    @patch('helpers.llmhelpers.get_llm')
    def test_llm_generate_chat_model(self, mock_get_llm, mock_get_config):
        """Test LLM generate with chat model"""
        from helpers.llmhelpers import LLM
        from langchain.schema import HumanMessage
        
        mock_llm_instance = MagicMock()
        mock_result = MagicMock()
        mock_llm_instance.generate.return_value = mock_result
        mock_get_llm.return_value = mock_llm_instance
        
        llm = LLM('OpenAI:gpt-4', 0.5)
        messages = [HumanMessage(content="Hello")]
        
        result = llm.generate(messages)
        
        mock_llm_instance.generate.assert_called_once()

    @patch('helpers.llmhelpers.get_llm_config', return_value={})
    @patch('helpers.llmhelpers.get_llm')
    @patch('helpers.llmhelpers.get_enable_oobabooga', return_value=False)
    @patch('helpers.llmhelpers.LOG')
    def test_llm_run_oobabooga_disabled(self, mock_log, mock_enable, mock_get_llm, mock_get_config):
        """Test LLM run returns error when Oobabooga is disabled"""
        from helpers.llmhelpers import LLM
        from langchain.schema import HumanMessage
        
        mock_llm_instance = MagicMock()
        mock_get_llm.return_value = mock_llm_instance
        
        llm = LLM('self-hosted:model', 0.5)
        messages = [HumanMessage(content="Hello")]
        
        text, output, info = llm.run(messages)
        
        self.assertIn("Oobabooga is not enabled", text)

    @patch('helpers.llmhelpers.get_llm_config', return_value={})
    @patch('helpers.llmhelpers.get_llm')
    @patch('helpers.llmhelpers.LOG')
    def test_llm_run_single_generation(self, mock_log, mock_get_llm, mock_get_config):
        """Test LLM run with single generation"""
        from helpers.llmhelpers import LLM
        from langchain.schema import HumanMessage
        
        mock_llm_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.generations = [{'text': 'Hello response', 'generation_info': {'finish_reason': 'stop'}}]
        mock_result.llm_output = {'token_usage': {'total_tokens': 100}}
        mock_llm_instance.generate.return_value = mock_result
        mock_get_llm.return_value = mock_llm_instance
        
        llm = LLM('OpenAI:gpt-4', 0.5)
        messages = [HumanMessage(content="Hello")]
        
        text, output, info = llm.run(messages)
        
        self.assertEqual(text, 'Hello response')
        self.assertIn('generation_time', output)

    @patch('helpers.llmhelpers.get_llm_config', return_value={})
    @patch('helpers.llmhelpers.get_llm')
    @patch('helpers.llmhelpers.LOG')
    def test_llm_run_best_of_multiple(self, mock_log, mock_get_llm, mock_get_config):
        """Test LLM run with best_of > 1"""
        from helpers.llmhelpers import LLM
        from langchain.schema import HumanMessage
        
        mock_llm_instance = MagicMock()
        mock_result1 = MagicMock()
        mock_result1.generations = [{'text': 'Response 1', 'generation_info': {}}]
        mock_result1.llm_output = {'token_usage': {}}
        
        mock_result2 = MagicMock()
        mock_result2.generations = [{'text': 'Response 2', 'generation_info': {}}]
        mock_result2.llm_output = {'token_usage': {}}
        
        mock_llm_instance.generate.side_effect = [mock_result1, mock_result2]
        mock_get_llm.return_value = mock_llm_instance
        
        llm = LLM('OpenAI:gpt-4', 0.5)
        # Mock choose_best_generation to return first result
        llm.choose_best_generation = MagicMock(return_value=0)
        
        messages = [HumanMessage(content="Hello")]
        
        text, output, info = llm.run(messages, best_of=2)
        
        self.assertEqual(text, 'Response 1')
        llm.choose_best_generation.assert_called_once()

    @patch('helpers.llmhelpers.get_llm_config', return_value={})
    @patch('helpers.llmhelpers.get_llm')
    @patch('helpers.llmhelpers.get_available_llms', return_value=(['model1', 'model2'], ['model1', 'model2']))
    @patch('helpers.llmhelpers.llm_router_prompt', return_value='routing prompt')
    @patch('helpers.llmhelpers.LOG')
    def test_llm_run_auto_routing(self, mock_log, mock_router, mock_available, mock_get_llm, mock_get_config):
        """Test LLM run with auto routing"""
        from helpers.llmhelpers import LLM
        
        mock_llm_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.generations = [{'text': 'Response', 'generation_info': {}}]
        mock_result.llm_output = {'token_usage': {}}
        mock_llm_instance.generate.return_value = mock_result
        mock_get_llm.return_value = mock_llm_instance
        
        llm = LLM('auto', 0.5)
        llm.choose_best_llm = MagicMock(return_value='model1')
        
        messages = [{'role': 'user', 'content': 'Hello'}]
        
        text, output, info = llm.run(messages)
        
        llm.choose_best_llm.assert_called_once()

    @patch('helpers.llmhelpers.get_llm_config', return_value={})
    @patch('helpers.llmhelpers.get_llm')
    @patch('helpers.llmhelpers.get_available_llms', return_value=(['model1'], ['model1']))
    @patch('helpers.llmhelpers.llm_router_prompt', return_value='routing prompt')
    @patch('helpers.llmhelpers.LOG')
    def test_llm_run_auto_routing_with_list_content(self, mock_log, mock_router, mock_available, mock_get_llm, mock_get_config):
        """Test LLM run with auto routing and list content"""
        from helpers.llmhelpers import LLM
        
        mock_llm_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.generations = [{'text': 'Response', 'generation_info': {}}]
        mock_result.llm_output = {'token_usage': {}}
        mock_llm_instance.generate.return_value = mock_result
        mock_get_llm.return_value = mock_llm_instance
        
        llm = LLM('auto', 0.5)
        llm.choose_best_llm = MagicMock(return_value='model1')
        
        messages = [{'role': 'user', 'content': [{'text': 'Hello'}]}]
        
        text, output, info = llm.run(messages)
        
        llm.choose_best_llm.assert_called_once()


class TestLLMChooseBestLlm(unittest.TestCase):
    """Test cases for LLM.choose_best_llm method"""

    @patch('helpers.llmhelpers.get_llm_config', return_value={})
    @patch('helpers.llmhelpers.get_llm')
    @patch('helpers.llmhelpers.LOG')
    def test_choose_best_llm_valid_selection(self, mock_log, mock_get_llm, mock_get_config):
        """Test choose_best_llm with valid selection"""
        from helpers.llmhelpers import LLM
        
        mock_llm_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.generations = [{'text': '1'}]
        mock_llm_instance.generate.return_value = mock_result
        mock_get_llm.return_value = mock_llm_instance
        
        llm = LLM('OpenAI:gpt-4', 0.5)
        
        result = llm.choose_best_llm('prompt', ['model0', 'model1', 'model2'])
        
        self.assertEqual(result, 'model1')

    @patch('helpers.llmhelpers.get_llm_config', return_value={})
    @patch('helpers.llmhelpers.get_llm')
    @patch('helpers.llmhelpers.LOG')
    def test_choose_best_llm_with_newline(self, mock_log, mock_get_llm, mock_get_config):
        """Test choose_best_llm removes leading newline"""
        from helpers.llmhelpers import LLM
        
        mock_llm_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.generations = [{'text': '\n2'}]
        mock_llm_instance.generate.return_value = mock_result
        mock_get_llm.return_value = mock_llm_instance
        
        llm = LLM('OpenAI:gpt-4', 0.5)
        
        result = llm.choose_best_llm('prompt', ['model0', 'model1', 'model2'])
        
        self.assertEqual(result, 'model2')

    @patch('helpers.llmhelpers.get_llm_config', return_value={})
    @patch('helpers.llmhelpers.get_llm')
    @patch('helpers.llmhelpers.LOG')
    def test_choose_best_llm_invalid_selection(self, mock_log, mock_get_llm, mock_get_config):
        """Test choose_best_llm with invalid selection returns default"""
        from helpers.llmhelpers import LLM
        
        mock_llm_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.generations = [{'text': 'invalid'}]
        mock_llm_instance.generate.return_value = mock_result
        mock_get_llm.return_value = mock_llm_instance
        
        llm = LLM('OpenAI:gpt-4', 0.5)
        
        result = llm.choose_best_llm('prompt', ['model0', 'model1'])
        
        self.assertEqual(result, 'default_model')

    @patch('helpers.llmhelpers.get_llm_config', return_value={})
    @patch('helpers.llmhelpers.get_llm')
    @patch('helpers.llmhelpers.LOG')
    def test_choose_best_llm_out_of_range(self, mock_log, mock_get_llm, mock_get_config):
        """Test choose_best_llm with out of range selection"""
        from helpers.llmhelpers import LLM
        
        mock_llm_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.generations = [{'text': '5'}]
        mock_llm_instance.generate.return_value = mock_result
        mock_get_llm.return_value = mock_llm_instance
        
        llm = LLM('OpenAI:gpt-4', 0.5)
        
        result = llm.choose_best_llm('prompt', ['model0', 'model1'])
        
        # Out of range, should return default
        self.assertEqual(result, 'default_model')


class TestLLMChooseBestGeneration(unittest.TestCase):
    """Test cases for LLM.choose_best_generation method"""

    @patch('helpers.llmhelpers.get_llm_config', return_value={})
    @patch('helpers.llmhelpers.get_llm')
    @patch('helpers.llmhelpers.parse_generation')
    @patch('helpers.llmhelpers.LOG')
    def test_choose_best_generation_valid(self, mock_log, mock_parse, mock_get_llm, mock_get_config):
        """Test choose_best_generation with valid JSON response"""
        from helpers.llmhelpers import LLM, CodeGeneration
        from langchain.schema import HumanMessage
        
        mock_llm_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.generations = [[MagicMock(text='```json\n{"best_n": 1}\n```')]]
        mock_llm_instance.generate.return_value = mock_result
        mock_get_llm.return_value = mock_llm_instance
        
        mock_code_gen = MagicMock(spec=CodeGeneration)
        mock_code_gen.content = '{"best_n": 1}'
        mock_parse.return_value = [mock_code_gen]
        
        llm = LLM('OpenAI:gpt-4', 0.5)
        
        messages = [HumanMessage(content="Test")]
        mock_gen1 = MagicMock()
        mock_gen1.generations = [[MagicMock(text="Response 1")]]
        mock_gen2 = MagicMock()
        mock_gen2.generations = [[MagicMock(text="Response 2")]]
        
        result = llm.choose_best_generation(messages, [mock_gen1, mock_gen2])
        
        self.assertEqual(result, 1)

    @patch('helpers.llmhelpers.get_llm_config', return_value={})
    @patch('helpers.llmhelpers.get_llm')
    @patch('helpers.llmhelpers.parse_generation')
    @patch('helpers.llmhelpers.LOG')
    def test_choose_best_generation_parse_error(self, mock_log, mock_parse, mock_get_llm, mock_get_config):
        """Test choose_best_generation with parse error returns 0"""
        from helpers.llmhelpers import LLM
        from langchain.schema import HumanMessage
        
        mock_llm_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.generations = [[MagicMock(text='invalid')]]
        mock_llm_instance.generate.return_value = mock_result
        mock_get_llm.return_value = mock_llm_instance
        
        mock_parse.side_effect = Exception("Parse error")
        
        llm = LLM('OpenAI:gpt-4', 0.5)
        
        messages = [HumanMessage(content="Test")]
        mock_gen = MagicMock()
        mock_gen.generations = [[MagicMock(text="Response")]]
        
        result = llm.choose_best_generation(messages, [mock_gen])
        
        self.assertEqual(result, 0)

    @patch('helpers.llmhelpers.get_llm_config', return_value={})
    @patch('helpers.llmhelpers.get_llm')
    @patch('helpers.llmhelpers.parse_generation')
    @patch('helpers.llmhelpers.LOG')
    def test_choose_best_generation_best_n_out_of_range(self, mock_log, mock_parse, mock_get_llm, mock_get_config):
        """Test choose_best_generation with best_n out of range returns 0"""
        from helpers.llmhelpers import LLM, CodeGeneration
        from langchain.schema import HumanMessage
        
        mock_llm_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.generations = [[MagicMock(text='```json\n{"best_n": 10}\n```')]]
        mock_llm_instance.generate.return_value = mock_result
        mock_get_llm.return_value = mock_llm_instance
        
        mock_code_gen = MagicMock(spec=CodeGeneration)
        mock_code_gen.content = '{"best_n": 10}'
        mock_parse.return_value = [mock_code_gen]
        
        llm = LLM('OpenAI:gpt-4', 0.5)
        
        messages = [HumanMessage(content="Test")]
        mock_gen = MagicMock()
        mock_gen.generations = [[MagicMock(text="Response")]]
        
        result = llm.choose_best_generation(messages, [mock_gen])
        
        self.assertEqual(result, 0)

    @patch('helpers.llmhelpers.get_llm_config', return_value={})
    @patch('helpers.llmhelpers.get_llm')
    @patch('helpers.llmhelpers.parse_generation')
    @patch('helpers.llmhelpers.LOG')
    def test_choose_best_generation_text_davinci(self, mock_log, mock_parse, mock_get_llm, mock_get_config):
        """Test choose_best_generation with text-davinci-003"""
        from helpers.llmhelpers import LLM, CodeGeneration
        from langchain.schema import HumanMessage
        
        mock_llm_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.generations = [[MagicMock(text='```json\n{"best_n": 0}\n```')]]
        mock_llm_instance.generate.return_value = mock_result
        mock_get_llm.return_value = mock_llm_instance
        
        mock_code_gen = MagicMock(spec=CodeGeneration)
        mock_code_gen.content = '{"best_n": 0}'
        mock_parse.return_value = [mock_code_gen]
        
        llm = LLM('text-davinci-003', 0.5)
        
        messages = [HumanMessage(content="Test")]
        mock_gen = MagicMock()
        mock_gen.generations = [[MagicMock(text="Response")]]
        
        result = llm.choose_best_generation(messages, [mock_gen])
        
        self.assertEqual(result, 0)

    @patch('helpers.llmhelpers.get_llm_config', return_value={})
    @patch('helpers.llmhelpers.get_llm')
    @patch('helpers.llmhelpers.parse_generation')
    @patch('helpers.llmhelpers.LOG')
    def test_choose_best_generation_invalid_json(self, mock_log, mock_parse, mock_get_llm, mock_get_config):
        """Test choose_best_generation with invalid JSON in code block"""
        from helpers.llmhelpers import LLM, CodeGeneration
        from langchain.schema import HumanMessage
        
        mock_llm_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.generations = [[MagicMock(text='```json\ninvalid json\n```')]]
        mock_llm_instance.generate.return_value = mock_result
        mock_get_llm.return_value = mock_llm_instance
        
        mock_code_gen = MagicMock(spec=CodeGeneration)
        mock_code_gen.content = 'invalid json'
        mock_parse.return_value = [mock_code_gen]
        
        llm = LLM('OpenAI:gpt-4', 0.5)
        
        messages = [HumanMessage(content="Test")]
        mock_gen = MagicMock()
        mock_gen.generations = [[MagicMock(text="Response")]]
        
        result = llm.choose_best_generation(messages, [mock_gen])
        
        # Should return 0 as default when JSON parsing fails
        self.assertEqual(result, 0)


if __name__ == '__main__':
    unittest.main()
