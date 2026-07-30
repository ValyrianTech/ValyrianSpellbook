#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import simplejson
import pytest
from unittest.mock import patch, MagicMock
from argparse import Namespace

import listeners.transaction_listener as tx_listener


@pytest.fixture
def reset_globals():
    """Reset module-level globals before and after each test."""
    old_watchlist = tx_listener.WATCHLIST
    old_exit_on_event = tx_listener.EXIT_ON_EVENT
    old_exit_on_timeout = tx_listener.EXIT_ON_TIMEOUT
    old_args = getattr(tx_listener, "args", None)

    tx_listener.WATCHLIST = {}
    tx_listener.EXIT_ON_EVENT = False
    tx_listener.EXIT_ON_TIMEOUT = None
    tx_listener.args = Namespace(send=False, receive=False, testnet=False)
    yield
    tx_listener.WATCHLIST = old_watchlist
    tx_listener.EXIT_ON_EVENT = old_exit_on_event
    tx_listener.EXIT_ON_TIMEOUT = old_exit_on_timeout
    if old_args is not None:
        tx_listener.args = old_args
    elif hasattr(tx_listener, "args"):
        del tx_listener.args


def make_tx_message(txid="abc123", inputs=None, outputs=None):
    """Build a fake new-transactions websocket message."""
    if inputs is None:
        inputs = [{"address": "1AddrIn", "amount": 50000}]
    if outputs is None:
        outputs = [{"address": "1AddrOut", "amount": 40000}]
    data = {
        "type": "new-transactions",
        "data": {
            "txid": txid,
            "inputs": inputs,
            "outputs": outputs,
        },
    }
    return simplejson.dumps(data)


class TestOnMessage:
    """Tests for transaction_listener.on_message"""

    def test_ignores_non_transaction_message(self, reset_globals):
        ws = MagicMock()
        message = simplejson.dumps({"type": "other-type"})

        tx_listener.on_message(ws, message)

        ws.send.assert_not_called()

    def test_processes_transaction_no_watchlist_match(self, reset_globals):
        ws = MagicMock()
        message = make_tx_message()

        tx_listener.on_message(ws, message)

        ws.send.assert_not_called()

    def test_send_watchlist_match_triggers_command(self, reset_globals):
        tx_listener.args.send = True
        tx_listener.WATCHLIST = {"1AddrIn": {"SEND": "echo #txid#"}}
        ws = MagicMock()
        message = make_tx_message(inputs=[{"address": "1AddrIn", "amount": 50000}])

        with patch("listeners.transaction_listener.RunCommandProcess") as mock_proc:
            tx_listener.on_message(ws, message)

            mock_proc.assert_called_once()
            call_kwargs = mock_proc.call_args
            assert "echo abc123" in str(call_kwargs)

    def test_receive_watchlist_match_triggers_command(self, reset_globals):
        tx_listener.args.receive = True
        tx_listener.WATCHLIST = {"1AddrOut": {"RECEIVE": "echo #txid#"}}
        ws = MagicMock()
        message = make_tx_message(outputs=[{"address": "1AddrOut", "amount": 40000}])

        with patch("listeners.transaction_listener.RunCommandProcess") as mock_proc:
            tx_listener.on_message(ws, message)

            mock_proc.assert_called_once()
            call_kwargs = mock_proc.call_args
            assert "echo abc123" in str(call_kwargs)

    def test_exit_on_event_with_match(self, reset_globals):
        tx_listener.args.send = True
        tx_listener.WATCHLIST = {"1AddrIn": {"SEND": "echo send"}}
        tx_listener.EXIT_ON_EVENT = True
        ws = MagicMock()
        message = make_tx_message(inputs=[{"address": "1AddrIn", "amount": 50000}])

        with patch("listeners.transaction_listener.RunCommandProcess"), \
             pytest.raises(SystemExit):
            tx_listener.on_message(ws, message)

        ws.send.assert_called_once_with('{"type":"new-transactions", "unsubscribe": true}')

    def test_exit_on_event_no_match_does_not_exit(self, reset_globals):
        tx_listener.args.send = True
        tx_listener.WATCHLIST = {"1AddrIn": {"SEND": "echo send"}}
        tx_listener.EXIT_ON_EVENT = True
        ws = MagicMock()
        message = make_tx_message(inputs=[{"address": "1OtherAddr", "amount": 50000}])

        tx_listener.on_message(ws, message)

        ws.send.assert_not_called()

    def test_exit_on_timeout(self, reset_globals):
        tx_listener.EXIT_ON_TIMEOUT = int(time.time()) - 1
        ws = MagicMock()
        message = make_tx_message()

        with pytest.raises(SystemExit):
            tx_listener.on_message(ws, message)

        ws.send.assert_called_once_with('{"type":"new-transactions", "unsubscribe": true}')

    def test_no_exit_when_timeout_not_reached(self, reset_globals):
        tx_listener.EXIT_ON_TIMEOUT = int(time.time()) + 3600
        ws = MagicMock()
        message = make_tx_message()

        tx_listener.on_message(ws, message)

        ws.send.assert_not_called()

    def test_empty_input_address_not_added_to_list(self, reset_globals):
        tx_listener.args.send = True
        ws = MagicMock()
        message = make_tx_message(inputs=[{"address": "", "amount": 50000}])

        tx_listener.on_message(ws, message)

        ws.send.assert_not_called()

    def test_empty_output_address_not_added_to_list(self, reset_globals):
        tx_listener.args.receive = True
        ws = MagicMock()
        message = make_tx_message(outputs=[{"address": "", "amount": 40000}])

        tx_listener.on_message(ws, message)

        ws.send.assert_not_called()


