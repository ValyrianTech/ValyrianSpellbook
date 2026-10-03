#!/usr/bin/env python
"""Tests for webui.routers.triggers."""
import asyncio

from unittest.mock import MagicMock, patch

from routers import triggers as rt


class TestListTriggers:
    @patch("routers.triggers.is_authenticated", return_value=False)
    def test_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/triggers/", follow_redirects=False)
        assert response.status_code == 303
        assert "/login" in response.headers["location"]

    @patch("routers.triggers.is_authenticated", return_value=True)
    @patch("routers.triggers.get_api_client")
    def test_list_with_triggers(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_triggers.return_value = ["t1", "t2"]
        mock_client.get_trigger_config.side_effect = lambda tid: {"id": tid, "type": "manual"}
        mock_get_client.return_value = mock_client

        response = client.get("/triggers/", follow_redirects=False)
        assert response.status_code == 200

    @patch("routers.triggers.is_authenticated", return_value=True)
    @patch("routers.triggers.get_api_client")
    def test_list_with_error_in_config(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_triggers.return_value = ["t1"]
        mock_client.get_trigger_config.return_value = {"error": "not found"}
        mock_get_client.return_value = mock_client

        response = client.get("/triggers/", follow_redirects=False)
        assert response.status_code == 200

    @patch("routers.triggers.is_authenticated", return_value=True)
    @patch("routers.triggers.get_api_client")
    def test_list_with_non_list_response(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_triggers.return_value = {"error": "fail"}
        mock_get_client.return_value = mock_client

        response = client.get("/triggers/", follow_redirects=False)
        assert response.status_code == 200

    def test_list_masks_secret(self):
        mock_client = MagicMock()
        mock_client.get_triggers.return_value = ["t1"]
        mock_client.get_trigger_config.return_value = {"trigger_type": "manual", "secret": "s3cret"}
        mock_request = MagicMock()

        with patch.object(rt, "is_authenticated", return_value=True), \
                patch.object(rt, "get_api_client", return_value=mock_client), \
                patch.object(rt, "templates") as mock_templates:
            asyncio.run(rt.list_triggers(mock_request))

        context = mock_templates.TemplateResponse.call_args[0][2]
        assert context["triggers"][0]["config"]["secret"] == "********"

    def test_list_skips_error_config(self):
        mock_client = MagicMock()
        mock_client.get_triggers.return_value = ["t1"]
        mock_client.get_trigger_config.return_value = {"error": "not found"}
        mock_request = MagicMock()

        with patch.object(rt, "is_authenticated", return_value=True), \
                patch.object(rt, "get_api_client", return_value=mock_client), \
                patch.object(rt, "templates") as mock_templates:
            asyncio.run(rt.list_triggers(mock_request))

        context = mock_templates.TemplateResponse.call_args[0][2]
        assert context["triggers"] == []


class TestNewTrigger:
    @patch("routers.triggers.is_authenticated", return_value=False)
    def test_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/triggers/new", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.triggers.is_authenticated", return_value=True)
    def test_new_trigger_form(self, mock_auth, client):
        response = client.get("/triggers/new", follow_redirects=False)
        assert response.status_code == 200


class TestViewTrigger:
    @patch("routers.triggers.is_authenticated", return_value=False)
    def test_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/triggers/my-trigger", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.triggers.is_authenticated", return_value=True)
    @patch("routers.triggers.get_api_client")
    def test_view_trigger(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_trigger_config.return_value = {"id": "my-trigger", "type": "manual"}
        mock_get_client.return_value = mock_client

        response = client.get("/triggers/my-trigger", follow_redirects=False)
        assert response.status_code == 200

    @patch("routers.triggers.is_authenticated", return_value=True)
    @patch("routers.triggers.get_api_client")
    def test_view_trigger_masks_secret(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_trigger_config.return_value = {"id": "my-trigger", "type": "manual", "secret": "s3cret"}
        mock_get_client.return_value = mock_client

        response = client.get("/triggers/my-trigger", follow_redirects=False)
        assert response.status_code == 200
        assert "s3cret" not in response.text
        assert "********" in response.text


class TestEditTrigger:
    @patch("routers.triggers.is_authenticated", return_value=False)
    def test_edit_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/triggers/my-trigger/edit", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.triggers.is_authenticated", return_value=True)
    @patch("routers.triggers.get_api_client")
    def test_edit_trigger_form(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_trigger_config.return_value = {"id": "my-trigger", "type": "manual"}
        mock_get_client.return_value = mock_client

        response = client.get("/triggers/my-trigger/edit", follow_redirects=False)
        assert response.status_code == 200


class TestSaveTrigger:
    @patch("routers.triggers.is_authenticated", return_value=False)
    def test_save_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.post("/triggers/my-trigger/save", data={"type": "manual"}, follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.triggers.is_authenticated", return_value=True)
    @patch("routers.triggers.get_api_client")
    def test_save_success_redirects(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.save_trigger.return_value = {"success": True}
        mock_get_client.return_value = mock_client

        response = client.post("/triggers/my-trigger/save", data={"type": "manual", "name": "test"}, follow_redirects=False)
        assert response.status_code == 303
        assert "/triggers/my-trigger" in response.headers["location"]

    @patch("routers.triggers.is_authenticated", return_value=True)
    @patch("routers.triggers.get_api_client")
    def test_save_error_shows_form(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.save_trigger.return_value = {"error": "validation failed"}
        mock_get_client.return_value = mock_client

        response = client.post("/triggers/my-trigger/save", data={"type": "manual"}, follow_redirects=False)
        assert response.status_code == 200


class TestMaskSecret:
    def test_mask_secret_masks_truthy_secret(self):
        result = rt._mask_secret({"type": "manual", "secret": "s3cret"})
        assert result["secret"] == "********"
        assert result["type"] == "manual"

    def test_mask_secret_non_dict_unchanged(self):
        value = "not-a-dict"
        assert rt._mask_secret(value) == value

    def test_mask_secret_empty_secret_unchanged(self):
        config = {"type": "manual", "secret": ""}
        assert rt._mask_secret(config) == config


class TestDeleteTrigger:
    @patch("routers.triggers.is_authenticated", return_value=False)
    def test_delete_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.post("/triggers/my-trigger/delete", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.triggers.is_authenticated", return_value=True)
    @patch("routers.triggers.get_api_client")
    def test_delete_redirects_to_list(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        response = client.post("/triggers/my-trigger/delete", follow_redirects=False)
        assert response.status_code == 303
        assert "/triggers" in response.headers["location"]


class TestActivateTrigger:
    @patch("routers.triggers.is_authenticated", return_value=False)
    def test_activate_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.post("/triggers/my-trigger/activate", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.triggers.is_authenticated", return_value=True)
    @patch("routers.triggers.get_api_client")
    def test_activate_redirects_to_view(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        response = client.post("/triggers/my-trigger/activate", follow_redirects=False)
        assert response.status_code == 303
        assert "/triggers/my-trigger" in response.headers["location"]


class TestCheckTrigger:
    @patch("routers.triggers.is_authenticated", return_value=False)
    def test_check_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.post("/triggers/my-trigger/check", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.triggers.is_authenticated", return_value=True)
    @patch("routers.triggers.get_api_client")
    def test_check_redirects_to_view(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        response = client.post("/triggers/my-trigger/check", follow_redirects=False)
        assert response.status_code == 303
        assert "/triggers/my-trigger" in response.headers["location"]
