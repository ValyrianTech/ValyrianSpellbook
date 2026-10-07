#!/usr/bin/env python
"""Tests for webui.auth helpers."""
import stat
from pathlib import Path
from unittest.mock import MagicMock, patch

import auth
import pytest
from auth import (
    SessionStore,
    get_api_client,
    is_authenticated,
    login_user,
    logout_user,
    require_auth,
    validate_credentials,
)


@pytest.fixture(autouse=True)
def reset_session_store(tmp_path):
    """Reset the module-level session store before each test."""
    auth._SESSION_STORE = SessionStore(directory=str(tmp_path))
    yield
    auth._SESSION_STORE = SessionStore(directory=str(tmp_path))


class TestSessionStore:
    def test_create_and_get(self, tmp_path):
        store = SessionStore(directory=str(tmp_path))
        session_id = store.create("key", "secret")
        record = store.get(session_id)
        assert record is not None
        assert record["api_key"] == "key"
        assert record["api_secret"] == "secret"
        assert "created" in record

    def test_get_returns_none_for_falsy_id(self, tmp_path):
        store = SessionStore(directory=str(tmp_path))
        assert store.get(None) is None
        assert store.get("") is None

    def test_get_returns_none_for_unknown_id(self, tmp_path):
        store = SessionStore(directory=str(tmp_path))
        assert store.get("does-not-exist") is None

    def test_get_returns_none_for_corrupt_json(self, tmp_path):
        store = SessionStore(directory=str(tmp_path))
        session_id = store.create("key", "secret")
        path = Path(auth._session_file_path(str(tmp_path), session_id))
        path.write_text("{not valid json")
        assert store.get(session_id) is None

    def test_get_returns_none_for_non_dict_record(self, tmp_path):
        store = SessionStore(directory=str(tmp_path))
        session_id = store.create("key", "secret")
        path = Path(auth._session_file_path(str(tmp_path), session_id))
        path.write_text("[]")
        assert store.get(session_id) is None

    def test_get_returns_none_for_unreadable_file(self, tmp_path):
        store = SessionStore(directory=str(tmp_path))
        session_id = store.create("key", "secret")
        path = Path(auth._session_file_path(str(tmp_path), session_id))
        path.unlink()
        path.mkdir()
        assert store.get(session_id) is None

    def test_delete_removes_record(self, tmp_path):
        store = SessionStore(directory=str(tmp_path))
        session_id = store.create("key", "secret")
        store.delete(session_id)
        assert store.get(session_id) is None

    def test_delete_missing_id_is_noop(self, tmp_path):
        store = SessionStore(directory=str(tmp_path))
        store.delete("does-not-exist")
        store.delete(None)

    def test_ttl_expiry_purges_record(self, tmp_path):
        store = SessionStore(directory=str(tmp_path))
        with patch("auth.time.time", return_value=1000.0):
            session_id = store.create("key", "secret")
        path = Path(auth._session_file_path(str(tmp_path), session_id))
        assert path.exists()
        with patch("auth.time.time", return_value=1000.0 + auth.SESSION_TTL_SECONDS + 1):
            assert store.get(session_id) is None
        # The entry should have been purged from the store.
        assert not path.exists()
        assert store.get(session_id) is None

    def test_get_purges_record_without_created(self, tmp_path):
        store = SessionStore(directory=str(tmp_path))
        session_id = store.create("key", "secret")
        path = Path(auth._session_file_path(str(tmp_path), session_id))
        path.write_text('{"api_key": "key", "api_secret": "secret"}')
        assert store.get(session_id) is None
        assert not path.exists()

    def test_create_writes_file_with_0600_permissions(self, tmp_path):
        store = SessionStore(directory=str(tmp_path))
        session_id = store.create("key", "secret")
        path = Path(auth._session_file_path(str(tmp_path), session_id))
        assert path.exists()
        assert stat.S_IMODE(path.stat().st_mode) == 0o600

    def test_records_visible_across_store_instances(self, tmp_path):
        store_a = SessionStore(directory=str(tmp_path))
        session_id = store_a.create("key", "secret")
        store_b = SessionStore(directory=str(tmp_path))
        record = store_b.get(session_id)
        assert record is not None
        assert record["api_key"] == "key"
        assert record["api_secret"] == "secret"

    def test_get_returns_defensive_copy(self, tmp_path):
        store = SessionStore(directory=str(tmp_path))
        session_id = store.create("key", "secret")
        record = store.get(session_id)
        assert record is not None
        # Mutating the returned dict must not affect the stored record.
        record["api_key"] = "tampered"
        record["api_secret"] = "tampered"
        fresh = store.get(session_id)
        assert fresh is not None
        assert fresh["api_key"] == "key"
        assert fresh["api_secret"] == "secret"

    def test_get_filters_to_known_keys(self, tmp_path):
        store = SessionStore(directory=str(tmp_path))
        session_id = store.create("key", "secret")
        path = Path(auth._session_file_path(str(tmp_path), session_id))
        import json as _json
        data = _json.loads(path.read_text())
        data["extra"] = "should-be-hidden"
        path.write_text(_json.dumps(data))
        record = store.get(session_id)
        assert record is not None
        assert "extra" not in record
        assert set(record) == set(auth.SESSION_RECORD_KEYS)

    def test_atomic_write_failure_removes_temp_and_raises(self, tmp_path):
        store = SessionStore(directory=str(tmp_path))
        with patch("auth.os.replace", side_effect=OSError("boom")), \
                pytest.raises(OSError):
            store.create("key", "secret")
        assert list(tmp_path.iterdir()) == []


