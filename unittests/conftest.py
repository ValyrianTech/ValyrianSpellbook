#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pytest configuration and fixtures for the Valyrian Spellbook test suite.
"""
from unittest.mock import patch

# Patch the websocket server initialization before any imports that might trigger it.
# The llm_interface module calls init_websocket_server() at import time, which tries
# to bind to port 8765. This causes "address already in use" warnings when multiple
# tests import code that transitively imports llm_interface.

# Patch init_websocket_server to be a no-op, but keep the rest of the module intact
# so that tests for websockethelpers.py can still use the real classes and functions.
_patcher = patch('helpers.websockethelpers.init_websocket_server')
_patcher.start()
