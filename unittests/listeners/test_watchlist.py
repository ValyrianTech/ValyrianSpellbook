#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import simplejson
import pytest
from unittest.mock import patch, mock_open

from listeners.watchlist import Watchlist


@pytest.fixture
def temp_watchlist_file(tmp_path, monkeypatch):
    """Point WATCHLIST_FILE at a temp path so the real file is never touched."""
    watchlist_path = str(tmp_path / "watchlist.json")
    monkeypatch.setattr("listeners.watchlist.WATCHLIST_FILE", watchlist_path)
    return watchlist_path


@pytest.fixture
def temp_watchlist_for_runpy(tmp_path, monkeypatch):
    """Change to a temp directory so runpy execution uses a temp watchlist.json.

    WATCHLIST_FILE is a relative path ('watchlist.json'), so changing the cwd
    is sufficient to isolate the runpy execution.
    """
    watchlist_path = str(tmp_path / "watchlist.json")
    monkeypatch.chdir(tmp_path)
    return watchlist_path


class TestWatchlistInit:
    """Tests for Watchlist.__init__"""

    def test_init_creates_empty_file_when_missing(self, temp_watchlist_file):
        wl = Watchlist()
        assert wl.watchlist == {}
        assert os.path.exists(temp_watchlist_file)

    def test_init_loads_existing_file(self, temp_watchlist_file):
        data = {"1AddressABC": {"SEND": "echo send"}}
        with open(temp_watchlist_file, "w") as f:
            simplejson.dump(data, f)

        wl = Watchlist()
        assert wl.watchlist == data

    def test_init_raises_on_invalid_json(self, temp_watchlist_file):
        with open(temp_watchlist_file, "w") as f:
            f.write("not valid json {{{")

        with pytest.raises(Exception, match="does not contain a valid dictionary"):
            Watchlist()


class TestSaveEvent:
    """Tests for Watchlist.save_event"""

    def test_save_event_new_address(self, temp_watchlist_file):
        wl = Watchlist()
        wl.save_event("addr1", "SEND", "echo hello")

        assert wl.watchlist == {"addr1": {"SEND": "echo hello"}}

    def test_save_event_existing_address_new_event(self, temp_watchlist_file):
        wl = Watchlist()
        wl.save_event("addr1", "SEND", "echo send")
        wl.save_event("addr1", "RECEIVE", "echo recv")

        assert wl.watchlist == {
            "addr1": {"SEND": "echo send", "RECEIVE": "echo recv"}
        }

    def test_save_event_updates_existing_event(self, temp_watchlist_file):
        wl = Watchlist()
        wl.save_event("addr1", "SEND", "echo old")
        wl.save_event("addr1", "SEND", "echo new")

        assert wl.watchlist == {"addr1": {"SEND": "echo new"}}

    def test_save_event_persists_to_file(self, temp_watchlist_file):
        wl = Watchlist()
        wl.save_event("addr1", "SEND", "echo hello")

        with open(temp_watchlist_file, "r") as f:
            saved = simplejson.load(f)
        assert saved == {"addr1": {"SEND": "echo hello"}}


class TestDeleteEvent:
    """Tests for Watchlist.delete_event"""

    def test_delete_event_removes_event(self, temp_watchlist_file):
        wl = Watchlist()
        wl.save_event("addr1", "SEND", "echo send")
        wl.save_event("addr1", "RECEIVE", "echo recv")

        wl.delete_event("addr1", "SEND")

        assert wl.watchlist == {"addr1": {"RECEIVE": "echo recv"}}

    def test_delete_event_only_event(self, temp_watchlist_file):
        wl = Watchlist()
        wl.save_event("addr1", "SEND", "echo send")

        wl.delete_event("addr1", "SEND")

        assert wl.watchlist == {"addr1": {}}

    def test_delete_event_address_not_in_watchlist(self, temp_watchlist_file):
        wl = Watchlist()
        wl.delete_event("nonexistent", "SEND")
        assert wl.watchlist == {}

    def test_delete_event_not_in_address(self, temp_watchlist_file):
        wl = Watchlist()
        wl.save_event("addr1", "SEND", "echo send")

        wl.delete_event("addr1", "RECEIVE")

        assert wl.watchlist == {"addr1": {"SEND": "echo send"}}


