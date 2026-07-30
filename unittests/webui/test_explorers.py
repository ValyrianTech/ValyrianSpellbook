#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for webui.routers.explorers."""
import pytest
from unittest.mock import patch, MagicMock


class TestListExplorers:
    @patch("routers.explorers.is_authenticated", return_value=False)
    def test_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/explorers/", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.explorers.is_authenticated", return_value=True)
    @patch("routers.explorers.get_api_client")
    def test_list_with_explorers(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_explorers.return_value = ["blockstream", "blockchain_info"]
        mock_client.get_explorer_config.side_effect = lambda eid: {"id": eid, "url": "http://example.com"}
        mock_get_client.return_value = mock_client

        response = client.get("/explorers/", follow_redirects=False)
        assert response.status_code == 200

    @patch("routers.explorers.is_authenticated", return_value=True)
    @patch("routers.explorers.get_api_client")
    def test_list_with_error_in_config(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_explorers.return_value = ["e1"]
        mock_client.get_explorer_config.return_value = {"error": "fail"}
        mock_get_client.return_value = mock_client

        response = client.get("/explorers/", follow_redirects=False)
        assert response.status_code == 200

    @patch("routers.explorers.is_authenticated", return_value=True)
    @patch("routers.explorers.get_api_client")
    def test_list_with_non_list_response(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_explorers.return_value = {"error": "fail"}
        mock_get_client.return_value = mock_client

        response = client.get("/explorers/", follow_redirects=False)
        assert response.status_code == 200


class TestNewExplorer:
    @patch("routers.explorers.is_authenticated", return_value=False)
    def test_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/explorers/new", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.explorers.is_authenticated", return_value=True)
    def test_new_explorer_form(self, mock_auth, client):
        response = client.get("/explorers/new", follow_redirects=False)
        assert response.status_code == 200


class TestViewExplorer:
    @patch("routers.explorers.is_authenticated", return_value=False)
    def test_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/explorers/blockstream", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.explorers.is_authenticated", return_value=True)
    @patch("routers.explorers.get_api_client")
    def test_view_explorer(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_explorer_config.return_value = {"id": "blockstream", "url": "https://blockstream.info"}
        mock_get_client.return_value = mock_client

        response = client.get("/explorers/blockstream", follow_redirects=False)
        assert response.status_code == 200


class TestEditExplorer:
    @patch("routers.explorers.is_authenticated", return_value=False)
    def test_edit_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/explorers/blockstream/edit", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.explorers.is_authenticated", return_value=True)
    @patch("routers.explorers.get_api_client")
    def test_edit_explorer_form(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_explorer_config.return_value = {"id": "blockstream", "url": "https://blockstream.info"}
        mock_get_client.return_value = mock_client

        response = client.get("/explorers/blockstream/edit", follow_redirects=False)
        assert response.status_code == 200


class TestSaveExplorer:
    @patch("routers.explorers.is_authenticated", return_value=False)
    def test_save_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.post("/explorers/blockstream/save", data={"url": "https://example.com"}, follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.explorers.is_authenticated", return_value=True)
    @patch("routers.explorers.get_api_client")
    def test_save_success_redirects(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.save_explorer.return_value = {"success": True}
        mock_get_client.return_value = mock_client

        response = client.post("/explorers/blockstream/save", data={"url": "https://example.com", "name": "test"}, follow_redirects=False)
        assert response.status_code == 303
        assert "/explorers/blockstream" in response.headers["location"]

    @patch("routers.explorers.is_authenticated", return_value=True)
    @patch("routers.explorers.get_api_client")
    def test_save_error_shows_form(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.save_explorer.return_value = {"error": "bad config"}
        mock_get_client.return_value = mock_client

        response = client.post("/explorers/blockstream/save", data={"url": "https://example.com"}, follow_redirects=False)
        assert response.status_code == 200


class TestDeleteExplorer:
    @patch("routers.explorers.is_authenticated", return_value=False)
    def test_delete_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.post("/explorers/blockstream/delete", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.explorers.is_authenticated", return_value=True)
    @patch("routers.explorers.get_api_client")
    def test_delete_redirects_to_list(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        response = client.post("/explorers/blockstream/delete", follow_redirects=False)
        assert response.status_code == 303
        assert "/explorers" in response.headers["location"]