class TestOnError:
    """Tests for transaction_listener.on_error"""

    def test_on_error_logs_error(self):
        tx_listener.on_error(MagicMock(), "connection reset")


class TestOnClose:
    """Tests for transaction_listener.on_close"""

    def test_on_close_logs_message(self):
        tx_listener.on_close(MagicMock())


class TestOnOpen:
    """Tests for transaction_listener.on_open"""

    def test_on_open_mainnet(self, reset_globals):
        tx_listener.args.testnet = False
        ws = MagicMock()

        tx_listener.on_open(ws)

        ws.send.assert_called_once_with('{"type":"new-transactions", "network":"BTC"}')

    def test_on_open_testnet(self, reset_globals):
        tx_listener.args.testnet = True
        ws = MagicMock()

        tx_listener.on_open(ws)

        ws.send.assert_called_once_with('{"type":"new-transactions", "network":"BTCTEST"}')


class TestMainBlock:
    """Tests for transaction_listener __main__ block via runpy"""

    @patch("websocket.WebSocketApp")
    def test_main_single_address_send_mode(self, mock_ws_app, monkeypatch):
        mock_instance = MagicMock()
        mock_ws_app.return_value = mock_instance

        monkeypatch.setattr("sys.argv", [
            "transaction_listener.py",
            "-a", "1AddrTest",
            "-s",
            "-c", "echo send",
        ])

        import runpy
        runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "transaction_listener.py"), run_name="__main__")

        mock_ws_app.assert_called_once()
        mock_instance.run_forever.assert_called_once()

    @patch("websocket.WebSocketApp")
    def test_main_single_address_receive_mode(self, mock_ws_app, monkeypatch):
        mock_instance = MagicMock()
        mock_ws_app.return_value = mock_instance

        monkeypatch.setattr("sys.argv", [
            "transaction_listener.py",
            "-a", "1AddrTest",
            "-r",
            "-c", "echo recv",
        ])

        import runpy
        runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "transaction_listener.py"), run_name="__main__")

        mock_ws_app.assert_called_once()
        mock_instance.run_forever.assert_called_once()

    @patch("websocket.WebSocketApp")
    def test_main_watchlist_mode(self, mock_ws_app, monkeypatch, tmp_path):
        mock_instance = MagicMock()
        mock_ws_app.return_value = mock_instance

        watchlist_file = tmp_path / "watchlist.json"
        watchlist_file.write_text(simplejson.dumps({"addr1": {"SEND": "echo hi"}}))

        monkeypatch.setattr("sys.argv", [
            "transaction_listener.py",
            "-w", str(watchlist_file),
        ])

        import runpy
        runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "transaction_listener.py"), run_name="__main__")

        mock_ws_app.assert_called_once()
        mock_instance.run_forever.assert_called_once()

    @patch("websocket.WebSocketApp")
    def test_main_verbose_mode(self, mock_ws_app, monkeypatch):
        mock_instance = MagicMock()
        mock_ws_app.return_value = mock_instance

        monkeypatch.setattr("sys.argv", [
            "transaction_listener.py",
            "-a", "1AddrTest",
            "-s",
            "-c", "echo send",
            "-v",
        ])

        import runpy
        runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "transaction_listener.py"), run_name="__main__")

        mock_ws_app.assert_called_once()

    @patch("websocket.WebSocketApp")
    def test_main_exit_on_event_flag(self, mock_ws_app, monkeypatch):
        mock_instance = MagicMock()
        mock_ws_app.return_value = mock_instance

        monkeypatch.setattr("sys.argv", [
            "transaction_listener.py",
            "-a", "1AddrTest",
            "-s",
            "-c", "echo send",
            "-e",
        ])

        import runpy
        runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "transaction_listener.py"), run_name="__main__")

        mock_ws_app.assert_called_once()

    @patch("websocket.WebSocketApp")
    def test_main_timeout_flag(self, mock_ws_app, monkeypatch):
        mock_instance = MagicMock()
        mock_ws_app.return_value = mock_instance

        monkeypatch.setattr("sys.argv", [
            "transaction_listener.py",
            "-a", "1AddrTest",
            "-s",
            "-c", "echo send",
            "-to", "60",
        ])

        import runpy
        runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "transaction_listener.py"), run_name="__main__")

        mock_ws_app.assert_called_once()

    @patch("websocket.WebSocketApp")
    def test_main_testnet_flag(self, mock_ws_app, monkeypatch):
        mock_instance = MagicMock()
        mock_ws_app.return_value = mock_instance

        monkeypatch.setattr("sys.argv", [
            "transaction_listener.py",
            "-a", "1AddrTest",
            "-s",
            "-c", "echo send",
            "-t",
        ])

        import runpy
        runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "transaction_listener.py"), run_name="__main__")

        mock_ws_app.assert_called_once()

    def test_main_database_mode_missing_user_exits(self, monkeypatch):
        monkeypatch.setattr("sys.argv", [
            "transaction_listener.py",
            "-d", "testdb",
            "-s",
            "-c", "echo send",
        ])

        import runpy
        with pytest.raises(SystemExit) as exc_info:
            runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "transaction_listener.py"), run_name="__main__")

        assert exc_info.value.code == 1

    def test_main_database_mode_missing_password_exits(self, monkeypatch):
        monkeypatch.setattr("sys.argv", [
            "transaction_listener.py",
            "-d", "testdb",
            "-u", "testuser",
            "-s",
            "-c", "echo send",
        ])

        import runpy
        with pytest.raises(SystemExit) as exc_info:
            runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "transaction_listener.py"), run_name="__main__")

        assert exc_info.value.code == 1

    def test_main_database_mode_missing_command_exits(self, monkeypatch):
        monkeypatch.setattr("sys.argv", [
            "transaction_listener.py",
            "-d", "testdb",
            "-u", "testuser",
            "-pw", "testpass",
            "-s",
        ])

        import runpy
        with pytest.raises(SystemExit) as exc_info:
            runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "transaction_listener.py"), run_name="__main__")

        assert exc_info.value.code == 1

    def test_main_database_mode_no_send_or_receive_exits(self, monkeypatch):
        monkeypatch.setattr("sys.argv", [
            "transaction_listener.py",
            "-d", "testdb",
            "-u", "testuser",
            "-pw", "testpass",
            "-c", "echo send",
        ])

        import runpy
        with pytest.raises(SystemExit) as exc_info:
            runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "transaction_listener.py"), run_name="__main__")

        assert exc_info.value.code == 1

    def test_main_watchlist_file_not_found_raises(self, monkeypatch):
        monkeypatch.setattr("sys.argv", [
            "transaction_listener.py",
            "-w", "/nonexistent/path/watchlist.json",
        ])

        import runpy
        with pytest.raises(Exception, match="does not exists"):
            runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "transaction_listener.py"), run_name="__main__")

    @patch("websocket.WebSocketApp")
    def test_main_database_mode_with_send_and_receive(self, mock_ws_app, monkeypatch):
        mock_instance = MagicMock()
        mock_ws_app.return_value = mock_instance

        monkeypatch.setattr("sys.argv", [
            "transaction_listener.py",
            "-d", "testdb",
            "-u", "testuser",
            "-pw", "testpass",
            "-c", "echo send",
            "-s",
            "-r",
        ])

        import runpy
        runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "transaction_listener.py"), run_name="__main__")

        mock_ws_app.assert_called_once()
        mock_instance.run_forever.assert_called_once()

    def test_main_watchlist_invalid_json_raises(self, monkeypatch, tmp_path):
        watchlist_file = tmp_path / "watchlist.json"
        watchlist_file.write_text("not valid json {{{")

        monkeypatch.setattr("sys.argv", [
            "transaction_listener.py",
            "-w", str(watchlist_file),
        ])

        import runpy
        with pytest.raises(Exception, match="does not contain a valid dictionary"):
            runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "transaction_listener.py"), run_name="__main__")
