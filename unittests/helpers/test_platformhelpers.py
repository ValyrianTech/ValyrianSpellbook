#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock

from helpers.platformhelpers import format_args


class TestPlatformHelpers(object):
    """Tests for platform helper functions"""

    @mock.patch('helpers.platformhelpers.platform.system', return_value='Linux')
    def test_format_args_linux_list(self, mock_system):
        """Test format_args on Linux with a list"""
        args = ['cmd', 'arg1', 'arg2']
        result = format_args(args)
        assert result == 'cmd arg1 arg2 '

    @mock.patch('helpers.platformhelpers.platform.system', return_value='Linux')
    def test_format_args_linux_with_spaces(self, mock_system):
        """Test format_args on Linux with arguments containing spaces"""
        args = ['cmd', 'arg with spaces', 'normal']
        result = format_args(args)
        assert result == 'cmd "arg with spaces" normal '

    @mock.patch('helpers.platformhelpers.platform.system', return_value='Windows')
    def test_format_args_windows(self, mock_system):
        """Test format_args on Windows returns list unchanged"""
        args = ['cmd', 'arg1', 'arg2']
        result = format_args(args)
        assert result == args

    @mock.patch('helpers.platformhelpers.platform.system', return_value='Linux')
    def test_format_args_linux_string(self, mock_system):
        """Test format_args on Linux with a string (not list)"""
        args = 'cmd arg1 arg2'
        result = format_args(args)
        assert result == args
