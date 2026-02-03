#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock
import os

from helpers.runcommandprocess import RunCommandProcess, PROCESS_LOG


class TestRunCommandProcess(object):
    """Tests for RunCommandProcess class"""

    def test_init(self):
        process = RunCommandProcess('echo hello')
        assert process.command == 'echo hello'
        assert process.working_dir is None

    def test_init_with_working_dir(self):
        process = RunCommandProcess('echo hello', working_dir='/tmp')
        assert process.command == 'echo hello'
        assert process.working_dir == '/tmp'

    @mock.patch('helpers.runcommandprocess.Popen')
    def test_run_simple_command(self, mock_popen):
        mock_process = mock.MagicMock()
        mock_process.stdout.readline.side_effect = ['output line\n', '']
        mock_process.stderr.readline.side_effect = ['']
        mock_popen.return_value = mock_process

        process = RunCommandProcess('echo hello')
        process.run()

        mock_popen.assert_called_once()

    def test_run_with_working_dir_attribute(self):
        # Test that working_dir is properly stored
        process = RunCommandProcess('echo hello', working_dir='/tmp')
        assert process.working_dir == '/tmp'
        assert process.command == 'echo hello'

    @mock.patch('helpers.runcommandprocess.Popen')
    def test_run_with_stderr(self, mock_popen):
        mock_process = mock.MagicMock()
        mock_process.stdout.readline.side_effect = ['']
        mock_process.stderr.readline.side_effect = ['error message\n', '']
        mock_popen.return_value = mock_process

        process = RunCommandProcess('failing_command')
        process.run()

        mock_popen.assert_called_once()

    @mock.patch('helpers.runcommandprocess.Popen')
    def test_run_multiple_output_lines(self, mock_popen):
        mock_process = mock.MagicMock()
        mock_process.stdout.readline.side_effect = ['line 1\n', 'line 2\n', 'line 3\n', '']
        mock_process.stderr.readline.side_effect = ['']
        mock_popen.return_value = mock_process

        process = RunCommandProcess('multi_line_command')
        process.run()

        mock_popen.assert_called_once()

    def test_process_is_multiprocessing_process(self):
        # Test that RunCommandProcess is a proper multiprocessing.Process subclass
        import multiprocessing
        process = RunCommandProcess('echo hello')
        assert isinstance(process, multiprocessing.Process)


class TestProcessLog(object):
    """Tests for PROCESS_LOG logger"""

    def test_process_log_exists(self):
        assert PROCESS_LOG is not None

    def test_process_log_has_handlers(self):
        assert len(PROCESS_LOG.handlers) >= 1
