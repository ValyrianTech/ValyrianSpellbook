#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import os

from bips.mnemonic import Mnemonic, ConfigurationError, binary_search


class TestBinarySearch(object):
    """Tests for binary_search function"""

    def test_binary_search_found(self):
        a = ['apple', 'banana', 'cherry', 'date']
        assert binary_search(a, 'banana') == 1
        assert binary_search(a, 'apple') == 0
        assert binary_search(a, 'date') == 3

    def test_binary_search_not_found(self):
        a = ['apple', 'banana', 'cherry', 'date']
        assert binary_search(a, 'fig') == -1
        assert binary_search(a, 'aardvark') == -1

    def test_binary_search_with_bounds(self):
        a = ['apple', 'banana', 'cherry', 'date']
        assert binary_search(a, 'banana', lo=0, hi=2) == 1
        assert binary_search(a, 'date', lo=0, hi=2) == -1


class TestMnemonic(object):
    """Tests for Mnemonic class"""

    def test_mnemonic_init_english(self):
        m = Mnemonic('english')
        assert m.radix == 2048
        assert len(m.wordlist) == 2048

    def test_mnemonic_init_japanese(self):
        m = Mnemonic('japanese')
        assert m.radix == 2048
        assert len(m.wordlist) == 2048

    def test_mnemonic_get_directory(self):
        directory = Mnemonic._get_directory()
        assert os.path.isdir(directory)
        assert 'wordlist' in directory

    def test_mnemonic_list_languages(self):
        languages = Mnemonic.list_languages()
        assert 'english' in languages
        assert 'japanese' in languages
        assert len(languages) >= 2

    def test_mnemonic_normalize_string_str(self):
        result = Mnemonic.normalize_string('hello')
        assert result == 'hello'

    def test_mnemonic_normalize_string_bytes(self):
        result = Mnemonic.normalize_string(b'hello')
        assert result == 'hello'

    def test_mnemonic_normalize_string_invalid(self):
        with pytest.raises(TypeError):
            Mnemonic.normalize_string(123)

    def test_mnemonic_detect_language_english(self):
        mnemonic = "abandon ability able about above absent"
        lang = Mnemonic.detect_language(mnemonic)
        assert lang == 'english'

    def test_mnemonic_detect_language_not_found(self):
        with pytest.raises(ConfigurationError):
            Mnemonic.detect_language("xyznotaword")

    def test_mnemonic_generate(self):
        m = Mnemonic('english')
        mnemonic = m.generate(strength=128)
        words = mnemonic.split(' ')
        assert len(words) == 12

    def test_mnemonic_generate_different_strengths(self):
        m = Mnemonic('english')
        # 128 bits = 12 words
        assert len(m.generate(strength=128).split(' ')) == 12
        # 160 bits = 15 words
        assert len(m.generate(strength=160).split(' ')) == 15
        # 192 bits = 18 words
        assert len(m.generate(strength=192).split(' ')) == 18
        # 224 bits = 21 words
        assert len(m.generate(strength=224).split(' ')) == 21
        # 256 bits = 24 words
        assert len(m.generate(strength=256).split(' ')) == 24

    def test_mnemonic_generate_invalid_strength(self):
        m = Mnemonic('english')
        with pytest.raises(ValueError):
            m.generate(strength=100)

    def test_mnemonic_to_mnemonic(self):
        m = Mnemonic('english')
        # 16 bytes = 128 bits = 12 words
        data = bytes([0] * 16)
        mnemonic = m.to_mnemonic(data)
        words = mnemonic.split(' ')
        assert len(words) == 12

    def test_mnemonic_to_mnemonic_invalid_length(self):
        m = Mnemonic('english')
        with pytest.raises(ValueError):
            m.to_mnemonic(bytes([0] * 10))

    def test_mnemonic_to_entropy(self):
        m = Mnemonic('english')
        # Generate a mnemonic and convert back to entropy
        data = bytes([0] * 16)
        mnemonic = m.to_mnemonic(data)
        entropy = m.to_entropy(mnemonic)
        assert bytes(entropy) == data

    def test_mnemonic_to_entropy_invalid_word_count(self):
        m = Mnemonic('english')
        with pytest.raises(ValueError):
            m.to_entropy("abandon ability able")  # Only 3 words

    def test_mnemonic_to_entropy_word_not_found(self):
        m = Mnemonic('english')
        with pytest.raises(LookupError):
            m.to_entropy("abandon ability able about above absent absorb abstract absurd abuse access xyznotaword")

    def test_mnemonic_check_valid(self):
        m = Mnemonic('english')
        # Generate a valid mnemonic
        mnemonic = m.generate(strength=128)
        assert m.check(mnemonic) == True

    def test_mnemonic_check_invalid_word_count(self):
        m = Mnemonic('english')
        assert m.check("abandon ability able") == False

    def test_mnemonic_check_invalid_word(self):
        m = Mnemonic('english')
        assert m.check("abandon ability able about above absent absorb abstract absurd abuse access xyznotaword") == False

    def test_mnemonic_check_invalid_checksum(self):
        m = Mnemonic('english')
        # This mnemonic has wrong checksum
        assert m.check("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon") == False

    def test_mnemonic_expand_word_exact_match(self):
        m = Mnemonic('english')
        assert m.expand_word('abandon') == 'abandon'

    def test_mnemonic_expand_word_prefix_unique(self):
        m = Mnemonic('english')
        # 'aban' should expand to 'abandon' if it's unique
        result = m.expand_word('aban')
        assert result == 'abandon'

    def test_mnemonic_expand_word_prefix_not_unique(self):
        m = Mnemonic('english')
        # 'ab' has multiple matches, should return input
        result = m.expand_word('ab')
        assert result == 'ab'

    def test_mnemonic_expand(self):
        m = Mnemonic('english')
        result = m.expand('aban abil')
        assert 'abandon' in result
        assert 'ability' in result

    def test_mnemonic_to_seed(self):
        seed = Mnemonic.to_seed("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about", "")
        assert len(seed) == 64
        assert isinstance(seed, bytes)

    def test_mnemonic_to_seed_with_passphrase(self):
        seed_no_pass = Mnemonic.to_seed("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about", "")
        seed_with_pass = Mnemonic.to_seed("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about", "test")
        assert seed_no_pass != seed_with_pass


