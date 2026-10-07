#!/usr/bin/env python
"""Tests for webui.config Settings."""
import os
import stat
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def isolated_secret_key(monkeypatch, tmp_path):
    """Point the persisted key file at tmp_path and clear the env var."""
    key_file = tmp_path / "session_secret.key"
    monkeypatch.setattr("config.SESSION_SECRET_KEY_FILE", str(key_file))
    monkeypatch.delenv("SPELLBOOK_SESSION_SECRET", raising=False)
    return key_file


class TestSettings:
    def test_default_values(self, isolated_secret_key, monkeypatch):
        from config import Settings
        monkeypatch.delenv("SPELLBOOK_WEBUI_DEBUG", raising=False)
        monkeypatch.delenv("SPELLBOOK_SESSION_HTTPS_ONLY", raising=False)
        s = Settings()
        assert s.WEBUI_HOST == "0.0.0.0"
        assert s.WEBUI_PORT == 5001
        assert s.DEBUG is False
        assert s.SESSION_COOKIE_HTTPS_ONLY is False
        assert isinstance(s.SESSION_SECRET_KEY, str)
        assert len(s.SESSION_SECRET_KEY) == 64  # 32 bytes hex = 64 chars

    @pytest.mark.parametrize("value", ["1", "true", "yes", "on", "TRUE", "Yes", "ON"])
    def test_debug_true_for_truthy_env(self, monkeypatch, value):
        from config import Settings
        monkeypatch.setenv("SPELLBOOK_WEBUI_DEBUG", value)
        assert Settings().DEBUG is True

    @pytest.mark.parametrize("value", ["0", "false", "no", "off", "", "random"])
    def test_debug_false_for_other_env(self, monkeypatch, value):
        from config import Settings
        monkeypatch.setenv("SPELLBOOK_WEBUI_DEBUG", value)
        assert Settings().DEBUG is False

    def test_debug_false_when_env_unset(self, monkeypatch):
        from config import Settings
        monkeypatch.delenv("SPELLBOOK_WEBUI_DEBUG", raising=False)
        assert Settings().DEBUG is False

    @pytest.mark.parametrize("value", ["1", "true", "yes", "on", "TRUE", "Yes", "ON"])
    def test_session_cookie_https_only_true_for_truthy_env(self, monkeypatch, value):
        from config import Settings
        monkeypatch.setenv("SPELLBOOK_SESSION_HTTPS_ONLY", value)
        assert Settings().SESSION_COOKIE_HTTPS_ONLY is True

    @pytest.mark.parametrize("value", ["0", "false", "no", "off", "", "random"])
    def test_session_cookie_https_only_false_for_other_env(self, monkeypatch, value):
        from config import Settings
        monkeypatch.setenv("SPELLBOOK_SESSION_HTTPS_ONLY", value)
        assert Settings().SESSION_COOKIE_HTTPS_ONLY is False

    def test_session_cookie_https_only_false_when_env_unset(self, monkeypatch):
        from config import Settings
        monkeypatch.delenv("SPELLBOOK_SESSION_HTTPS_ONLY", raising=False)
        assert Settings().SESSION_COOKIE_HTTPS_ONLY is False

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

    def test_session_secret_key_race_fallback_returns_winner(self, isolated_secret_key):
        from config import Settings
        isolated_secret_key.write_text("winner-key")
        with patch("config.os.open", side_effect=FileExistsError):
            assert Settings().SESSION_SECRET_KEY == "winner-key"

    def test_session_secret_key_retries_until_secret_appears(self, isolated_secret_key):
        from config import Settings
        reads = iter(["", "late-key"])
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.read.side_effect = lambda: next(reads)
        sleep_mock = MagicMock()
        with patch("config.os.open", side_effect=FileExistsError), \
             patch("builtins.open", return_value=mock_file), \
             patch("config.time.sleep", sleep_mock):
            assert Settings().SESSION_SECRET_KEY == "late-key"
        assert sleep_mock.call_count >= 1

    def test_session_secret_key_exhausted_retries_regenerates(self, isolated_secret_key):
        from config import Settings
        key_file = isolated_secret_key
        real_open = os.open

        def fake_open(path, *args, **kwargs):
            if path == str(key_file):
                raise FileExistsError
            return real_open(path, *args, **kwargs)

        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.read.return_value = ""
        sleep_mock = MagicMock()
        with patch("config.os.open", side_effect=fake_open), \
             patch("builtins.open", return_value=mock_file), \
             patch("config.time.sleep", sleep_mock):
            secret = Settings().SESSION_SECRET_KEY

        assert isinstance(secret, str)
        assert len(secret) == 64
        assert key_file.read_text() == secret
        assert stat.S_IMODE(key_file.stat().st_mode) == 0o600
        assert sleep_mock.call_count == 10

    def test_session_secret_key_fails_closed_on_empty_secret(self, isolated_secret_key):
        from config import Settings
        with patch("config.secrets.token_hex", return_value=""), \
             pytest.raises(RuntimeError, match="non-empty session secret"):
            _ = Settings().SESSION_SECRET_KEY

    def test_atomic_write_secret_writes_file(self, isolated_secret_key):
        from config import _atomic_write_secret
        key_file = isolated_secret_key
        _atomic_write_secret(str(key_file), "written-secret")
        assert key_file.read_text() == "written-secret"
        assert stat.S_IMODE(key_file.stat().st_mode) == 0o600

    def test_atomic_write_secret_removes_temp_file_on_failure(self, isolated_secret_key):
        from config import _atomic_write_secret
        key_file = isolated_secret_key
        key_dir = key_file.parent
        with patch("config.os.replace", side_effect=OSError("boom")), \
             pytest.raises(OSError):
            _atomic_write_secret(str(key_file), "written-secret")
        assert not key_file.exists()
        assert list(key_dir.iterdir()) == []
