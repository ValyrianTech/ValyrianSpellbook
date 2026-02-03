#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock

from helpers.llm_config_saver import (
    load_from_json_file, save_to_json_file, get_llms_file_path,
    load_llms, save_llm_config_lightweight, get_llm_config_lightweight,
    delete_llm_lightweight
)


class TestLoadFromJsonFile(unittest.TestCase):
    """Test cases for load_from_json_file function"""

    def test_load_existing_file(self):
        """Test loading an existing JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'key': 'value'}, f)
            temp_path = f.name
        
        try:
            result = load_from_json_file(temp_path)
            self.assertEqual(result, {'key': 'value'})
        finally:
            os.unlink(temp_path)

    def test_load_nonexistent_file(self):
        """Test loading a non-existent file returns empty dict"""
        result = load_from_json_file('/nonexistent/path/file.json')
        self.assertEqual(result, {})

    def test_load_invalid_json(self):
        """Test loading invalid JSON returns empty dict"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('not valid json')
            temp_path = f.name
        
        try:
            result = load_from_json_file(temp_path)
            self.assertEqual(result, {})
        finally:
            os.unlink(temp_path)


class TestSaveToJsonFile(unittest.TestCase):
    """Test cases for save_to_json_file function"""

    def test_save_to_file(self):
        """Test saving data to a JSON file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = os.path.join(temp_dir, 'test.json')
            data = {'key': 'value', 'number': 42}
            
            save_to_json_file(data, temp_path)
            
            with open(temp_path, 'r') as f:
                loaded = json.load(f)
            self.assertEqual(loaded, data)

    def test_save_creates_directory(self):
        """Test saving creates parent directories if needed"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = os.path.join(temp_dir, 'subdir', 'test.json')
            data = {'key': 'value'}
            
            save_to_json_file(data, temp_path)
            
            self.assertTrue(os.path.exists(temp_path))


class TestGetLlmsFilePath(unittest.TestCase):
    """Test cases for get_llms_file_path function"""

    def test_returns_path(self):
        """Test that get_llms_file_path returns a path string"""
        result = get_llms_file_path()
        self.assertIsInstance(result, str)
        self.assertTrue(result.endswith('LLMs.json'))


class TestSaveLlmConfigLightweight(unittest.TestCase):
    """Test cases for save_llm_config_lightweight function"""

    @patch('helpers.llm_config_saver.load_llms')
    @patch('helpers.llm_config_saver.save_to_json_file')
    @patch('helpers.llm_config_saver.get_llms_file_path')
    def test_save_new_config(self, mock_path, mock_save, mock_load):
        """Test saving a new LLM config"""
        mock_load.return_value = {}
        mock_path.return_value = '/fake/path/LLMs.json'
        
        config = {'model_name': 'test-model', 'api_key': 'test-key'}
        save_llm_config_lightweight('test-llm', config)
        
        mock_save.assert_called_once()
        saved_data = mock_save.call_args[1]['data']
        self.assertIn('test-llm', saved_data)

    @patch('helpers.llm_config_saver.load_llms')
    @patch('helpers.llm_config_saver.save_to_json_file')
    @patch('helpers.llm_config_saver.get_llms_file_path')
    def test_masked_api_key_preserved(self, mock_path, mock_save, mock_load):
        """Test that masked api_key doesn't override existing key"""
        mock_load.return_value = {'test-llm': {'api_key': 'real-key'}}
        mock_path.return_value = '/fake/path/LLMs.json'
        
        config = {'model_name': 'test-model', 'api_key': '********'}
        save_llm_config_lightweight('test-llm', config)
        
        saved_data = mock_save.call_args[1]['data']
        self.assertEqual(saved_data['test-llm']['api_key'], 'real-key')

    @patch('helpers.llm_config_saver.load_llms')
    @patch('helpers.llm_config_saver.save_to_json_file')
    @patch('helpers.llm_config_saver.get_llms_file_path')
    def test_trailing_slash_removed_from_host(self, mock_path, mock_save, mock_load):
        """Test that trailing slash is removed from host"""
        mock_load.return_value = {}
        mock_path.return_value = '/fake/path/LLMs.json'
        
        config = {'host': 'http://localhost:8080/'}
        save_llm_config_lightweight('test-llm', config)
        
        saved_data = mock_save.call_args[1]['data']
        self.assertEqual(saved_data['test-llm']['host'], 'http://localhost:8080')


class TestGetLlmConfigLightweight(unittest.TestCase):
    """Test cases for get_llm_config_lightweight function"""

    @patch('helpers.llm_config_saver.load_llms')
    def test_get_existing_config(self, mock_load):
        """Test getting an existing LLM config"""
        mock_load.return_value = {'test-llm': {'model_name': 'test'}}
        
        result = get_llm_config_lightweight('test-llm')
        self.assertEqual(result, {'model_name': 'test'})

    @patch('helpers.llm_config_saver.load_llms')
    def test_get_nonexistent_config(self, mock_load):
        """Test getting a non-existent LLM config returns empty dict"""
        mock_load.return_value = {}
        
        result = get_llm_config_lightweight('nonexistent')
        self.assertEqual(result, {})


class TestDeleteLlmLightweight(unittest.TestCase):
    """Test cases for delete_llm_lightweight function"""

    @patch('helpers.llm_config_saver.load_llms')
    @patch('helpers.llm_config_saver.save_to_json_file')
    @patch('helpers.llm_config_saver.get_llms_file_path')
    def test_delete_existing_llm(self, mock_path, mock_save, mock_load):
        """Test deleting an existing LLM"""
        mock_load.return_value = {'test-llm': {'model_name': 'test'}}
        mock_path.return_value = '/fake/path/LLMs.json'
        
        result = delete_llm_lightweight('test-llm')
        
        self.assertTrue(result)
        saved_data = mock_save.call_args[1]['data']
        self.assertNotIn('test-llm', saved_data)

    @patch('helpers.llm_config_saver.load_llms')
    def test_delete_nonexistent_llm(self, mock_load):
        """Test deleting a non-existent LLM returns False"""
        mock_load.return_value = {}
        
        result = delete_llm_lightweight('nonexistent')
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
