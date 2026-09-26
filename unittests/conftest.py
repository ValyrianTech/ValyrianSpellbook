#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pytest configuration and fixtures for the Valyrian Spellbook test suite.
"""
import os
from unittest.mock import patch

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CONFIG_FILE = os.path.join(_REPO_ROOT, 'configuration', 'spellbook.conf')
_EXAMPLE_CONFIG = os.path.join(_REPO_ROOT, 'configuration', 'example_configuration_file.conf')


def _ensure_spellbook_conf():
    """Create a valid configuration/spellbook.conf if missing (e.g. in a fresh clone).

    configuration/spellbook.conf is gitignored, so a fresh clone has none and every
    test that reads the config fails. Copy the example config, substituting the
    placeholder authentication values with valid ones (the secret length must be a
    multiple of 4 for signature()). No-op when a real config already exists.
    """
    if os.path.exists(_CONFIG_FILE):
        return
    with open(_EXAMPLE_CONFIG) as example:
        content = example.read()
    content = content.replace('key=<apikey>', 'key=test_key')
    content = content.replace('secret=<apisecret>', 'secret=test')
    with open(_CONFIG_FILE, 'w') as config:
        config.write(content)


_ensure_spellbook_conf()

# Import helpers.websockethelpers before patching so the module attribute exists.

# Patch the websocket server initialization before any imports that might trigger it.
# The llm_interface module calls init_websocket_server() at import time, which tries
# to bind to port 8765. This causes "address already in use" warnings when multiple
# tests import code that transitively imports llm_interface.

# Patch init_websocket_server to be a no-op, but keep the rest of the module intact
# so that tests for websockethelpers.py can still use the real classes and functions.
_patcher = patch('helpers.websockethelpers.init_websocket_server')
_patcher.start()