class TestGetApiClient:
    def test_with_credentials_from_store(self):
        request = MagicMock()
        session_id = auth._SESSION_STORE.create("key", "secret")
        request.session.get = MagicMock(side_effect=lambda key: {"session_id": session_id}.get(key))
        client = get_api_client(request)
        assert client.api_key == "key"
        assert client.api_secret == "secret"

    def test_without_credentials(self):
        request = MagicMock()
        request.session.get = MagicMock(return_value=None)
        client = get_api_client(request)
        assert client.api_key is None
        assert client.api_secret is None

    def test_with_unknown_session_id(self):
        request = MagicMock()
        request.session.get = MagicMock(return_value="unknown-id")
        client = get_api_client(request)
        assert client.api_key is None
        assert client.api_secret is None


class TestIsAuthenticated:
    def test_authenticated_with_valid_store_record(self):
        request = MagicMock()
        session_id = auth._SESSION_STORE.create("key", "secret")
        request.session.get = MagicMock(
            side_effect=lambda key, default=None: {
                "authenticated": True,
                "session_id": session_id,
            }.get(key, default)
        )
        assert is_authenticated(request) is True
        request.session.clear.assert_not_called()

    def test_authenticated_but_missing_store_record(self):
        request = MagicMock()
        request.session.get = MagicMock(
            side_effect=lambda key, default=None: {
                "authenticated": True,
                "session_id": "unknown-id",
            }.get(key, default)
        )
        assert is_authenticated(request) is False
        request.session.clear.assert_called_once()

    def test_authenticated_but_deleted_store_record(self):
        request = MagicMock()
        session_id = auth._SESSION_STORE.create("key", "secret")
        auth._SESSION_STORE.delete(session_id)
        request.session.get = MagicMock(
            side_effect=lambda key, default=None: {
                "authenticated": True,
                "session_id": session_id,
            }.get(key, default)
        )
        assert is_authenticated(request) is False
        request.session.clear.assert_called_once()

    def test_authenticated_but_missing_session_id(self):
        request = MagicMock()
        request.session.get = MagicMock(
            side_effect=lambda key, default=None: {
                "authenticated": True,
                "session_id": None,
            }.get(key, default)
        )
        assert is_authenticated(request) is False
        request.session.clear.assert_called_once()

    def test_not_authenticated_no_cleanup(self):
        request = MagicMock()
        request.session.get = MagicMock(
            side_effect=lambda key, default=None: {
                "authenticated": False,
            }.get(key, default)
        )
        assert is_authenticated(request) is False
        request.session.clear.assert_not_called()

    def test_default_not_authenticated_no_cleanup(self):
        request = MagicMock()
        request.session.get = MagicMock(
            side_effect=lambda key, default=None: {
                "authenticated": None,
            }.get(key, default)
        )
        assert is_authenticated(request) is False
        request.session.clear.assert_not_called()

    def test_cleanup_failure_still_returns_false(self):
        request = MagicMock()
        request.session.get = MagicMock(
            side_effect=lambda key, default=None: {
                "authenticated": True,
                "session_id": "unknown-id",
            }.get(key, default)
        )
        request.session.clear = MagicMock(side_effect=Exception("read-only session"))
        assert is_authenticated(request) is False


