#!/usr/bin/env python
import os
import tempfile
from unittest import mock

import pytest

from helpers.jsonhelpers import load_from_json_file, save_to_json_file


class TestJsonHelpers:
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
    @mock.patch('helpers.jsonhelpers.os.replace', side_effect=OSError('replace failed'))
    def test_save_to_json_file_error(self, mock_replace, mock_log):
        """Test error handling when the atomic save fails: an error is logged and no temp file is left behind."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.json')
            save_to_json_file(filepath, {'key': 'value'})
            mock_log.error.assert_called()
            assert os.listdir(tmpdir) == []

    @mock.patch('helpers.jsonhelpers.LOG')
    @mock.patch('helpers.jsonhelpers.tempfile.NamedTemporaryFile', side_effect=OSError('temp file failed'))
    def test_save_to_json_file_temp_file_error(self, mock_tempfile, mock_log):
        """Test error handling when the temp file cannot be created: an error is logged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.json')
            save_to_json_file(filepath, {'key': 'value'})
            mock_log.error.assert_called()
            assert os.listdir(tmpdir) == []

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

    @mock.patch('helpers.jsonhelpers.LOG')
    @mock.patch('helpers.jsonhelpers.time.sleep')
    def test_load_from_json_file_retry_succeeds(self, mock_sleep, mock_log):
        """Test that the retry re-reads the file and can succeed"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.json')
            with open(filepath, 'w') as f:
                f.write('invalid json {')

            with mock.patch('helpers.jsonhelpers.simplejson.load', side_effect=[ValueError('bad'), {'recovered': True}]) as mock_load:
                result = load_from_json_file(filepath)
                assert result == {'recovered': True}
                assert mock_load.call_count == 2
            mock_sleep.assert_called_once_with(1)
            mock_log.error.assert_called()

    @mock.patch('helpers.jsonhelpers.LOG')
    @mock.patch('helpers.jsonhelpers.time.sleep')
    @mock.patch('helpers.jsonhelpers.open')
    def test_load_from_json_file_open_error(self, mock_open, mock_sleep, mock_log):
        """Test that an OSError when opening the file returns None"""
        mock_open.side_effect = OSError('open failed')
        result = load_from_json_file('nonexistent.json')
        assert result is None
        mock_sleep.assert_called_once_with(1)
        mock_log.error.assert_called()

    def test_load_from_json_file_missing_file_raises(self):
        """A missing file is a normal condition: load_from_json_file re-raises FileNotFoundError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = os.path.join(tmpdir, 'does_not_exist.json')
            with pytest.raises(FileNotFoundError):
                load_from_json_file(missing)