class TestSaveFile:
    """Tests for Watchlist.save_file"""

    def test_save_file_writes_json(self, temp_watchlist_file):
        wl = Watchlist()
        wl.watchlist = {"addr1": {"SEND": "cmd"}}

        wl.save_file()

        with open(temp_watchlist_file, "r") as f:
            saved = simplejson.load(f)
        assert saved == {"addr1": {"SEND": "cmd"}}

    def test_save_file_raises_on_write_error(self, temp_watchlist_file):
        wl = Watchlist()
        wl.watchlist = {"addr1": {"SEND": "cmd"}}

        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = IOError("disk full")
            with pytest.raises(Exception, match="Failed to write data"):
                wl.save_file()


class TestShow:
    """Tests for Watchlist.show"""

    def test_show_all_addresses(self, temp_watchlist_file, capsys):
        wl = Watchlist()
        wl.save_event("addr1", "SEND", "echo send")
        wl.save_event("addr2", "RECEIVE", "echo recv")

        wl.show()

        captured = capsys.readouterr()
        assert "addr1" in captured.out
        assert "addr2" in captured.out

    def test_show_single_address(self, temp_watchlist_file, capsys):
        wl = Watchlist()
        wl.save_event("addr1", "SEND", "echo send")
        wl.save_event("addr2", "RECEIVE", "echo recv")

        wl.show("addr1")

        captured = capsys.readouterr()
        assert "addr1" in captured.out
        assert "addr2" not in captured.out

    def test_show_nonexistent_address(self, temp_watchlist_file, capsys):
        wl = Watchlist()
        wl.save_event("addr1", "SEND", "echo send")

        wl.show("nonexistent")

        captured = capsys.readouterr()
        assert "No events found" in captured.out

    def test_show_empty_watchlist_no_address(self, temp_watchlist_file, capsys):
        wl = Watchlist()

        wl.show()

        captured = capsys.readouterr()
        assert captured.out == ""


class TestMainBlock:
    """Tests for watchlist __main__ block via runpy"""

    def test_main_add_command(self, temp_watchlist_for_runpy, monkeypatch):
        monkeypatch.setattr("sys.argv", ["watchlist.py", "add", "addr1", "SEND", "echo", "hello"])

        import runpy
        runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "watchlist.py"), run_name="__main__")

        with open(temp_watchlist_for_runpy, "r") as f:
            saved = simplejson.load(f)
        assert saved == {"addr1": {"SEND": "echo hello"}}

    def test_main_add_receive_command(self, temp_watchlist_for_runpy, monkeypatch):
        monkeypatch.setattr("sys.argv", ["watchlist.py", "add", "addr1", "RECEIVE", "echo", "recv"])

        import runpy
        runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "watchlist.py"), run_name="__main__")

        with open(temp_watchlist_for_runpy, "r") as f:
            saved = simplejson.load(f)
        assert saved == {"addr1": {"RECEIVE": "echo recv"}}

    def test_main_delete_command(self, temp_watchlist_for_runpy, monkeypatch):
        with open(temp_watchlist_for_runpy, "w") as f:
            simplejson.dump({"addr1": {"SEND": "echo send", "RECEIVE": "echo recv"}}, f)

        monkeypatch.setattr("sys.argv", ["watchlist.py", "delete", "addr1", "SEND"])

        import runpy
        runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "watchlist.py"), run_name="__main__")

        with open(temp_watchlist_for_runpy, "r") as f:
            saved = simplejson.load(f)
        assert saved == {"addr1": {"RECEIVE": "echo recv"}}

    def test_main_show_all_command(self, temp_watchlist_for_runpy, monkeypatch, capsys):
        with open(temp_watchlist_for_runpy, "w") as f:
            simplejson.dump({"addr1": {"SEND": "echo send"}}, f)

        monkeypatch.setattr("sys.argv", ["watchlist.py", "show"])

        import runpy
        runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "watchlist.py"), run_name="__main__")

        captured = capsys.readouterr()
        assert "addr1" in captured.out

    def test_main_show_single_address_command(self, temp_watchlist_for_runpy, monkeypatch, capsys):
        with open(temp_watchlist_for_runpy, "w") as f:
            simplejson.dump({"addr1": {"SEND": "echo send"}, "addr2": {"RECEIVE": "echo recv"}}, f)

        monkeypatch.setattr("sys.argv", ["watchlist.py", "show", "addr1"])

        import runpy
        runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "listeners", "watchlist.py"), run_name="__main__")

        captured = capsys.readouterr()
        assert "addr1" in captured.out
        assert "addr2" not in captured.out
