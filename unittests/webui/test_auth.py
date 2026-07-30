#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for webui.auth helpers."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from auth import (
    get_api_client,
    is_authenticated,
    require_auth,
    validate_credentials,
    login_user,
    logout_user,
)


class TestGetApiClient:
    def test_with_credentials(self):
        request = MagicMock()
        request.session.get = MagicMock(side_effect=lambda key: {"api_key": "key", "api_secret": "secret"}.get(key))
        client = get_api_client(request)
        assert client.api_key == "key"
        assert client.api_secret == "secret"

    def test_without_credentials(self):
        request = MagicMock()
        request.session.get = MagicMock(return_value=None)
        client = get_api_client(request)
        assert client.api_key is None
        assert client.api_secret is None


class TestIsAuthenticated:
    def test_authenticated(self):
        request = MagicMock()
        request.session.get.return_value = True
        assert is_authenticated(request) is True

    def test_not_authenticated(self):
        request = MagicMock()
        request.session.get.return_value = False
        assert is_authenticated(request) is False

    def test_default_not_authenticated(self):
        request = MagicMock()
        request.session.get.return_value = None
        assert not is_authenticated(request)


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


class TestLoginUser:
    @patch("auth.validate_credentials", return_value=True)
    def test_successful_login(self, mock_validate):
        request = MagicMock()
        request.session = {}
        result = login_user(request, "key", "secret")
        assert result is True
        assert request.session["authenticated"] is True
        assert request.session["api_key"] == "key"
        assert request.session["api_secret"] == "secret"

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
        request.session = MagicMock()
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
        request.session.get.return_value = True
        import asyncio
        result = asyncio.run(view(request))
        assert result == {"success": True}
