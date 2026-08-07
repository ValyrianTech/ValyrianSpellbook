#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for dockerfiles/replace_placeholders.py — replaces config placeholders
with environment variable values.

replace_placeholders.py runs all logic at module level. We mock
ConfigParser, os.environ.get, and builtins.open before importing via
importlib, following the pattern from test_spellbook.py.
"""
import importlib.util
import os
import sys

import mock
from configparser import ConfigParser

_REPLACE_PH_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'dockerfiles', 'replace_placeholders.py')

_REAL_OPEN = open


def _open_side_effect(file, mode='r', *args, **kwargs):
    """Mock open: raise FileNotFoundError for reads of spellbook.conf
    (ConfigParser.read catches OSError), mock writes."""
    if isinstance(file, str) and 'spellbook.conf' in file:
        if 'w' in mode:
            return mock.mock_open()()
        raise FileNotFoundError(2, 'No such file', str(file))
    return _REAL_OPEN(file, mode, *args, **kwargs)


def _make_config():
    """Create a ConfigParser with test sections."""
    config = ConfigParser()
    config.add_section('RESTAPI')
    config.set('RESTAPI', 'host', '<host>')
    config.set('RESTAPI', 'port', '<port>')
    config.add_section('SMTP')
    config.set('SMTP', 'enable_smtp', '<enable_smtp>')
    config.set('SMTP', 'host', '<smtp_host>')
    return config


def _env_side_effect(name):
    """Return a value for RESTAPI_HOST, None for others."""
    if name == 'RESTAPI_HOST':
        return '1.2.3.4'
    if name == 'RESTAPI_PORT':
        return '42069'
    return None


def _import_replace_placeholders(config=None, env_side_effect=None):
    """Import replace_placeholders with mocked dependencies. Returns the module object."""
    if 'replace_placeholders' in sys.modules:
        del sys.modules['replace_placeholders']

    if config is None:
        config = _make_config()
    if env_side_effect is None:
        env_side_effect = _env_side_effect

    patches = [
        mock.patch('configparser.ConfigParser', return_value=config),
        mock.patch('os.environ.get', side_effect=env_side_effect),
        mock.patch('builtins.open', side_effect=_open_side_effect),
    ]

    for p in patches:
        p.start()

    try:
        spec = importlib.util.spec_from_file_location('replace_placeholders', _REPLACE_PH_PATH)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sys.modules['replace_placeholders'] = mod
        return mod, config
    finally:
        for p in patches:
            p.stop()


class TestReplacePlaceholdersImport:

    def test_module_imports_successfully(self):
        mod, _ = _import_replace_placeholders()
        assert mod is not None

    def test_config_params_dict_exists(self):
        mod, _ = _import_replace_placeholders()
        assert hasattr(mod, 'config_params')
        assert isinstance(mod.config_params, dict)

    def test_config_params_has_restapi(self):
        mod, _ = _import_replace_placeholders()
        assert 'RESTAPI' in mod.config_params

    def test_config_params_has_smtp(self):
        mod, _ = _import_replace_placeholders()
        assert 'SMTP' in mod.config_params

    def test_config_params_has_authentication(self):
        mod, _ = _import_replace_placeholders()
        assert 'Authentication' in mod.config_params

    def test_config_params_has_all_sections(self):
        mod, _ = _import_replace_placeholders()
        expected_sections = {'RESTAPI', 'Authentication', 'SMTP', 'Wallet', 'Transactions',
                             'IPFS', 'APPS', 'SSL', 'Twitter', 'OpenAI', 'Mastodon',
                             'Nostr', 'LLMs', 'Uploads', 'Transcribe'}
        assert set(mod.config_params.keys()) == expected_sections


class TestPlaceholderReplacement:

    def test_env_var_replaces_placeholder(self):
        _, config = _import_replace_placeholders()
        assert config.get('RESTAPI', 'host') == '1.2.3.4'

    def test_env_var_replaces_port_placeholder(self):
        _, config = _import_replace_placeholders()
        assert config.get('RESTAPI', 'port') == '42069'

    def test_no_env_var_keeps_placeholder(self):
        _, config = _import_replace_placeholders()
        # SMTP host has no matching env var
        assert config.get('SMTP', 'host') == '<smtp_host>'

    def test_no_env_var_for_smtp_enable(self):
        _, config = _import_replace_placeholders()
        assert config.get('SMTP', 'enable_smtp') == '<enable_smtp>'

    def test_empty_env_replaces_placeholder(self):
        """Empty string env var should still replace the placeholder."""
        def env_returns_empty(name):
            if name == 'RESTAPI_HOST':
                return ''
            return None
        _, config = _import_replace_placeholders(env_side_effect=env_returns_empty)
        assert config.get('RESTAPI', 'host') == ''

    def test_none_env_keeps_placeholder(self):
        """When os.environ.get returns None, placeholder stays."""
        _, config = _import_replace_placeholders(env_side_effect=lambda name: None)
        assert config.get('RESTAPI', 'host') == '<host>'
