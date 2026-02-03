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


if __name__ == '__main__':
    unittest.main()
