#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for webui.api_client SpellbookAPIClient."""
import pytest
from unittest.mock import patch, MagicMock
import requests

from api_client import SpellbookAPIClient


class TestSpellbookAPIClientInit:
    def test_default_init(self):
        with patch("api_client.settings") as mock_settings:
            mock_settings.SPELLBOOK_API_URL = "http://localhost:8080"
            c = SpellbookAPIClient()
            assert c.base_url == "http://localhost:8080"
            assert c.api_key is None
            assert c.api_secret is None

    def test_init_with_credentials(self):
        with patch("api_client.settings") as mock_settings:
            mock_settings.SPELLBOOK_API_URL = "http://localhost:8080"
            c = SpellbookAPIClient(api_key="key123", api_secret="secret123")
            assert c.api_key == "key123"
            assert c.api_secret == "secret123"


class TestGetAuthHeaders:
    def test_no_credentials_returns_empty(self):
        with patch("api_client.settings") as mock_settings:
            mock_settings.SPELLBOOK_API_URL = "http://localhost:8080"
            c = SpellbookAPIClient()
            headers = c._get_auth_headers()
            assert headers == {}

    def test_with_credentials_returns_headers(self):
        with patch("api_client.settings") as mock_settings:
            mock_settings.SPELLBOOK_API_URL = "http://localhost:8080"
            c = SpellbookAPIClient(api_key="key123", api_secret="dGVzdA==")
            headers = c._get_auth_headers(data={"test": "data"})
            assert headers["API_Key"] == "key123"
            assert "API_Sign" in headers
            assert "API_Nonce" in headers
            assert headers["Content-Type"] == "application/json"


class TestRequest:
    def test_get_request(self):
        with patch("api_client.settings") as mock_settings:
            mock_settings.SPELLBOOK_API_URL = "http://localhost:8080"
            c = SpellbookAPIClient()
            mock_resp = MagicMock()
            mock_resp.text = '{"result": "ok"}'
            mock_resp.json.return_value = {"result": "ok"}
            mock_resp.raise_for_status = MagicMock()
            with patch("api_client.requests.get", return_value=mock_resp) as mock_get:
                result = c._request("GET", "/spellbook/ping")
                assert result == {"result": "ok"}
                mock_get.assert_called_once()

    def test_post_request(self):
        with patch("api_client.settings") as mock_settings:
            mock_settings.SPELLBOOK_API_URL = "http://localhost:8080"
            c = SpellbookAPIClient()
            mock_resp = MagicMock()
            mock_resp.text = '{"result": "saved"}'
            mock_resp.json.return_value = {"result": "saved"}
            mock_resp.raise_for_status = MagicMock()
            with patch("api_client.requests.post", return_value=mock_resp) as mock_post:
                result = c._request("POST", "/spellbook/llms/test", data={"key": "val"})
                assert result == {"result": "saved"}
                mock_post.assert_called_once()

    def test_delete_request(self):
        with patch("api_client.settings") as mock_settings:
            mock_settings.SPELLBOOK_API_URL = "http://localhost:8080"
            c = SpellbookAPIClient()
            mock_resp = MagicMock()
            mock_resp.text = '{"result": "deleted"}'
            mock_resp.json.return_value = {"result": "deleted"}
            mock_resp.raise_for_status = MagicMock()
            with patch("api_client.requests.delete", return_value=mock_resp) as mock_delete:
                result = c._request("DELETE", "/spellbook/llms/test")
                assert result == {"result": "deleted"}
                mock_delete.assert_called_once()

    def test_unsupported_method(self):
        with patch("api_client.settings") as mock_settings:
            mock_settings.SPELLBOOK_API_URL = "http://localhost:8080"
            c = SpellbookAPIClient()
            with pytest.raises(ValueError, match="Unsupported HTTP method"):
                c._request("PUT", "/spellbook/test")

    def test_request_exception_returns_error(self):
        with patch("api_client.settings") as mock_settings:
            mock_settings.SPELLBOOK_API_URL = "http://localhost:8080"
            c = SpellbookAPIClient()
            with patch("api_client.requests.get", side_effect=requests.exceptions.ConnectionError("fail")):
                result = c._request("GET", "/spellbook/ping")
                assert "error" in result
                assert "fail" in result["error"]

    def test_empty_response_returns_empty_dict(self):
        with patch("api_client.settings") as mock_settings:
            mock_settings.SPELLBOOK_API_URL = "http://localhost:8080"
            c = SpellbookAPIClient()
            mock_resp = MagicMock()
            mock_resp.text = ""
            mock_resp.raise_for_status = MagicMock()
            with patch("api_client.requests.get", return_value=mock_resp):
                result = c._request("GET", "/spellbook/ping")
                assert result == {}

    def test_authenticated_request_uses_auth_headers(self):
        with patch("api_client.settings") as mock_settings:
            mock_settings.SPELLBOOK_API_URL = "http://localhost:8080"
            c = SpellbookAPIClient(api_key="key", api_secret="dGVzdA==")
            mock_resp = MagicMock()
            mock_resp.text = '{"ok": true}'
            mock_resp.json.return_value = {"ok": True}
            mock_resp.raise_for_status = MagicMock()
            with patch("api_client.requests.post", return_value=mock_resp) as mock_post:
                c._request("POST", "/test", data={"a": 1}, authenticate=True)
                call_kwargs = mock_post.call_args
                headers = call_kwargs[1]["headers"]
                assert "API_Key" in headers
                assert "API_Sign" in headers


