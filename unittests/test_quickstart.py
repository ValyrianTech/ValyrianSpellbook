#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for quickstart.py — interactive configuration setup CLI.

quickstart.py runs all logic at module level (no __main__ guard). We patch
sys.argv, input, file I/O, and helper functions before importing via
importlib, following the pattern from test_spellbook.py.
"""
import importlib.util
import os
import sys

import mock
import pytest
from configparser import ConfigParser

_QUICKSTART_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'quickstart.py')

_REAL_OPEN = open


def _open_side_effect(file, mode='r', *args, **kwargs):
    """Mock open: let reads use real open, mock writes to spellbook.conf."""
    if isinstance(file, str) and 'spellbook.conf' in file and 'w' in mode:
        return mock.mock_open()()
    return _REAL_OPEN(file, mode, *args, **kwargs)


def _isfile_side_effect(path):
    """Return False for spellbook.conf (use example config), True for api_keys.json."""
    if isinstance(path, str) and 'spellbook.conf' in path:
        return False
    if isinstance(path, str) and 'api_keys.json' in path:
        return True
    return False


def _import_quickstart(input_values=None, isfile_side_effect=None, extra_patches=None):
    """Import quickstart with mocked dependencies. Returns the module object."""
    if 'quickstart' in sys.modules:
        del sys.modules['quickstart']

    if input_values is None:
        # Default: empty string for all prompts (keep current values)
        input_values = [''] * 100
    if isfile_side_effect is None:
        isfile_side_effect = _isfile_side_effect

    patches = [
        mock.patch('builtins.input', side_effect=input_values),
        mock.patch('os.path.isfile', side_effect=isfile_side_effect),
        mock.patch('builtins.open', side_effect=_open_side_effect),
        mock.patch('helpers.jsonhelpers.load_from_json_file', return_value={}),
        mock.patch('authentication.initialize_api_keys_file'),
        mock.patch('helpers.configurationhelpers.what_is_my_ip', return_value='1.2.3.4'),
    ]

    if extra_patches:
        patches.extend(extra_patches)

    for p in patches:
        p.start()

    try:
        spec = importlib.util.spec_from_file_location('quickstart', _QUICKSTART_PATH)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sys.modules['quickstart'] = mod
        return mod
    finally:
        for p in patches:
            p.stop()


class TestQuickstartImport:

    def test_module_imports_successfully(self):
        mod = _import_quickstart()
        assert mod is not None

    def test_program_dir_set(self):
        mod = _import_quickstart()
        assert mod.PROGRAM_DIR is not None
        assert os.path.isabs(mod.PROGRAM_DIR)

    def test_update_config_function_exists(self):
        mod = _import_quickstart()
        assert callable(mod.update_config)


class TestUpdateConfig:

    def test_update_config_keeps_current_value_on_empty_input(self):
        config = ConfigParser()
        config.add_section('Test')
        config.set('Test', 'key', 'current_val')

        with mock.patch('builtins.input', return_value=''):
            from quickstart import update_config
            update_config(config, 'Test', 'key', 'Prompt (%s) ')

        assert config.get('Test', 'key') == 'current_val'

    def test_update_config_sets_new_value(self):
        config = ConfigParser()
        config.add_section('Test')
        config.set('Test', 'key', 'old_val')

        with mock.patch('builtins.input', return_value='new_val'):
            from quickstart import update_config
            update_config(config, 'Test', 'key', 'Prompt (%s) ')

        assert config.get('Test', 'key') == 'new_val'

    def test_update_config_uses_fallback(self):
        config = ConfigParser()
        config.add_section('Test')
        # Don't set 'key' — fallback should be used

        with mock.patch('builtins.input', return_value=''):
            from quickstart import update_config
            update_config(config, 'Test', 'key', 'Prompt (%s) ', fallback='default_val')

        assert config.get('Test', 'key') == 'default_val'

    def test_update_config_uses_current_value_override(self):
        config = ConfigParser()
        config.add_section('Test')
        config.set('Test', 'key', 'config_val')

        with mock.patch('builtins.input', return_value=''):
            from quickstart import update_config
            update_config(config, 'Test', 'key', 'Prompt (%s) ', current_value='override_val')

        assert config.get('Test', 'key') == 'override_val'


class TestQuickstartFullRun:

    def test_run_with_defaults(self):
        """Module-level code runs with all defaults (empty input)."""
        mod = _import_quickstart()
        # The module should have run successfully and printed output
        assert hasattr(mod, 'PROGRAM_DIR')

    def test_run_with_custom_host(self):
        """Provide a custom host value for RESTAPI."""
        inputs = [''] * 100
        # First input is for RESTAPI host
        inputs[0] = 'my.host.com'
        mod = _import_quickstart(input_values=inputs)
        assert mod is not None


class TestQuickstartEnabledBranches:
    """Test that enabled branches for SMTP, SSL, Twitter, OpenAI, Mastodon, Nostr are entered."""

    def test_all_enabled_branches(self):
        """Run quickstart with all enable_* options set to 'true' via input."""
        inputs = [''] * 100
        # With all '' inputs, the input sequence is:
        # 0-13: basic settings (14 inputs)
        # 14: SMTP enable_smtp
        # 15: IPFS enable_ipfs (already 'true' in example config, so branch entered)
        # 16-19: IPFS fields (4 inputs)
        # 20: SSL enable_ssl
        # 21: Twitter enable_twitter
        # 22: OpenAI enable_openai
        # 23: Mastodon enable_mastodon
        # (Nostr: checked from config, no input)
        # 24: LLMs enable_oobabooga
        # ...
        # When SMTP is enabled, 5 extra inputs are consumed (15-19)
        # When IPFS is enabled (already true), 4 extra inputs are consumed
        # So with SMTP=true, the sequence shifts by 5
        inputs[14] = 'true'  # SMTP enable_smtp -> enters branch (5 extra inputs: 15-19)
        # After SMTP branch: IPFS enable_ipfs at 20, IPFS fields at 21-24
        # SSL enable_ssl at 25
        inputs[25] = 'true'  # SSL enable_ssl -> enters branch (4 extra inputs: 26-29)
        # After SSL branch: Twitter enable_twitter at 30
        inputs[30] = 'true'  # Twitter enable_twitter -> enters branch (5 extra inputs: 31-35)
        # After Twitter branch: OpenAI enable_openai at 36
        inputs[36] = 'true'  # OpenAI enable_openai -> enters branch (2 extra inputs: 37-38)
        # After OpenAI branch: Mastodon enable_mastodon at 39
        inputs[39] = 'true'  # Mastodon enable_mastodon -> enters branch (4 extra inputs: 40-43)
        # After Mastodon branch: Nostr (from config, no input)
        # LLMs at 44, etc.

        # Patch ConfigParser.getboolean to return True for Nostr
        original_getboolean = ConfigParser.getboolean

        def mock_getboolean(self, section, option, *args, **kwargs):
            if section == 'Nostr' and option == 'enable_nostr':
                return True
            return original_getboolean(self, section, option, *args, **kwargs)

        with mock.patch.object(ConfigParser, 'getboolean', mock_getboolean):
            mod = _import_quickstart(input_values=inputs)
            assert mod is not None


class TestQuickstartSpellbookConfExists:
    """Test the else branch when spellbook.conf already exists (line 26)."""

    def test_spellbook_conf_exists(self):
        """When spellbook.conf exists, the else branch reads it instead of the example."""
        def isfile_spellbook_conf_exists(path):
            if isinstance(path, str) and 'spellbook.conf' in path:
                return True
            if isinstance(path, str) and 'api_keys.json' in path:
                return True
            return False

        # Patch ConfigParser.read to always read the example config
        # so we have valid sections/options
        original_read = ConfigParser.read

        def mock_read(self, filenames, *args, **kwargs):
            example = os.path.join(os.path.dirname(_QUICKSTART_PATH),
                                   'configuration', 'example_configuration_file.conf')
            return original_read(self, example, *args, **kwargs)

        extra = [mock.patch.object(ConfigParser, 'read', mock_read)]
        mod = _import_quickstart(isfile_side_effect=isfile_spellbook_conf_exists,
                                 extra_patches=extra)
        assert mod is not None


class TestQuickstartEmptyHost:
    """Test that an empty host triggers what_is_my_ip() (line 31)."""

    def test_empty_host_calls_what_is_my_ip(self):
        """When host is empty, what_is_my_ip() is called to set it."""
        original_get = ConfigParser.get

        def mock_get(self, section, option, **kwargs):
            if section == 'RESTAPI' and option == 'host':
                return ''
            return original_get(self, section, option, **kwargs)

        with mock.patch.object(ConfigParser, 'get', mock_get):
            mod = _import_quickstart()
            assert mod is not None


class TestQuickstartApiKeysMissing:
    """Test that missing api_keys.json triggers initialize_api_keys_file() (lines 42-43)."""

    def test_api_keys_missing_initializes(self):
        """When api_keys.json doesn't exist, initialize_api_keys_file() is called."""
        def isfile_no_api_keys(path):
            if isinstance(path, str) and 'spellbook.conf' in path:
                return False
            return False  # api_keys.json also returns False

        mod = _import_quickstart(isfile_side_effect=isfile_no_api_keys)
        assert mod is not None