class TestConfigurationError(object):
    """Tests for ConfigurationError"""

    def test_configuration_error(self):
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Test error")


class TestMnemonicJapanese(object):
    """Tests for Japanese mnemonic handling"""

    def test_mnemonic_to_mnemonic_japanese(self):
        """Test to_mnemonic with Japanese language (ideographic space)"""
        m = Mnemonic('japanese')
        data = bytes([0] * 16)
        mnemonic = m.to_mnemonic(data)
        # Japanese mnemonics use ideographic space (U+3000)
        assert '\u3000' in mnemonic


class TestMnemonicMain(object):
    """Tests for main() function"""

    def test_main_with_argv(self):
        """Test main function with command line argument"""
        import sys
        from bips.mnemonic import main
        
        # Save original argv
        original_argv = sys.argv
        
        try:
            # Set argv with hex data (16 bytes = 32 hex chars)
            sys.argv = ['mnemonic.py', '00' * 16]
            # main() should run without error
            main()
        finally:
            # Restore original argv
            sys.argv = original_argv

    def test_main_with_stdin(self):
        """Test main function with stdin input"""
        import sys
        import io
        from bips.mnemonic import main
        
        # Save original stdin and argv
        original_stdin = sys.stdin
        original_argv = sys.argv
        
        try:
            # Set argv to just the script name (no arguments)
            sys.argv = ['mnemonic.py']
            # Provide hex data via stdin
            sys.stdin = io.StringIO('00' * 16 + '\n')
            # main() should run without error
            main()
        finally:
            # Restore original stdin and argv
            sys.stdin = original_stdin
            sys.argv = original_argv


class TestMnemonicEdgeCases(object):
    """Edge case tests for Mnemonic class"""

    def test_to_entropy_with_list_input(self):
        """Test to_entropy accepts list of words directly"""
        m = Mnemonic('english')
        # Generate a valid mnemonic and split into list
        mnemonic = m.generate(strength=128)
        words_list = mnemonic.split(' ')
        # Should accept list directly
        entropy = m.to_entropy(words_list)
        assert len(entropy) == 16

    def test_to_entropy_checksum_validation(self):
        """Test that to_entropy validates checksum correctly"""
        m = Mnemonic('english')
        # Generate valid mnemonic
        mnemonic = m.generate(strength=128)
        # Verify it can be converted back
        entropy = m.to_entropy(mnemonic)
        # Convert back to mnemonic
        mnemonic2 = m.to_mnemonic(bytes(entropy))
        assert mnemonic == mnemonic2
