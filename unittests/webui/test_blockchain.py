#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for webui.routers.blockchain."""
from unittest.mock import patch, MagicMock


class TestBlockchainIndex:
    @patch("routers.blockchain.is_authenticated", return_value=False)
    def test_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/blockchain/", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.blockchain.is_authenticated", return_value=True)
    @patch("routers.blockchain.get_api_client")
    def test_blockchain_index(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_latest_block.return_value = {"height": 800000, "hash": "abc123"}
        mock_get_client.return_value = mock_client

        response = client.get("/blockchain/", follow_redirects=False)
        assert response.status_code == 200


class TestViewBlock:
    @patch("routers.blockchain.is_authenticated", return_value=False)
    def test_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/blockchain/block/800000", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.blockchain.is_authenticated", return_value=True)
    @patch("routers.blockchain.get_api_client")
    def test_view_block_by_height(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_block_by_height.return_value = {"height": 800000, "hash": "abc"}
        mock_get_client.return_value = mock_client

        response = client.get("/blockchain/block/800000", follow_redirects=False)
        assert response.status_code == 200
        mock_client.get_block_by_height.assert_called_once_with(800000)

    @patch("routers.blockchain.is_authenticated", return_value=True)
    @patch("routers.blockchain.get_api_client")
    def test_view_block_by_hash(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_block_by_hash.return_value = {"height": 800000, "hash": "abcdef1234567890"}
        mock_get_client.return_value = mock_client

        response = client.get("/blockchain/block/abcdef1234567890", follow_redirects=False)
        assert response.status_code == 200
        mock_client.get_block_by_hash.assert_called_once_with("abcdef1234567890")


class TestViewTransaction:
    @patch("routers.blockchain.is_authenticated", return_value=False)
    def test_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/blockchain/tx/abc123", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.blockchain.is_authenticated", return_value=True)
    @patch("routers.blockchain.get_api_client")
    def test_view_transaction(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_transaction.return_value = {"txid": "abc123", "value": 1.5}
        mock_client.get_prime_input_address.return_value = {"address": "bc1qexample"}
        mock_get_client.return_value = mock_client

        response = client.get("/blockchain/tx/abc123", follow_redirects=False)
        assert response.status_code == 200


class TestViewAddress:
    @patch("routers.blockchain.is_authenticated", return_value=False)
    def test_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.get("/blockchain/address/bc1qexample", follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.blockchain.is_authenticated", return_value=True)
    @patch("routers.blockchain.get_api_client")
    def test_view_address(self, mock_get_client, mock_auth, client):
        mock_client = MagicMock()
        mock_client.get_balance.return_value = {"balance": 100000}
        mock_client.get_transactions.return_value = []
        mock_client.get_utxos.return_value = []
        mock_get_client.return_value = mock_client

        response = client.get("/blockchain/address/bc1qexample", follow_redirects=False)
        assert response.status_code == 200


class TestSearch:
    @patch("routers.blockchain.is_authenticated", return_value=False)
    def test_search_redirects_when_not_authenticated(self, mock_auth, client):
        response = client.post("/blockchain/search", data={"query": "800000"}, follow_redirects=False)
        assert response.status_code == 303

    @patch("routers.blockchain.is_authenticated", return_value=True)
    def test_search_by_txid_or_hash(self, mock_auth, client):
        query = "a" * 64  # 64-char hex string
        response = client.post("/blockchain/search", data={"query": query}, follow_redirects=False)
        assert response.status_code == 303
        assert f"/blockchain/tx/{query}" in response.headers["location"]

    @patch("routers.blockchain.is_authenticated", return_value=True)
    def test_search_by_block_height(self, mock_auth, client):
        response = client.post("/blockchain/search", data={"query": "800000"}, follow_redirects=False)
        assert response.status_code == 303
        assert "/blockchain/block/800000" in response.headers["location"]

    @patch("routers.blockchain.is_authenticated", return_value=True)
    def test_search_by_address(self, mock_auth, client):
        response = client.post("/blockchain/search", data={"query": "bc1qexample"}, follow_redirects=False)
        assert response.status_code == 303
        assert "/blockchain/address/bc1qexample" in response.headers["location"]
