#!/usr/bin/env python
import os
import subprocess
from unittest.mock import patch

from action.actiontype import ActionType
from action.commandaction import DEFAULT_COMMAND_TIMEOUT, CommandAction


class TestCommandAction:
    """Tests for CommandAction"""

    def test_commandaction_init(self):
        action = CommandAction('test_command_action')
        assert action.id == 'test_command_action'
        assert action.action_type == ActionType.COMMAND
        assert action.run_command is None
        assert action.working_dir is None
        assert action.command_timeout == DEFAULT_COMMAND_TIMEOUT

    def test_commandaction_configure(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo hello', working_dir='/tmp')
        assert action.run_command == 'echo hello'
        assert action.working_dir == '/tmp'

    def test_commandaction_configure_with_command_timeout(self):
        action = CommandAction('test_command_action')
        action.configure(command_timeout=5)
        assert action.command_timeout == 5

    def test_commandaction_configure_without_optional_params(self):
        action = CommandAction('test_command_action')
        action.configure()
        assert action.run_command is None
        assert action.working_dir is None

    def test_commandaction_json_encodable(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo hello', working_dir='/tmp', created=1609459200)
        result = action.json_encodable()
        assert result['id'] == 'test_command_action'
        assert result['action_type'] == ActionType.COMMAND
        assert result['run_command'] == 'echo hello'
        assert result['working_dir'] == '/tmp'
        assert result['command_timeout'] == DEFAULT_COMMAND_TIMEOUT

    def test_commandaction_json_encodable_command_timeout(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo hello', command_timeout=5)
        result = action.json_encodable()
        assert result['command_timeout'] == 5

    def test_commandaction_run_with_no_command(self):
        action = CommandAction('test_command_action')
        assert not action.run()

    def test_commandaction_run_with_empty_command(self):
        action = CommandAction('test_command_action')
        action.run_command = ''
        assert not action.run()

    def test_commandaction_run_success(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo hello')
        result = action.run()
        assert result[0]
        assert b'hello' in result[1]

    def test_commandaction_run_with_error(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='ls /nonexistent_directory_12345')
        result = action.run()
        assert not result[0]

    def test_commandaction_run_with_missing_executable(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='this_command_does_not_exist_12345')
        result = action.run()
        assert len(result) == 3
        assert result[0] is False
        assert result[1] == b''
        assert isinstance(result[2], bytes)

    def test_commandaction_run_with_placeholders(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo {MESSAGE}')
        result = action.run(placeholders={'{MESSAGE}': 'test_placeholder'})
        assert result[0]
        assert b'test_placeholder' in result[1]

    def test_commandaction_run_with_working_dir(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='pwd', working_dir='/tmp')
        original_dir = os.getcwd()
        result = action.run()
        assert result[0]
        assert b'/tmp' in result[1]
        # Verify we're back to original directory
        assert os.getcwd() == original_dir

    def test_commandaction_run_switches_back_to_original_dir(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo test', working_dir='/tmp')
        original_dir = os.getcwd()
        action.run()
        assert os.getcwd() == original_dir

    def test_commandaction_run_times_out(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo hello')
        with patch('action.commandaction.subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd=['x'], timeout=1, output=b'partial')
            result = action.run()
        assert result.success is False
        assert result.stdout == b'partial'
        assert result.stderr == b'timeout'
        assert mock_run.call_args.kwargs['timeout'] == DEFAULT_COMMAND_TIMEOUT

    def test_commandaction_run_times_out_without_output(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo hello')
        with patch('action.commandaction.subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd=['x'], timeout=1, output=None)
            result = action.run()
        assert result.success is False
        assert result.stdout == b''
        assert result.stderr == b'timeout'

    def test_commandaction_run_times_out_end_to_end(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='sleep 5', command_timeout=0.1)
        result = action.run()
        assert result.success is False
        assert result.stderr == b'timeout'


class TestCommandActionTimeoutValidation:
    """Tests for CommandAction command_timeout validation/coercion"""

    def test_command_timeout_none_falls_back_to_default(self):
        action = CommandAction('test_command_action')
        with patch('action.commandaction.LOG') as mock_log:
            action.configure(command_timeout=None)
        assert action.command_timeout == DEFAULT_COMMAND_TIMEOUT
        assert mock_log.error.called

    def test_command_timeout_non_numeric_string_falls_back(self):
        action = CommandAction('test_command_action')
        with patch('action.commandaction.LOG') as mock_log:
            action.configure(command_timeout='abc')
        assert action.command_timeout == DEFAULT_COMMAND_TIMEOUT
        assert mock_log.error.called

    def test_command_timeout_bool_falls_back(self):
        action = CommandAction('test_command_action')
        with patch('action.commandaction.LOG') as mock_log:
            action.configure(command_timeout=True)
        assert action.command_timeout == DEFAULT_COMMAND_TIMEOUT
        assert mock_log.error.called

    def test_command_timeout_list_falls_back(self):
        action = CommandAction('test_command_action')
        with patch('action.commandaction.LOG') as mock_log:
            action.configure(command_timeout=[1, 2])
        assert action.command_timeout == DEFAULT_COMMAND_TIMEOUT
        assert mock_log.error.called

    def test_command_timeout_zero_falls_back(self):
        action = CommandAction('test_command_action')
        with patch('action.commandaction.LOG') as mock_log:
            action.configure(command_timeout=0)
        assert action.command_timeout == DEFAULT_COMMAND_TIMEOUT
        assert mock_log.error.called

    def test_command_timeout_negative_falls_back(self):
        action = CommandAction('test_command_action')
        with patch('action.commandaction.LOG') as mock_log:
            action.configure(command_timeout=-5)
        assert action.command_timeout == DEFAULT_COMMAND_TIMEOUT
        assert mock_log.error.called

    def test_command_timeout_nan_falls_back(self):
        action = CommandAction('test_command_action')
        with patch('action.commandaction.LOG') as mock_log:
            action.configure(command_timeout=float('nan'))
        assert action.command_timeout == DEFAULT_COMMAND_TIMEOUT
        assert mock_log.error.called

    def test_command_timeout_inf_falls_back(self):
        action = CommandAction('test_command_action')
        with patch('action.commandaction.LOG') as mock_log:
            action.configure(command_timeout=float('inf'))
        assert action.command_timeout == DEFAULT_COMMAND_TIMEOUT
        assert mock_log.error.called

    def test_command_timeout_int_is_preserved(self):
        action = CommandAction('test_command_action')
        action.configure(command_timeout=5)
        assert action.command_timeout == 5
        assert isinstance(action.command_timeout, int)

    def test_command_timeout_float_is_preserved(self):
        action = CommandAction('test_command_action')
        action.configure(command_timeout=2.5)
        assert action.command_timeout == 2.5
        assert isinstance(action.command_timeout, float)

    def test_command_timeout_numeric_string_int_is_coerced(self):
        action = CommandAction('test_command_action')
        action.configure(command_timeout='5')
        assert action.command_timeout == 5
        assert isinstance(action.command_timeout, int)

    def test_command_timeout_numeric_string_float_is_coerced(self):
        action = CommandAction('test_command_action')
        action.configure(command_timeout='2.5')
        assert action.command_timeout == 2.5
        assert isinstance(action.command_timeout, float)

    def test_run_sanitizes_direct_invalid_string_timeout(self, caplog):
        action = CommandAction('test_command_action')
        action.run_command = 'echo hi'
        action.command_timeout = 'abc'
        result = action.run()
        assert result.success is True
        assert action.command_timeout == 'abc'
        assert 'not a number' in caplog.text

    def test_run_sanitizes_direct_none_timeout(self, caplog):
        action = CommandAction('test_command_action')
        action.run_command = 'echo hi'
        action.command_timeout = None
        result = action.run()
        assert result.success is True
        assert action.command_timeout is None
        assert 'expected a number' in caplog.text

    def test_run_coerces_direct_numeric_string_timeout_and_times_out(self):
        action = CommandAction('test_command_action')
        action.run_command = 'sleep 1'
        action.command_timeout = '0.1'
        result = action.run()
        assert result.success is False
        assert result.stderr == b'timeout'
        assert action.command_timeout == '0.1'


class TestCommandActionSecurity:
    """Security-focused tests for CommandAction"""

    def test_commandaction_placeholder_does_not_inject_shell_command(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo {MESSAGE}')
        result = action.run(placeholders={'{MESSAGE}': 'safe; echo INJECTED'})
        assert result[0]
        out = result[1]
        assert b'INJECTED' in out
        assert out.count(b'INJECTED') == 1

    def test_commandaction_run_does_not_mutate_run_command(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo {MESSAGE}')
        action.run(placeholders={'{MESSAGE}': 'first'})
        assert action.run_command == 'echo {MESSAGE}'
        result = action.run(placeholders={'{MESSAGE}': 'second'})
        assert result[0]
        assert b'second' in result[1]
        assert b'first' not in result[1]

    def test_commandaction_run_with_special_characters_in_placeholder(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='printf %s {MESSAGE}')
        result = action.run(placeholders={'{MESSAGE}': 'a b|c&d;e'})
        assert result[0]
        assert result[1] == b'a b|c&d;e'

    def test_commandaction_placeholder_intended_for_whole_token_usage(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo {MESSAGE}')
        result = action.run(placeholders={'{MESSAGE}': 'alpha beta'})
        assert result[0]
        assert result[1] == b'alpha beta'

    def test_commandaction_placeholder_embedded_in_quoted_literal_is_preserved_literally(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='printf %s "prefix {MESSAGE} suffix"')
        result = action.run(placeholders={'{MESSAGE}': 'a b|c&d;e'})
        assert result[0]
        # shlex.quote() wraps the value in single quotes, which become literal characters
        # inside the surrounding double quotes, so the special characters are preserved.
        assert result[1] == b"prefix 'a b|c&d;e' suffix"
