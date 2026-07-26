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


class TestPrintPrompt(unittest.TestCase):
    """Test cases for print_prompt function"""

    def test_print_prompt_string(self):
        """Test print_prompt with a simple string"""
        from helpers.textgenerationhelpers import print_prompt
        import io
        from contextlib import redirect_stdout
        f = io.StringIO()
        with redirect_stdout(f):
            print_prompt("Hello world")
        output = f.getvalue()
        self.assertIn("Hello world|", output)
        self.assertIn("======================", output)

    def test_print_prompt_messages_list(self):
        """Test print_prompt with a list of messages"""
        from helpers.textgenerationhelpers import print_prompt
        import io
        from contextlib import redirect_stdout
        messages = [
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi there'},
        ]
        f = io.StringIO()
        with redirect_stdout(f):
            print_prompt(messages)
        output = f.getvalue()
        self.assertIn("Hello", output)
        self.assertIn("Hi there", output)
        self.assertIn("|", output)

    def test_print_prompt_multimodal_messages(self):
        """Test print_prompt with multimodal content (list of parts)"""
        from helpers.textgenerationhelpers import print_prompt
        import io
        from contextlib import redirect_stdout
        messages = [
            {'role': 'user', 'content': [
                {'text': 'Describe this image'},
                {'image_url': 'http://example.com/img.png'},
            ]},
        ]
        f = io.StringIO()
        with redirect_stdout(f):
            print_prompt(messages)
        output = f.getvalue()
        self.assertIn("Describe this image", output)
        self.assertIn("===Included image===", output)

    def test_print_prompt_multimodal_string_parts(self):
        """Test print_prompt with multimodal content containing string parts"""
        from helpers.textgenerationhelpers import print_prompt
        import io
        from contextlib import redirect_stdout
        messages = [
            {'role': 'user', 'content': ['plain string part']},
        ]
        f = io.StringIO()
        with redirect_stdout(f):
            print_prompt(messages)
        output = f.getvalue()
        self.assertIn("plain string part", output)

    def test_print_prompt_other_type(self):
        """Test print_prompt with a non-string non-list type"""
        from helpers.textgenerationhelpers import print_prompt
        import io
        from contextlib import redirect_stdout
        f = io.StringIO()
        with redirect_stdout(f):
            print_prompt(42)
        output = f.getvalue()
        self.assertIn("42|", output)

    def test_print_prompt_empty_content_in_message(self):
        """Test print_prompt with a message that has no 'content' key"""
        from helpers.textgenerationhelpers import print_prompt
        import io
        from contextlib import redirect_stdout
        messages = [{'role': 'user'}]
        f = io.StringIO()
        with redirect_stdout(f):
            print_prompt(messages)
        output = f.getvalue()
        self.assertIn("|", output)


class TestParseGenerationEdgeCases(unittest.TestCase):
    """Edge case tests for parse_generation function"""

    def test_unclosed_code_block_no_text_before(self):
        """Test unclosed code block with no text before it"""
        result = parse_generation("```python\nprint('hello')")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['type'], 'code')

    def test_unclosed_code_block_empty_after(self):
        """Test unclosed code block with nothing after the opening backticks"""
        result = parse_generation("text before```")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['type'], 'text')

    def test_code_block_no_code_content(self):
        """Test code block with language but no code content"""
        result = parse_generation("```python\n```")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['type'], 'code')
        self.assertEqual(result[0]['language'], 'python')
        self.assertEqual(result[0]['content'], '')

    def test_only_backticks(self):
        """Test string with only triple backticks"""
        result = parse_generation("```")
        self.assertEqual(result, [])

    def test_text_with_single_backtick_after_code(self):
        """Test that single backtick after code block is not included"""
        result = parse_generation("```python\ncode\n```")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['type'], 'code')


if __name__ == '__main__':
    unittest.main()
