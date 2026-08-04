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


def _import_quickstart(input_values=None):
    """Import quickstart with mocked dependencies. Returns the module object."""
    if 'quickstart' in sys.modules:
        del sys.modules['quickstart']

    if input_values is None:
        # Default: empty string for all prompts (keep current values)
        input_values = [''] * 100

    patches = [
        mock.patch('builtins.input', side_effect=input_values),
        mock.patch('os.path.isfile', side_effect=_isfile_side_effect),
        mock.patch('builtins.open', side_effect=_open_side_effect),
        mock.patch('helpers.jsonhelpers.load_from_json_file', return_value={}),
        mock.patch('authentication.initialize_api_keys_file'),
        mock.patch('helpers.configurationhelpers.what_is_my_ip', return_value='1.2.3.4'),
    ]

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
