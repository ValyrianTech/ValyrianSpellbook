#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for webui.config Settings."""
import pytest
from unittest.mock import patch


class TestSettings:
    def test_default_values(self):
        from config import Settings
        s = Settings()
        assert s.WEBUI_HOST == "0.0.0.0"
        assert s.WEBUI_PORT == 5001
        assert s.DEBUG is True
        assert isinstance(s.SESSION_SECRET_KEY, str)
        assert len(s.SESSION_SECRET_KEY) == 64  # 32 bytes hex = 64 chars

    def test_spellbook_api_host(self):
        from config import Settings
        s = Settings()
        with patch("config.get_host", return_value="localhost"):
            assert s.SPELLBOOK_API_HOST == "localhost"

    def test_spellbook_api_port(self):
        from config import Settings
        s = Settings()
        with patch("config.get_port", return_value=8080):
            assert s.SPELLBOOK_API_PORT == 8080

    def test_spellbook_api_url(self):
        from config import Settings
        s = Settings()
        with patch("config.get_host", return_value="localhost"), \
             patch("config.get_port", return_value=8080):
            assert s.SPELLBOOK_API_URL == "http://localhost:8080"

    def test_session_secret_key_is_set(self):
        from config import Settings
        s = Settings()
        assert isinstance(s.SESSION_SECRET_KEY, str)
        assert len(s.SESSION_SECRET_KEY) == 64
