#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for webui.routers.llms."""
from unittest.mock import patch, MagicMock


class TestListLLMs:
    @patch("routers.llms.is_authenticated", return_value=False)
    def test_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/llms/", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.llms.is_authenticated", return_value=True)
    @patch("routers.llms.get_api_client")
    def test_list_with_llms(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_llms.return_value = ["OpenAI:gpt-4o", "Anthropic:claude-3"]
        mock_client.get_llm_config.side_effect = lambda lid: {"id": lid, "type": "OpenAI"}
        mock_get_client.return_value = mock_client

        response = client.get("/llms/", follow_redirects=False)
        assert response.status_code == 200

    @patch("routers.llms.is_authenticated", return_value=True)
    @patch("routers.llms.get_api_client")
    def test_list_with_error_in_config(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_llms.return_value = ["llm1"]
        mock_client.get_llm_config.return_value = {"error": "fail"}
        mock_get_client.return_value = mock_client

        response = client.get("/llms/", follow_redirects=False)
        assert response.status_code == 200

    @patch("routers.llms.is_authenticated", return_value=True)
    @patch("routers.llms.get_api_client")
    def test_list_with_non_list_response(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_llms.return_value = {"error": "fail"}
        mock_get_client.return_value = mock_client

        response = client.get("/llms/", follow_redirects=False)
        assert response.status_code == 200


class TestNewLLM:
    @patch("routers.llms.is_authenticated", return_value=False)
    def test_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/llms/new", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.llms.is_authenticated", return_value=True)
    def test_new_llm_form(self, mock_auth, client):
        response = client.get("/llms/new", follow_redirects=False)
        assert response.status_code == 200


class TestViewLLM:
    @patch("routers.llms.is_authenticated", return_value=False)
    def test_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/llms/OpenAI:gpt-4o", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.llms.is_authenticated", return_value=True)
    @patch("routers.llms.get_api_client")
    def test_view_llm(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_llm_config.return_value = {"id": "OpenAI:gpt-4o", "type": "OpenAI"}
        mock_get_client.return_value = mock_client

        response = client.get("/llms/OpenAI:gpt-4o", follow_redirects=False)
        assert response.status_code == 200

    @patch("routers.llms.is_authenticated", return_value=True)
    @patch("routers.llms.get_api_client")
    def test_view_llm_edit_route(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_llm_config.return_value = {"id": "OpenAI:gpt-4o", "type": "OpenAI"}
        mock_get_client.return_value = mock_client

        response = client.get("/llms/OpenAI:gpt-4o/edit", follow_redirects=False)
        assert response.status_code == 200


class TestSaveLLM:
    @patch("routers.llms.is_authenticated", return_value=False)
    def test_save_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.post("/llms/test-llm/save", data={"type": "OpenAI"}, follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.llms.is_authenticated", return_value=True)
    @patch("routers.llms.get_api_client")
    def test_save_success_redirects(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.save_llm_config.return_value = {"success": True}
        mock_get_client.return_value = mock_client

        response = client.post("/llms/test-llm/save", data={"type": "OpenAI", "name": "gpt"}, follow_redirects=False)
        assert response.status_code == 303
        assert "/llms/test-llm" in response.headers["location"]

    @patch("routers.llms.is_authenticated", return_value=True)
    @patch("routers.llms.get_api_client")
    def test_save_error_shows_form(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.save_llm_config.return_value = {"error": "bad config"}
        mock_get_client.return_value = mock_client

        response = client.post("/llms/test-llm/save", data={"type": "OpenAI"}, follow_redirects=False)
        assert response.status_code == 200


class TestDeleteLLM:
    @patch("routers.llms.is_authenticated", return_value=False)
    def test_delete_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.post("/llms/test-llm/delete", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.llms.is_authenticated", return_value=True)
    @patch("routers.llms.get_api_client")
    def test_delete_redirects_to_list(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        response = client.post("/llms/test-llm/delete", follow_redirects=False)
        assert response.status_code == 303
        assert "/llms" in response.headers["location"]
