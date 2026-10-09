#!/usr/bin/env python
"""Unit tests for the shared HTTP timeout constants."""
from helpers.http_helpers import DEFAULT_HTTP_TIMEOUT, STREAM_HTTP_TIMEOUT


class TestHttpHelpers:
    """Tests for helpers/http_helpers.py"""

    def test_default_http_timeout_is_positive_int(self):
        """Test that DEFAULT_HTTP_TIMEOUT is a positive integer equal to 10."""
        assert isinstance(DEFAULT_HTTP_TIMEOUT, int)
        assert DEFAULT_HTTP_TIMEOUT > 0
        assert DEFAULT_HTTP_TIMEOUT == 10

    def test_stream_http_timeout_is_positive_pair(self):
        """Test that STREAM_HTTP_TIMEOUT is a (connect, read) tuple of two positive numbers."""
        assert isinstance(STREAM_HTTP_TIMEOUT, tuple)
        assert len(STREAM_HTTP_TIMEOUT) == 2
        connect_timeout, read_timeout = STREAM_HTTP_TIMEOUT
        assert connect_timeout > 0
        assert read_timeout > 0
