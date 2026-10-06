#!/usr/bin/env python
import multiprocessing
import os
import sys
from unittest import mock

import pytest

from helpers.runcommandprocess import PROCESS_LOG, RunCommandProcess


def _mock_process(stdout_lines=(), stderr_lines=(), returncode=0):
    """Build a mocked Popen result with controlled streams and return code."""
    mock_process = mock.MagicMock()
    mock_process.stdout.readline.side_effect = list(stdout_lines) + ['']
    mock_process.stderr.readline.side_effect = list(stderr_lines) + ['']
    mock_process.returncode = returncode
    mock_process.wait.return_value = returncode
    return mock_process


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

    @mock.patch('helpers.runcommandprocess.PROCESS_LOG')
    @mock.patch('helpers.runcommandprocess.Popen')
    def test_run_simple_command(self, mock_popen, mock_log):
        mock_popen.return_value = _mock_process(['output line\n'])
        process = RunCommandProcess('echo hello')
        result = process.run()
        mock_popen.assert_called_once()
        assert result == 0

    def test_run_with_working_dir_attribute(self):
        # Test that working_dir is properly stored
        process = RunCommandProcess('echo hello', working_dir='/tmp')
        assert process.working_dir == '/tmp'
        assert process.command == 'echo hello'

    @mock.patch('helpers.runcommandprocess.PROCESS_LOG')
    @mock.patch('helpers.runcommandprocess.Popen')
    def test_run_with_stderr(self, mock_popen, mock_log):
        mock_popen.return_value = _mock_process([], ['error message\n'])
        process = RunCommandProcess('failing_command')
        result = process.run()
        mock_popen.assert_called_once()
        assert result == 0

    @mock.patch('helpers.runcommandprocess.PROCESS_LOG')
    @mock.patch('helpers.runcommandprocess.Popen')
    def test_run_multiple_output_lines(self, mock_popen, mock_log):
        mock_popen.return_value = _mock_process(['line 1\n', 'line 2\n', 'line 3\n'], [])
        process = RunCommandProcess('multi_line_command')
        result = process.run()
        mock_popen.assert_called_once()
        assert result == 0

    def test_process_is_multiprocessing_process(self):
        # Test that RunCommandProcess is a proper multiprocessing.Process subclass
        process = RunCommandProcess('echo hello')
        assert isinstance(process, multiprocessing.Process)

    @mock.patch('helpers.runcommandprocess.PROCESS_LOG')
    @mock.patch('helpers.runcommandprocess.Popen')
    def test_run_with_list_command(self, mock_popen, mock_log):
        mock_popen.return_value = _mock_process()
        process = RunCommandProcess(['echo', 'hello'])
        result = process.run()
        mock_popen.assert_called_once()
        assert mock_popen.call_args[0][0] == ['echo', 'hello']
        assert mock_popen.call_args.kwargs.get('shell') is not True
        assert result == 0

    @mock.patch('helpers.runcommandprocess.PROCESS_LOG')
    @mock.patch('helpers.runcommandprocess.Popen')
    def test_run_with_string_command_is_split(self, mock_popen, mock_log):
        mock_popen.return_value = _mock_process()
        process = RunCommandProcess('echo hello')
        result = process.run()
        mock_popen.assert_called_once()
        assert mock_popen.call_args[0][0] == ['echo', 'hello']
        assert mock_popen.call_args.kwargs.get('shell') is not True
        assert result == 0

    @mock.patch('helpers.runcommandprocess.PROCESS_LOG')
    @mock.patch('helpers.runcommandprocess.Popen')
    def test_run_logs_stdout_info_and_stderr_error(self, mock_popen, mock_log):
        process_id = multiprocessing.current_process().name
        mock_popen.return_value = _mock_process(['output line\n'], ['error message\n'])
        process = RunCommandProcess('echo hello')
        process.run()
        mock_log.info.assert_any_call(f'{process_id} | output line')
        mock_log.error.assert_any_call(f'{process_id} | error message')

    @mock.patch('helpers.runcommandprocess.PROCESS_LOG')
    @mock.patch('helpers.runcommandprocess.Popen')
    def test_run_nonzero_returncode(self, mock_popen, mock_log):
        mock_popen.return_value = _mock_process([], ['error message\n'], returncode=3)
        process = RunCommandProcess('failing_command')
        result = process.run()
        assert result == 3
        error_msgs = [call.args[0] for call in mock_log.error.call_args_list if call.args]
        assert any('Command failed with exit code 3' in msg for msg in error_msgs)

    @mock.patch('helpers.runcommandprocess.PROCESS_LOG')
    @mock.patch('helpers.runcommandprocess.Popen')
    def test_run_passes_cwd_to_popen(self, mock_popen, mock_log):
        mock_popen.return_value = _mock_process()
        process = RunCommandProcess('echo hello', working_dir='/working/dir')
        process.run()
        assert mock_popen.call_args.kwargs.get('cwd') == '/working/dir'

    @mock.patch('helpers.runcommandprocess.PROCESS_LOG')
    @mock.patch('helpers.runcommandprocess.Popen')
    def test_run_inherits_cwd_when_none(self, mock_popen, mock_log):
        mock_popen.return_value = _mock_process()
        process = RunCommandProcess('echo hello')
        process.run()
        assert mock_popen.call_args.kwargs.get('cwd') is None


