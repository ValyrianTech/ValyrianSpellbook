#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import simplejson
from unittest.mock import patch, MagicMock

import listeners.block_listener as block_listener


class TestOnMessage:
    """Tests for block_listener.on_message"""

    def test_on_message_prints_block_info(self, capsys):
        block_data = {
            "x": {
                "height": 800000,
                "hash": "abc123def456",
                "nTx": 1500,
                "time": 1700000000,
            }
        }
        message = simplejson.dumps(block_data)
        ws = MagicMock()

        block_listener.on_message(ws, message)

        captured = capsys.readouterr()
        assert "New block:" in captured.out
        assert "800000" in captured.out
        assert "abc123def456" in captured.out
        assert "1500" in captured.out
        assert "1700000000" in captured.out


class TestOnError:
    """Tests for block_listener.on_error"""

    def test_on_error_prints_error(self, capsys):
        block_listener.on_error(MagicMock(), "connection lost")

        captured = capsys.readouterr()
        assert "connection lost" in captured.out


class TestOnClose:
    """Tests for block_listener.on_close"""

    def test_on_close_prints_message(self, capsys):
        block_listener.on_close(MagicMock())

        captured = capsys.readouterr()
        assert "websocket closed" in captured.out


class TestOnOpen:
    """Tests for block_listener.on_open"""

    def test_on_open_sends_subscription(self, capsys):
        ws = MagicMock()

        block_listener.on_open(ws)

        captured = capsys.readouterr()
        assert "websocket opened" in captured.out
        assert "Subscribing to new blocks" in captured.out
        ws.send.assert_called_once_with('{"op":"blocks_sub"}')


class TestMainBlock:
    """Tests for block_listener __main__ block via runpy"""

    @patch("websocket.WebSocketApp")
    def test_main_block_creates_websocket_and_runs(self, mock_ws_app):
        mock_instance = MagicMock()
        mock_ws_app.return_value = mock_instance

        import runpy
        runpy.run_path(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "block_listener.py"),
            run_name="__main__",
        )

        mock_ws_app.assert_called_once()
        mock_instance.run_forever.assert_called_once()
