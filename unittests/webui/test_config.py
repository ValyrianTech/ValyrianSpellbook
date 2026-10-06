#!/usr/bin/env python
"""Tests for webui.config Settings."""
import stat
from unittest.mock import patch

import pytest


@pytest.fixture
def isolated_secret_key(monkeypatch, tmp_path):
    """Point the persisted key file at tmp_path and clear the env var."""
    key_file = tmp_path / "session_secret.key"
    monkeypatch.setattr("config.SESSION_SECRET_KEY_FILE", str(key_file))
    monkeypatch.delenv("SPELLBOOK_SESSION_SECRET", raising=False)
    return key_file


class TestSettings:
    def test_default_values(self, isolated_secret_key):
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

    def test_session_secret_key_is_set(self, isolated_secret_key):
        from config import Settings
        s = Settings()
        assert isinstance(s.SESSION_SECRET_KEY, str)
        assert len(s.SESSION_SECRET_KEY) == 64

    def test_session_secret_key_from_env_var(self, monkeypatch):
        from config import Settings
        monkeypatch.setenv("SPELLBOOK_SESSION_SECRET", "my-custom-secret")
        assert Settings().SESSION_SECRET_KEY == "my-custom-secret"

    def test_session_secret_key_creates_file_when_absent(self, isolated_secret_key):
        from config import Settings
        key_file = isolated_secret_key
        s = Settings()
        key = s.SESSION_SECRET_KEY
        assert isinstance(key, str)
        assert len(key) == 64
        assert key_file.exists()
        assert key_file.read_text() == key
        assert stat.S_IMODE(key_file.stat().st_mode) == 0o600

    def test_session_secret_key_reuses_existing_file(self, isolated_secret_key):
        from config import Settings
        key_file = isolated_secret_key
        key_file.write_text("  existing-stable-secret\n")
        first = Settings().SESSION_SECRET_KEY
        second = Settings().SESSION_SECRET_KEY
        assert first == "existing-stable-secret"
        assert first == second