class TestRunCommandProcessReal:
    """Integration tests exercising run() against real subprocesses."""

    def test_large_stdout_no_deadlock(self):
        code = 'import sys\nsys.stdout.write("x" * 3000000 + "\\n")\n'
        process = RunCommandProcess([sys.executable, '-c', code])
        with mock.patch('helpers.runcommandprocess.PROCESS_LOG') as log:
            result = process.run()
        assert result == 0
        assert log.info.call_count >= 1

    def test_large_stderr_no_deadlock(self):
        code = 'import sys\nsys.stderr.write("y" * 3000000 + "\\n")\n'
        process = RunCommandProcess([sys.executable, '-c', code])
        with mock.patch('helpers.runcommandprocess.PROCESS_LOG') as log:
            result = process.run()
        assert result == 0
        assert log.error.call_count >= 1

    def test_large_stdout_and_stderr_no_deadlock(self):
        code = (
            'import sys\n'
            'sys.stdout.write("o" * 2000000 + "\\n")\n'
            'sys.stderr.write("e" * 2000000 + "\\n")\n'
        )
        process = RunCommandProcess([sys.executable, '-c', code])
        with mock.patch('helpers.runcommandprocess.PROCESS_LOG'):
            result = process.run()
        assert result == 0

    def test_nonzero_exit_code_surfaced(self):
        code = 'import sys\nsys.stderr.write("boom\\n")\nsys.exit(3)\n'
        process = RunCommandProcess([sys.executable, '-c', code])
        with mock.patch('helpers.runcommandprocess.PROCESS_LOG') as log:
            result = process.run()
        assert result == 3
        error_msgs = [call.args[0] for call in log.error.call_args_list if call.args]
        assert any('Command failed with exit code 3' in msg for msg in error_msgs)

    def test_working_dir_not_mutated(self, tmp_path):
        before = os.getcwd()
        code = 'import os\nprint(os.getcwd())\n'
        process = RunCommandProcess([sys.executable, '-c', code], working_dir=str(tmp_path))
        with mock.patch('helpers.runcommandprocess.PROCESS_LOG') as log:
            result = process.run()
        assert result == 0
        assert os.getcwd() == before
        expected = os.path.realpath(str(tmp_path))
        info_msgs = [call.args[0] for call in log.info.call_args_list if call.args]
        assert any(expected in msg for msg in info_msgs)


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
        with (
            mock.patch('helpers.runcommandprocess.PROCESS_LOG'),
            mock.patch('helpers.runcommandprocess.Popen') as mock_popen,
        ):
            mock_popen.return_value = _mock_process()

            process = RunCommandProcess(['sh', '-c', 'echo $HOME | cat'])
            result = process.run()

        assert result == 0
        assert mock_popen.call_args[0][0] == ['sh', '-c', 'echo $HOME | cat']
        assert mock_popen.call_args.kwargs.get('shell') is not True