class TestValidateCredentials:
    @patch("auth.get_key", return_value="test-key")
    @patch("auth.get_secret", return_value="test-secret")
    def test_valid_credentials(self, mock_secret, mock_key):
        assert validate_credentials("test-key", "test-secret") is True

    @patch("auth.get_key", return_value="test-key")
    @patch("auth.get_secret", return_value="test-secret")
    def test_wrong_key(self, mock_secret, mock_key):
        assert validate_credentials("wrong-key", "test-secret") is False

    @patch("auth.get_key", return_value="test-key")
    @patch("auth.get_secret", return_value="test-secret")
    def test_wrong_secret(self, mock_secret, mock_key):
        assert validate_credentials("test-key", "wrong-secret") is False

    @patch("auth.get_key", return_value="test-key")
    @patch("auth.get_secret", return_value="test-secret")
    def test_both_wrong(self, mock_secret, mock_key):
        assert validate_credentials("wrong", "wrong") is False

    @patch(
        "auth.hmac.compare_digest",
        side_effect=lambda a, b: a == b,
    )
    @patch("auth.get_key", return_value="test-key")
    @patch("auth.get_secret", return_value="test-secret")
    def test_uses_compare_digest(self, mock_secret, mock_key, mock_compare_digest):
        assert validate_credentials("test-key", "test-secret") is True
        assert validate_credentials("wrong-key", "wrong-secret") is False
        assert mock_compare_digest.call_count == 4


class TestLoginUser:
    @patch("auth.validate_credentials", return_value=True)
    def test_successful_login(self, mock_validate):
        request = MagicMock()
        request.session = {}
        result = login_user(request, "key", "secret")
        assert result is True
        assert request.session["authenticated"] is True
        assert "session_id" in request.session
        assert "api_key" not in request.session
        assert "api_secret" not in request.session

    @patch("auth.validate_credentials", return_value=False)
    def test_failed_login(self, mock_validate):
        request = MagicMock()
        request.session = {}
        result = login_user(request, "key", "secret")
        assert result is False
        assert "authenticated" not in request.session


class TestLogoutUser:
    def test_logout_clears_session(self):
        request = MagicMock()
        session_id = auth._SESSION_STORE.create("key", "secret")
        request.session = MagicMock()
        request.session.get.return_value = session_id
        assert auth._SESSION_STORE.get(session_id) is not None
        logout_user(request)
        request.session.clear.assert_called_once()
        assert auth._SESSION_STORE.get(session_id) is None

    def test_logout_without_session_id_is_safe(self):
        request = MagicMock()
        request.session = MagicMock()
        request.session.get.return_value = None
        logout_user(request)
        request.session.clear.assert_called_once()


class TestRequireAuth:
    def test_redirects_when_not_authenticated(self):
        @require_auth
        async def view(request):
            return {"success": True}

        request = MagicMock()
        request.session.get.return_value = False
        import asyncio
        result = asyncio.run(view(request))
        # Should return a RedirectResponse
        assert hasattr(result, "status_code")
        assert result.status_code == 303

    def test_allows_when_authenticated(self):
        @require_auth
        async def view(request):
            return {"success": True}

        request = MagicMock()
        session_id = auth._SESSION_STORE.create("key", "secret")
        request.session.get = MagicMock(
            side_effect=lambda key, default=None: {
                "authenticated": True,
                "session_id": session_id,
            }.get(key, default)
        )
        import asyncio
        result = asyncio.run(view(request))
        assert result == {"success": True}
