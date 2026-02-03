#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import os
import tempfile
import mock

from helpers.jsonhelpers import save_to_json_file, load_from_json_file


class TestJsonHelpers(object):
    """Tests for JSON helper functions"""

    def test_save_to_json_file(self):
        """Test saving data to a JSON file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.json')
            data = {'key': 'value', 'number': 42}
            save_to_json_file(filepath, data)
            
            assert os.path.exists(filepath)
            
            # Verify content
            loaded = load_from_json_file(filepath)
            assert loaded == data

    def test_save_to_json_file_creates_directory(self):
        """Test that save_to_json_file creates parent directories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'subdir', 'nested', 'test.json')
            data = {'key': 'value'}
            save_to_json_file(filepath, data)
            
            assert os.path.exists(filepath)

    def test_load_from_json_file(self):
        """Test loading data from a JSON file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.json')
            data = {'key': 'value', 'list': [1, 2, 3]}
            save_to_json_file(filepath, data)
            
            loaded = load_from_json_file(filepath)
            assert loaded == data

    def test_load_from_json_file_complex_data(self):
        """Test loading complex nested data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.json')
            data = {
                'nested': {'a': 1, 'b': 2},
                'list': [{'x': 1}, {'y': 2}],
                'string': 'hello',
                'number': 3.14
            }
            save_to_json_file(filepath, data)
            
            loaded = load_from_json_file(filepath)
            assert loaded == data

    @mock.patch('helpers.jsonhelpers.LOG')
    def test_save_to_json_file_error(self, mock_log):
        """Test error handling when saving fails"""
        # Try to save to an invalid path (read-only or non-existent drive)
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.json')
            # Create the file first
            save_to_json_file(filepath, {'key': 'value'})
            
            # Make the file read-only
            os.chmod(filepath, 0o444)
            
            try:
                # This should fail and log an error
                save_to_json_file(filepath, {'new': 'data'})
                mock_log.error.assert_called()
            finally:
                # Restore permissions for cleanup
                os.chmod(filepath, 0o644)

    @mock.patch('helpers.jsonhelpers.LOG')
    @mock.patch('helpers.jsonhelpers.time.sleep')
    def test_load_from_json_file_retry_on_error(self, mock_sleep, mock_log):
        """Test that load_from_json_file retries on error"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.json')
            # Create an invalid JSON file
            with open(filepath, 'w') as f:
                f.write('invalid json {')
            
            # This should fail, retry, and return None
            result = load_from_json_file(filepath)
            assert result is None
            mock_log.error.assert_called()
            mock_sleep.assert_called_once_with(1)
