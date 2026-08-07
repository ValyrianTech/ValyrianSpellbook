#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for webui.routers.actions."""
from unittest.mock import patch, MagicMock


class TestListActions:
    @patch("routers.actions.is_authenticated", return_value=False)
    def test_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/actions/", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.actions.is_authenticated", return_value=True)
    @patch("routers.actions.get_api_client")
    def test_list_with_actions(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_actions.return_value = ["a1", "a2"]
        mock_client.get_action_config.side_effect = lambda aid: {"id": aid, "type": "command"}
        mock_get_client.return_value = mock_client

        response = client.get("/actions/", follow_redirects=False)
        assert response.status_code == 200

    @patch("routers.actions.is_authenticated", return_value=True)
    @patch("routers.actions.get_api_client")
    def test_list_with_error_in_config(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_actions.return_value = ["a1"]
        mock_client.get_action_config.return_value = {"error": "fail"}
        mock_get_client.return_value = mock_client

        response = client.get("/actions/", follow_redirects=False)
        assert response.status_code == 200

    @patch("routers.actions.is_authenticated", return_value=True)
    @patch("routers.actions.get_api_client")
    def test_list_with_non_list_response(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_actions.return_value = {"error": "fail"}
        mock_get_client.return_value = mock_client

        response = client.get("/actions/", follow_redirects=False)
        assert response.status_code == 200


class TestNewAction:
    @patch("routers.actions.is_authenticated", return_value=False)
    def test_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/actions/new", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.actions.is_authenticated", return_value=True)
    def test_new_action_form(self, mock_auth, client):
        response = client.get("/actions/new", follow_redirects=False)
        assert response.status_code == 200


class TestViewAction:
    @patch("routers.actions.is_authenticated", return_value=False)
    def test_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/actions/my-action", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.actions.is_authenticated", return_value=True)
    @patch("routers.actions.get_api_client")
    def test_view_action(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_action_config.return_value = {"id": "my-action", "type": "command"}
        mock_get_client.return_value = mock_client

        response = client.get("/actions/my-action", follow_redirects=False)
        assert response.status_code == 200


class TestEditAction:
    @patch("routers.actions.is_authenticated", return_value=False)
    def test_edit_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/actions/my-action/edit", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.actions.is_authenticated", return_value=True)
    @patch("routers.actions.get_api_client")
    def test_edit_action_form(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_action_config.return_value = {"id": "my-action", "type": "command"}
        mock_get_client.return_value = mock_client

        response = client.get("/actions/my-action/edit", follow_redirects=False)
        assert response.status_code == 200


class TestSaveAction:
    @patch("routers.actions.is_authenticated", return_value=False)
    def test_save_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.post("/actions/my-action/save", data={"type": "command"}, follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.actions.is_authenticated", return_value=True)
    @patch("routers.actions.get_api_client")
    def test_save_success_redirects(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.save_action.return_value = {"success": True}
        mock_get_client.return_value = mock_client

        response = client.post("/actions/my-action/save", data={"type": "command", "command": "ls"}, follow_redirects=False)
        assert response.status_code == 303
        assert "/actions/my-action" in response.headers["location"]

    @patch("routers.actions.is_authenticated", return_value=True)
    @patch("routers.actions.get_api_client")
    def test_save_error_shows_form(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.save_action.return_value = {"error": "bad config"}
        mock_get_client.return_value = mock_client

        response = client.post("/actions/my-action/save", data={"type": "command"}, follow_redirects=False)
        assert response.status_code == 200


class TestDeleteAction:
    @patch("routers.actions.is_authenticated", return_value=False)
    def test_delete_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.post("/actions/my-action/delete", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.actions.is_authenticated", return_value=True)
    @patch("routers.actions.get_api_client")
    def test_delete_redirects_to_list(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        response = client.post("/actions/my-action/delete", follow_redirects=False)
        assert response.status_code == 303
        assert "/actions" in response.headers["location"]


class TestRunAction:
    @patch("routers.actions.is_authenticated", return_value=False)
    def test_run_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.post("/actions/my-action/run", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.actions.is_authenticated", return_value=True)
    @patch("routers.actions.get_api_client")
    def test_run_redirects_to_view(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        response = client.post("/actions/my-action/run", follow_redirects=False)
        assert response.status_code == 303
        assert "/actions/my-action" in response.headers["location"]
