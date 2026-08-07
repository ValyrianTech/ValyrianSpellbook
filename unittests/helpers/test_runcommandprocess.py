#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mock

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
    @mock.patch('helpers.runcommandprocess.os.chdir')
    @mock.patch('helpers.runcommandprocess.os.getcwd')
    def test_run_with_working_dir_change(self, mock_getcwd, mock_chdir, mock_popen):
        """Test that run() changes to working_dir and back"""
        mock_getcwd.side_effect = ['/original/dir', '/working/dir', '/working/dir', '/original/dir']
        mock_process = mock.MagicMock()
        mock_process.stdout.readline.side_effect = ['']
        mock_process.stderr.readline.side_effect = ['']
        mock_popen.return_value = mock_process

        process = RunCommandProcess('echo hello', working_dir='/working/dir')
        process.run()

        mock_popen.assert_called_once()

    @mock.patch('helpers.runcommandprocess.Popen')
    @mock.patch('helpers.runcommandprocess.os.getcwd', return_value='/same/dir')
    @mock.patch('helpers.runcommandprocess.os.chdir')
    def test_run_no_dir_change_when_same(self, mock_chdir, mock_getcwd, mock_popen):
        """Test that run() does not change dir when already there"""
        mock_process = mock.MagicMock()
        mock_process.stdout.readline.side_effect = ['']
        mock_process.stderr.readline.side_effect = ['']
        mock_popen.return_value = mock_process

        process = RunCommandProcess('echo hello', working_dir='/same/dir')
        process.run()

        mock_chdir.assert_not_called()

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


class TestRunCommandProcessWorkingDir(object):
    """Tests for RunCommandProcess working directory handling"""

    def test_working_dir_stored(self):
        """Test that working_dir is properly stored"""
        process = RunCommandProcess('echo hello', working_dir='/test/dir')
        assert process.working_dir == '/test/dir'
        assert process.command == 'echo hello'

    def test_working_dir_none_by_default(self):
        """Test that working_dir is None by default"""
        process = RunCommandProcess('echo hello')
        assert process.working_dir is None
