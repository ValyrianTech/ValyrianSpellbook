#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for webui.routers.dashboard."""
from unittest.mock import patch, MagicMock


class TestDashboardIndex:
    @patch("routers.dashboard.is_authenticated", return_value=False)
    def test_index_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 303
        assert "/login" in response.headers["location"]

    @patch("routers.dashboard.is_authenticated", return_value=True)
    @patch("routers.dashboard.get_api_client")
    def test_index_when_authenticated(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_triggers.return_value = ["t1", "t2"]
        mock_client.get_actions.return_value = ["a1"]
        mock_client.get_llms.return_value = ["llm1", "llm2", "llm3"]
        mock_client.get_explorers.return_value = ["e1"]
        mock_client.ping.return_value = {"success": True}
        mock_client.get_latest_block.return_value = {"height": 800000}
        mock_get_client.return_value = mock_client

        response = client.get("/", follow_redirects=False)
        assert response.status_code == 200

    @patch("routers.dashboard.is_authenticated", return_value=True)
    @patch("routers.dashboard.get_api_client")
    def test_index_handles_error_responses(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_triggers.return_value = {"error": "fail"}
        mock_client.get_actions.return_value = {"error": "fail"}
        mock_client.get_llms.return_value = {"error": "fail"}
        mock_client.get_explorers.return_value = {"error": "fail"}
        mock_client.ping.return_value = {}
        mock_client.get_latest_block.return_value = {}
        mock_get_client.return_value = mock_client

        response = client.get("/", follow_redirects=False)
        assert response.status_code == 200


class TestLoginPage:
    @patch("routers.dashboard.is_authenticated", return_value=False)
    def test_login_page_when_not_authenticated(self, mock_auth, client):
        response = client.get("/login", follow_redirects=False)
        assert response.status_code == 200

    @patch("routers.dashboard.is_authenticated", return_value=True)
    def test_login_page_redirects_when_authenticated(self, mock_auth, client):
        response = client.get("/login", follow_redirects=False)
        assert response.status_code == 303
        assert "/" in response.headers["location"]


class TestLoginPost:
    @patch("routers.dashboard.login_user", return_value=True)
    def test_login_success_redirects(self, mock_login, client):
        response = client.post("/login", data={"api_key": "key", "api_secret": "secret"}, follow_redirects=False)
        assert response.status_code == 303
        assert "/" in response.headers["location"]

    @patch("routers.dashboard.login_user", return_value=False)
    def test_login_failure_shows_error(self, mock_login, client):
        response = client.post("/login", data={"api_key": "bad", "api_secret": "bad"}, follow_redirects=False)
        assert response.status_code == 200


class TestLogout:
    @patch("routers.dashboard.logout_user")
    def test_logout_redirects_to_login(self, mock_logout, client):
        response = client.get("/logout", follow_redirects=False)
        assert response.status_code == 303
        assert "/login" in response.headers["location"]