class TestAPIMethods:
    """Test that each API method calls _request with correct args."""

    def setup_method(self):
        self.patcher = patch("api_client.settings")
        self.mock_settings = self.patcher.start()
        self.mock_settings.SPELLBOOK_API_URL = "http://localhost:8080"
        self.client = SpellbookAPIClient()

    def teardown_method(self):
        self.patcher.stop()

    @patch.object(SpellbookAPIClient, "_request")
    def test_ping(self, mock_req):
        self.client.ping()
        mock_req.assert_called_once_with("GET", "/spellbook/ping")

    @patch.object(SpellbookAPIClient, "_request")
    def test_get_llms(self, mock_req):
        self.client.get_llms()
        mock_req.assert_called_once_with("GET", "/spellbook/llms")

    @patch.object(SpellbookAPIClient, "_request")
    def test_get_llm_config(self, mock_req):
        self.client.get_llm_config("OpenAI:gpt-4o")
        mock_req.assert_called_once_with("GET", "/spellbook/llms/OpenAI:gpt-4o")

    @patch.object(SpellbookAPIClient, "_request")
    def test_save_llm_config(self, mock_req):
        config = {"name": "test"}
        self.client.save_llm_config("test-llm", config)
        mock_req.assert_called_once_with("POST", "/spellbook/llms/test-llm", data=config, authenticate=True)

    @patch.object(SpellbookAPIClient, "_request")
    def test_delete_llm(self, mock_req):
        self.client.delete_llm("test-llm")
        mock_req.assert_called_once_with("DELETE", "/spellbook/llms/test-llm", authenticate=True)

    @patch.object(SpellbookAPIClient, "_request")
    def test_get_explorers(self, mock_req):
        self.client.get_explorers()
        mock_req.assert_called_once_with("GET", "/spellbook/explorers")

    @patch.object(SpellbookAPIClient, "_request")
    def test_get_explorer_config(self, mock_req):
        self.client.get_explorer_config("blockstream")
        mock_req.assert_called_once_with("GET", "/spellbook/explorers/blockstream", authenticate=True)

    @patch.object(SpellbookAPIClient, "_request")
    def test_save_explorer(self, mock_req):
        config = {"url": "http://example.com"}
        self.client.save_explorer("test-exp", config)
        mock_req.assert_called_once_with("POST", "/spellbook/explorers/test-exp", data=config, authenticate=True)

    @patch.object(SpellbookAPIClient, "_request")
    def test_delete_explorer(self, mock_req):
        self.client.delete_explorer("test-exp")
        mock_req.assert_called_once_with("DELETE", "/spellbook/explorers/test-exp", authenticate=True)

    @patch.object(SpellbookAPIClient, "_request")
    def test_get_triggers(self, mock_req):
        self.client.get_triggers()
        mock_req.assert_called_once_with("GET", "/spellbook/triggers")

    @patch.object(SpellbookAPIClient, "_request")
    def test_get_trigger_config(self, mock_req):
        self.client.get_trigger_config("test-trigger")
        mock_req.assert_called_once_with("GET", "/spellbook/triggers/test-trigger", authenticate=True)

    @patch.object(SpellbookAPIClient, "_request")
    def test_save_trigger(self, mock_req):
        config = {"type": "manual"}
        self.client.save_trigger("test-trigger", config)
        mock_req.assert_called_once_with("POST", "/spellbook/triggers/test-trigger", data=config, authenticate=True)

    @patch.object(SpellbookAPIClient, "_request")
    def test_delete_trigger(self, mock_req):
        self.client.delete_trigger("test-trigger")
        mock_req.assert_called_once_with("DELETE", "/spellbook/triggers/test-trigger", authenticate=True)

    @patch.object(SpellbookAPIClient, "_request")
    def test_activate_trigger(self, mock_req):
        self.client.activate_trigger("test-trigger")
        mock_req.assert_called_once_with("GET", "/spellbook/triggers/test-trigger/activate", authenticate=True)

    @patch.object(SpellbookAPIClient, "_request")
    def test_check_trigger(self, mock_req):
        self.client.check_trigger("test-trigger")
        mock_req.assert_called_once_with("GET", "/spellbook/triggers/test-trigger/check", authenticate=True)

    @patch.object(SpellbookAPIClient, "_request")
    def test_check_all_triggers(self, mock_req):
        self.client.check_all_triggers()
        mock_req.assert_called_once_with("GET", "/spellbook/check_triggers", authenticate=True)

    @patch.object(SpellbookAPIClient, "_request")
    def test_get_actions(self, mock_req):
        self.client.get_actions()
        mock_req.assert_called_once_with("GET", "/spellbook/actions")

    @patch.object(SpellbookAPIClient, "_request")
    def test_get_action_config(self, mock_req):
        self.client.get_action_config("test-action")
        mock_req.assert_called_once_with("GET", "/spellbook/actions/test-action", authenticate=True)

    @patch.object(SpellbookAPIClient, "_request")
    def test_save_action(self, mock_req):
        config = {"type": "command"}
        self.client.save_action("test-action", config)
        mock_req.assert_called_once_with("POST", "/spellbook/actions/test-action", data=config, authenticate=True)

    @patch.object(SpellbookAPIClient, "_request")
    def test_delete_action(self, mock_req):
        self.client.delete_action("test-action")
        mock_req.assert_called_once_with("DELETE", "/spellbook/actions/test-action", authenticate=True)

    @patch.object(SpellbookAPIClient, "_request")
    def test_run_action(self, mock_req):
        self.client.run_action("test-action")
        mock_req.assert_called_once_with("GET", "/spellbook/actions/test-action/run", authenticate=True)

    @patch.object(SpellbookAPIClient, "_request")
    def test_get_reveal(self, mock_req):
        self.client.get_reveal("test-action")
        mock_req.assert_called_once_with("GET", "/spellbook/actions/test-action/reveal")

    @patch.object(SpellbookAPIClient, "_request")
    def test_get_latest_block(self, mock_req):
        self.client.get_latest_block()
        mock_req.assert_called_once_with("GET", "/spellbook/blocks/latest")

    @patch.object(SpellbookAPIClient, "_request")
    def test_get_block_by_height(self, mock_req):
        self.client.get_block_by_height(800000)
        mock_req.assert_called_once_with("GET", "/spellbook/blocks/800000")

    @patch.object(SpellbookAPIClient, "_request")
    def test_get_block_by_hash(self, mock_req):
        self.client.get_block_by_hash("abc123def")
        mock_req.assert_called_once_with("GET", "/spellbook/blocks/abc123def")

    @patch.object(SpellbookAPIClient, "_request")
    def test_get_transaction(self, mock_req):
        self.client.get_transaction("txid123")
        mock_req.assert_called_once_with("GET", "/spellbook/transactions/txid123")

    @patch.object(SpellbookAPIClient, "_request")
    def test_get_prime_input_address(self, mock_req):
        self.client.get_prime_input_address("txid123")
        mock_req.assert_called_once_with("GET", "/spellbook/transactions/txid123/prime_input")

    @patch.object(SpellbookAPIClient, "_request")
    def test_get_balance(self, mock_req):
        self.client.get_balance("bc1qexample")
        mock_req.assert_called_once_with("GET", "/spellbook/addresses/bc1qexample/balance")

    @patch.object(SpellbookAPIClient, "_request")
    def test_get_transactions(self, mock_req):
        self.client.get_transactions("bc1qexample")
        mock_req.assert_called_once_with("GET", "/spellbook/addresses/bc1qexample/transactions")

    @patch.object(SpellbookAPIClient, "_request")
    def test_get_utxos(self, mock_req):
        self.client.get_utxos("bc1qexample", confirmations=3)
        mock_req.assert_called_once_with("GET", "/spellbook/addresses/bc1qexample/utxos?confirmations=3")

    @patch.object(SpellbookAPIClient, "_request")
    def test_get_logs(self, mock_req):
        self.client.get_logs("error")
        mock_req.assert_called_once_with("GET", "/spellbook/logs/error", authenticate=True)
