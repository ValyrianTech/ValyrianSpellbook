#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from helpers.textgenerationhelpers import (
    LLMResult, BaseGeneration, TextGeneration, CodeGeneration, parse_generation
)


class TestBaseGeneration(unittest.TestCase):
    """Test cases for BaseGeneration class"""

    def test_init(self):
        """Test BaseGeneration initialization"""
        gen = BaseGeneration("test content")
        self.assertEqual(gen.content, "test content")

    def test_to_json(self):
        """Test BaseGeneration to_json method"""
        gen = BaseGeneration("test content")
        result = gen.to_json()
        self.assertEqual(result, {'content': 'test content'})


class TestTextGeneration(unittest.TestCase):
    """Test cases for TextGeneration class"""

    def test_init(self):
        """Test TextGeneration initialization"""
        gen = TextGeneration("text content")
        self.assertEqual(gen.content, "text content")

    def test_to_json(self):
        """Test TextGeneration to_json method"""
        gen = TextGeneration("text content")
        result = gen.to_json()
        self.assertEqual(result, {'content': 'text content', 'type': 'text'})


class TestCodeGeneration(unittest.TestCase):
    """Test cases for CodeGeneration class"""

    def test_init(self):
        """Test CodeGeneration initialization"""
        gen = CodeGeneration("print('hello')", "python")
        self.assertEqual(gen.content, "print('hello')")
        self.assertEqual(gen.language, "python")

    def test_to_json(self):
        """Test CodeGeneration to_json method"""
        gen = CodeGeneration("print('hello')", "python")
        result = gen.to_json()
        self.assertEqual(result, {
            'content': "print('hello')",
            'language': 'python',
            'type': 'code'
        })


class TestParseGeneration(unittest.TestCase):
    """Test cases for parse_generation function"""

    def test_plain_text(self):
        """Test parsing plain text without code blocks"""
        result = parse_generation("Hello world")
        self.assertEqual(result, [{'type': 'text', 'content': 'Hello world'}])

    def test_single_code_block(self):
        """Test parsing a single code block"""
        input_str = "```python\nprint('hello')\n```"
        result = parse_generation(input_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['type'], 'code')
        self.assertEqual(result[0]['language'], 'python')
        self.assertEqual(result[0]['content'], "print('hello')\n")

    def test_text_before_code_block(self):
        """Test parsing text before a code block"""
        input_str = "Here is some code:\n```python\nprint('hello')\n```"
        result = parse_generation(input_str)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['type'], 'text')
        self.assertEqual(result[0]['content'], "Here is some code:\n")
        self.assertEqual(result[1]['type'], 'code')

    def test_text_after_code_block(self):
        """Test parsing text after a code block"""
        input_str = "```python\nprint('hello')\n```\nThat was the code."
        result = parse_generation(input_str)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['type'], 'code')
        self.assertEqual(result[1]['type'], 'text')
        self.assertEqual(result[1]['content'], "\nThat was the code.")

    def test_multiple_code_blocks(self):
        """Test parsing multiple code blocks"""
        input_str = "```python\ncode1\n```\ntext\n```javascript\ncode2\n```"
        result = parse_generation(input_str)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['type'], 'code')
        self.assertEqual(result[0]['language'], 'python')
        self.assertEqual(result[1]['type'], 'text')
        self.assertEqual(result[2]['type'], 'code')
        self.assertEqual(result[2]['language'], 'javascript')

    def test_unclosed_code_block(self):
        """Test parsing an unclosed code block"""
        input_str = "Here is code:\n```python\nprint('hello')"
        result = parse_generation(input_str)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['type'], 'text')
        self.assertEqual(result[1]['type'], 'code')

    def test_empty_string(self):
        """Test parsing empty string"""
        result = parse_generation("")
        self.assertEqual(result, [])

    def test_code_block_no_language(self):
        """Test parsing code block without language specified"""
        input_str = "```\nsome code\n```"
        result = parse_generation(input_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['type'], 'code')
        self.assertEqual(result[0]['language'], '')

    def test_backtick_only(self):
        """Test that single backtick is filtered out"""
        result = parse_generation("`")
        self.assertEqual(result, [])


class TestLLMResult(unittest.TestCase):
    """Test cases for LLMResult class"""

    def test_llm_result_creation(self):
        """Test LLMResult can be instantiated"""
        result = LLMResult()
        result.generations = []
        self.assertEqual(result.generations, [])


if __name__ == '__main__':
    unittest.main()
