#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pytest fixtures for webui tests.
"""
import os
import sys

import pytest

# Add webui directory to path so its modules can be imported
WEBUI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "webui")
sys.path.insert(0, WEBUI_DIR)


@pytest.fixture
def mock_settings():
    """Patch settings to use predictable values."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("config.settings.WEBUI_HOST", "127.0.0.1")
        mp.setattr("config.settings.WEBUI_PORT", 5001)
        mp.setattr("config.settings.DEBUG", False)
        mp.setattr("config.settings.SESSION_SECRET_KEY", "test-secret-key-for-testing")
        yield mp


@pytest.fixture
def app(mock_settings):
    """Import and return the FastAPI app after settings are patched."""
    # Force reimport of main and routers so they pick up patched settings
    for mod in list(sys.modules.keys()):
        if mod.startswith("main") or mod.startswith("routers."):
            del sys.modules[mod]
    import main as main_module
    return main_module.app


@pytest.fixture
def client(app):
    """Starlette TestClient for the FastAPI app."""
    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c
