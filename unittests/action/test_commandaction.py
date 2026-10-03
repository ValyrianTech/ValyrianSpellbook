#!/usr/bin/env python
import ast
import os
from unittest import mock

from action.actiontype import ActionType
from action.commandaction import CommandAction


def _logged_command_output(mock_log):
    """Collect all stdout bytes the action logged via 'Command output: ...'."""
    out = b''
    for call in mock_log.info.call_args_list:
        msg = call.args[0]
        if isinstance(msg, str) and msg.startswith('Command output: '):
            raw = msg[len('Command output: '):]
            try:
                out += ast.literal_eval(raw)
            except (ValueError, SyntaxError):
                out += raw.encode()
    return out


class TestCommandAction:
    """Tests for CommandAction"""

    def test_commandaction_init(self):
        action = CommandAction('test_command_action')
        assert action.id == 'test_command_action'
        assert action.action_type == ActionType.COMMAND
        assert action.run_command is None
        assert action.working_dir is None

    def test_commandaction_configure(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo hello', working_dir='/tmp')
        assert action.run_command == 'echo hello'
        assert action.working_dir == '/tmp'

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
        with mock.patch('action.commandaction.LOG') as mock_log:
            result = action.run()
        assert result is True
        assert b'hello' in _logged_command_output(mock_log)

    def test_commandaction_run_with_error(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='ls /nonexistent_directory_12345')
        result = action.run()
        assert result is False

    def test_commandaction_run_with_missing_executable(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='this_command_does_not_exist_12345')
        result = action.run()
        assert result is False

    def test_commandaction_run_with_placeholders(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo {MESSAGE}')
        with mock.patch('action.commandaction.LOG') as mock_log:
            result = action.run(placeholders={'{MESSAGE}': 'test_placeholder'})
        assert result is True
        assert b'test_placeholder' in _logged_command_output(mock_log)

    def test_commandaction_run_with_working_dir(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='pwd', working_dir='/tmp')
        original_dir = os.getcwd()
        with mock.patch('action.commandaction.LOG') as mock_log:
            result = action.run()
        assert result is True
        # Verify we're back to original directory
        assert os.getcwd() == original_dir
        assert b'/tmp' in _logged_command_output(mock_log)

    def test_commandaction_run_switches_back_to_original_dir(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo test', working_dir='/tmp')
        original_dir = os.getcwd()
        action.run()
        assert os.getcwd() == original_dir


class TestCommandActionSecurity:
    """Security-focused tests for CommandAction"""

    def test_commandaction_placeholder_does_not_inject_shell_command(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo {MESSAGE}')
        with mock.patch('action.commandaction.LOG') as mock_log:
            result = action.run(placeholders={'{MESSAGE}': 'safe; echo INJECTED'})
        assert result is True
        assert _logged_command_output(mock_log).count(b'INJECTED') == 1

    def test_commandaction_run_does_not_mutate_run_command(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo {MESSAGE}')
        with mock.patch('action.commandaction.LOG') as mock_log:
            action.run(placeholders={'{MESSAGE}': 'first'})
            assert action.run_command == 'echo {MESSAGE}'
            mock_log.reset_mock()
            result = action.run(placeholders={'{MESSAGE}': 'second'})
        assert result is True
        logged = _logged_command_output(mock_log)
        assert b'second' in logged
        assert b'first' not in logged

    def test_commandaction_run_with_special_characters_in_placeholder(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='printf %s {MESSAGE}')
        with mock.patch('action.commandaction.LOG') as mock_log:
            result = action.run(placeholders={'{MESSAGE}': 'a b|c&d;e'})
        assert result is True
        assert _logged_command_output(mock_log) == b'a b|c&d;e'

    def test_commandaction_placeholder_intended_for_whole_token_usage(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo {MESSAGE}')
        with mock.patch('action.commandaction.LOG') as mock_log:
            result = action.run(placeholders={'{MESSAGE}': 'alpha beta'})
        assert result is True
        assert _logged_command_output(mock_log) == b'alpha beta'

    def test_commandaction_placeholder_embedded_in_quoted_literal_is_preserved_literally(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='printf %s "prefix {MESSAGE} suffix"')
        with mock.patch('action.commandaction.LOG') as mock_log:
            result = action.run(placeholders={'{MESSAGE}': 'a b|c&d;e'})
        assert result is True
        assert _logged_command_output(mock_log) == b"prefix 'a b|c&d;e' suffix"
