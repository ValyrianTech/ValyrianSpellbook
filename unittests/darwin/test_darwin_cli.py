#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for darwin/darwin.py — the CLI entry point for the Evolver.

darwin.py runs all logic in a __main__ guard. We use runpy to execute it
with mocked dependencies, covering the argparse setup and evolver calls.
"""
import os
import sys
import runpy
from unittest.mock import patch, MagicMock

import pytest

_DARWIN_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                            'darwin', 'darwin.py')


class TestDarwinCli:

    def test_darwin_help(self):
        """Running with --help covers the argparse setup."""
        import subprocess
        result = subprocess.run([sys.executable, _DARWIN_PATH, '--help'],
                                capture_output=True, text=True)
        assert result.returncode == 0
        assert 'config' in result.stdout

    def test_darwin_main_guard(self):
        """Running via runpy with mocked Evolver covers the full __main__ guard."""
        mock_evolver = MagicMock()
        mock_config = {'title': 'test'}
        with patch('sys.argv', ['darwin.py', 'test_config.json']):
            with patch('darwin.evolver.Evolver', return_value=mock_evolver), \
                 patch('helpers.jsonhelpers.load_from_json_file', return_value=mock_config):
                runpy.run_path(_DARWIN_PATH, run_name='__main__')
                mock_evolver.load_config.assert_called_once_with(mock_config)
                mock_evolver.print_settings.assert_called_once()
                mock_evolver.start.assert_called_once()
