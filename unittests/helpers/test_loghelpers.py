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
