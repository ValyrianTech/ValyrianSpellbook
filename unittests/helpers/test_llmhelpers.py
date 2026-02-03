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


if __name__ == '__main__':
    unittest.main()
