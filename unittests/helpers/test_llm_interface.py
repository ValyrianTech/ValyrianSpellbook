#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock


class TestLLMInterface(unittest.TestCase):
    """Test cases for helpers/llm_interface.py"""

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.llm_interface.load_llms', return_value={})
    @patch('helpers.llm_interface.LOG')
    def test_init_basic(self, mock_log, mock_load_llms, mock_ws):
        """Test LLMInterface basic initialization"""
        from helpers.llm_interface import LLMInterface
        
        class ConcreteLLM(LLMInterface):
            def get_completion_text(self, messages, stop, **kwargs):
                return "test", {}
        
        llm = ConcreteLLM(model_name='test-model')
        
        self.assertEqual(llm.model_name, 'test-model')
        self.assertEqual(llm.prompt_tokens_cost, 0)
        self.assertEqual(llm.completion_tokens_cost, 0)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.llm_interface.load_llms')
    @patch('helpers.llm_interface.LOG')
    def test_init_with_cost_config(self, mock_log, mock_load_llms, mock_ws):
        """Test LLMInterface initialization with cost configuration"""
        from helpers.llm_interface import LLMInterface
        
        mock_load_llms.return_value = {
            'test-config': {
                'model_name': 'test-model',
                'prompt_tokens_cost': 0.01,
                'prompt_tokens_multiplier': 1000,
                'completion_tokens_cost': 0.02,
                'completion_tokens_multiplier': 1000
            }
        }
        
        class ConcreteLLM(LLMInterface):
            def get_completion_text(self, messages, stop, **kwargs):
                return "test", {}
        
        llm = ConcreteLLM(model_name='test-model')
        
        self.assertEqual(llm.prompt_tokens_cost, 0.01)
        self.assertEqual(llm.completion_tokens_cost, 0.02)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.llm_interface.load_llms', return_value={})
    @patch('helpers.llm_interface.LOG')
    def test_calculate_cost(self, mock_log, mock_load_llms, mock_ws):
        """Test calculate_cost method"""
        from helpers.llm_interface import LLMInterface
        
        class ConcreteLLM(LLMInterface):
            def get_completion_text(self, messages, stop, **kwargs):
                return "test", {}
        
        llm = ConcreteLLM(model_name='test-model')
        llm.prompt_tokens_cost = 0.01
        llm.prompt_tokens_multiplier = 1000
        llm.completion_tokens_cost = 0.02
        llm.completion_tokens_multiplier = 1000
        
        cost = llm.calculate_cost(prompt_tokens=1000, completion_tokens=500)
        
        expected = 1000 * (0.01 / 1000) + 500 * (0.02 / 1000)
        self.assertEqual(cost, expected)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.llm_interface.load_llms', return_value={})
    @patch('helpers.llm_interface.LOG')
    def test_check_stop_generation_no_file(self, mock_log, mock_load_llms, mock_ws):
        """Test check_stop_generation returns False when no stop file"""
        from helpers.llm_interface import LLMInterface
        
        result = LLMInterface.check_stop_generation()
        
        self.assertFalse(result)

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.llm_interface.load_llms', return_value={})
    @patch('helpers.llm_interface.LOG')
    def test_check_stop_generation_with_file(self, mock_log, mock_load_llms, mock_ws):
        """Test check_stop_generation returns True and removes stop file"""
        from helpers.llm_interface import LLMInterface
        
        # Create a stop file
        program_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        stop_file = os.path.join(program_dir, 'stop')
        
        try:
            with open(stop_file, 'w') as f:
                f.write('')
            
            result = LLMInterface.check_stop_generation()
            
            self.assertTrue(result)
            self.assertFalse(os.path.exists(stop_file))
        finally:
            if os.path.exists(stop_file):
                os.remove(stop_file)


class TestLoadLlms(unittest.TestCase):
    """Test cases for load_llms function"""

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.llm_interface.load_from_json_file')
    @patch('helpers.llm_interface.os.path.exists', return_value=True)
    def test_load_llms(self, mock_exists, mock_load_json, mock_ws):
        """Test load_llms loads from JSON file"""
        from helpers.llm_interface import load_llms
        
        mock_load_json.return_value = {'model1': {'host': 'localhost'}}
        
        result = load_llms()
        
        self.assertEqual(result, {'model1': {'host': 'localhost'}})

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.llm_interface.os.path.exists', return_value=False)
    def test_load_llms_no_file(self, mock_exists, mock_ws):
        """Test load_llms returns empty dict when file doesn't exist"""
        from helpers.llm_interface import load_llms
        
        result = load_llms()
        
        self.assertEqual(result, {})


class TestGetAvailableLlms(unittest.TestCase):
    """Test cases for get_available_llms function"""

    @patch('helpers.llm_interface.init_websocket_server')
    @patch('helpers.llm_interface.load_llms')
    def test_get_available_llms(self, mock_load_llms, mock_ws):
        """Test get_available_llms returns formatted list"""
        from helpers.llm_interface import get_available_llms
        
        mock_load_llms.return_value = {
            'model1': {'allow_auto_routing': True, 'description': 'Model 1', 'server_type': 'OpenAI'},
            'model2': {'allow_auto_routing': False, 'description': 'Model 2'},
        }
        
        text, names = get_available_llms()
        
        self.assertIn('model1', text)
        self.assertIn('OpenAI:model1', names)
        self.assertEqual(len(names), 1)  # Only model1 has auto_routing enabled


class TestLlmRouterPrompt(unittest.TestCase):
    """Test cases for llm_router_prompt function"""

    @patch('helpers.llm_interface.init_websocket_server')
    def test_llm_router_prompt(self, mock_ws):
        """Test llm_router_prompt generates correct prompt"""
        from helpers.llm_interface import llm_router_prompt
        
        result = llm_router_prompt("Test prompt", "0: Model1\n1: Model2")
        
        self.assertIn("Test prompt", result)
        self.assertIn("0: Model1", result)
        self.assertIn("LLM router", result)


if __name__ == '__main__':
    unittest.main()
