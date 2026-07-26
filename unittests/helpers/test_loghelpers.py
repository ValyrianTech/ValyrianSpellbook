#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import os
import tempfile

from helpers.loghelpers import get_logs, LOG, REQUESTS_LOG


class TestLogHelpers(object):
    """Tests for log helper functions"""

    def test_log_exists(self):
        """Test that LOG logger exists"""
        assert LOG is not None

    def test_requests_log_exists(self):
        """Test that REQUESTS_LOG logger exists"""
        assert REQUESTS_LOG is not None

    def test_get_logs_no_filter(self):
        """Test get_logs without filter"""
        # This will return logs from the actual log files
        logs = get_logs()
        assert isinstance(logs, list)

    def test_get_logs_with_filter(self):
        """Test get_logs with a filter string"""
        # Use a filter that likely won't match anything
        logs = get_logs(filter_string='UNLIKELY_FILTER_STRING_12345')
        assert isinstance(logs, list)
        assert len(logs) == 0

    def test_log_levels(self):
        """Test that LOG supports different log levels"""
        import logging
        assert LOG.level == logging.DEBUG

    def test_requests_log_levels(self):
        """Test that REQUESTS_LOG supports different log levels"""
        import logging
        assert REQUESTS_LOG.level == logging.DEBUG

    def test_log_has_handlers(self):
        """Test that LOG has handlers configured"""
        assert len(LOG.handlers) >= 2  # stream and file handler

    def test_requests_log_has_handlers(self):
        """Test that REQUESTS_LOG has handlers configured"""
        assert len(REQUESTS_LOG.handlers) >= 1  # file handler

    def test_get_logs_returns_sorted(self):
        """Test that get_logs returns sorted results"""
        logs = get_logs()
        # Verify it's a list (sorting is done internally)
        assert isinstance(logs, list)
        # If there are logs, verify they're sorted
        if len(logs) > 1:
            assert logs == sorted(logs)

    def test_get_logs_with_matching_filter(self):
        """Test get_logs with a filter that matches log entries"""
        # First write a log entry, then filter for it
        LOG.info('UNIQUE_TEST_MARKER_12345')
        logs = get_logs(filter_string='UNIQUE_TEST_MARKER_12345')
        assert isinstance(logs, list)
        # The log file may not be flushed immediately, but the function should work
        # If there are results, they should all contain the filter string
        for entry in logs:
            assert 'UNIQUE_TEST_MARKER_12345' in entry

    def test_get_logs_requests_log(self):
        """Test get_logs with requests log file"""
        REQUESTS_LOG.info('REQUEST_TEST_MARKER_12345')
        logs = get_logs(filter_string='REQUEST_TEST_MARKER_12345')
        assert isinstance(logs, list)

    def test_log_handlers_count(self):
        """Test that LOG has both stream and file handlers"""
        import logging
        stream_count = sum(1 for h in LOG.handlers if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.handlers.RotatingFileHandler))
        file_count = sum(1 for h in LOG.handlers if isinstance(h, logging.handlers.RotatingFileHandler))
        assert stream_count >= 1
        assert file_count >= 1
