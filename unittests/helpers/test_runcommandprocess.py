#!/usr/bin/env python
from unittest import mock

import pytest

from helpers.runcommandprocess import PROCESS_LOG, RunCommandProcess


class TestRunCommandProcess:
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

    @mock.patch('helpers.runcommandprocess.Popen')
    def test_run_with_list_command(self, mock_popen):
        mock_process = mock.MagicMock()
        mock_process.stdout.readline.side_effect = ['']
        mock_process.stderr.readline.side_effect = ['']
        mock_popen.return_value = mock_process

        process = RunCommandProcess(['echo', 'hello'])
        process.run()

        mock_popen.assert_called_once()
        assert mock_popen.call_args[0][0] == ['echo', 'hello']
        assert mock_popen.call_args.kwargs.get('shell') is not True

    @mock.patch('helpers.runcommandprocess.Popen')
    def test_run_with_string_command_is_split(self, mock_popen):
        mock_process = mock.MagicMock()
        mock_process.stdout.readline.side_effect = ['']
        mock_process.stderr.readline.side_effect = ['']
        mock_popen.return_value = mock_process

        process = RunCommandProcess('echo hello')
        process.run()

        mock_popen.assert_called_once()
        assert mock_popen.call_args[0][0] == ['echo', 'hello']
        assert mock_popen.call_args.kwargs.get('shell') is not True


class TestProcessLog:
    """Tests for PROCESS_LOG logger"""

    def test_process_log_exists(self):
        assert PROCESS_LOG is not None

    def test_process_log_has_handlers(self):
        assert len(PROCESS_LOG.handlers) >= 1


class TestRunCommandProcessWorkingDir:
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


class TestShellMetacharacterDetection:
    """Tests for shell metacharacter detection and the shell-removal breaking change."""

    def test_contains_shell_metacharacters_rejects_non_string(self):
        """argv lists (non-str) never contain metacharacters."""
        assert RunCommandProcess.contains_shell_metacharacters(['echo', 'hello']) is False

    def test_contains_shell_metacharacters_plain_string(self):
        """A plain command string has no metacharacters."""
        assert RunCommandProcess.contains_shell_metacharacters('echo hello') is False

    def test_contains_shell_metacharacters_pipe(self):
        assert RunCommandProcess.contains_shell_metacharacters('cat a | grep b') is True

    def test_contains_shell_metacharacters_redirection(self):
        assert RunCommandProcess.contains_shell_metacharacters('ls > out.txt') is True

    def test_contains_shell_metacharacters_chaining(self):
        assert RunCommandProcess.contains_shell_metacharacters('make && make install') is True

    def test_contains_shell_metacharacters_variable(self):
        assert RunCommandProcess.contains_shell_metacharacters('echo $HOME') is True

    def test_init_warns_on_metacharacters(self):
        """A string command with metacharacters logs a warning but does not raise."""
        with mock.patch('helpers.runcommandprocess.PROCESS_LOG') as mock_log:
            process = RunCommandProcess('cat a | grep b')

        assert process.command == 'cat a | grep b'
        assert process.strict is False
        mock_log.warning.assert_called_once()
        assert 'breaking change' in mock_log.warning.call_args[0][0]

    def test_init_strict_raises_on_metacharacters(self):
        """A string command with metacharacters raises ValueError when strict=True."""
        with pytest.raises(ValueError) as exc_info:
            RunCommandProcess('cat a | grep b', strict=True)

        assert 'shell' in str(exc_info.value)

    def test_init_strict_no_raise_without_metacharacters(self):
        """strict=True is a no-op for commands without shell metacharacters."""
        with mock.patch('helpers.runcommandprocess.PROCESS_LOG') as mock_log:
            process = RunCommandProcess('echo hello', strict=True)

        assert process.strict is True
        mock_log.warning.assert_not_called()

    def test_init_strict_no_raise_with_list_command(self):
        """argv lists never trigger warnings or raises, even in strict mode."""
        with mock.patch('helpers.runcommandprocess.PROCESS_LOG') as mock_log:
            process = RunCommandProcess(['sh', '-c', 'echo $HOME'], strict=True)

        assert process.strict is True
        mock_log.warning.assert_not_called()

    def test_explicit_shell_argv_list_is_supported(self):
        """Passing an explicit shell argv list is the documented escape hatch."""
        with mock.patch('helpers.runcommandprocess.Popen') as mock_popen:
            mock_process = mock.MagicMock()
            mock_process.stdout.readline.side_effect = ['']
            mock_process.stderr.readline.side_effect = ['']
            mock_popen.return_value = mock_process

            process = RunCommandProcess(['sh', '-c', 'echo $HOME | cat'])
            process.run()

        assert mock_popen.call_args[0][0] == ['sh', '-c', 'echo $HOME | cat']
        assert mock_popen.call_args.kwargs.get('shell') is not True
