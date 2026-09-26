#!/usr/bin/env python
import os

from action.actiontype import ActionType
from action.commandaction import CommandAction


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
        result = action.run()
        assert result[0]
        assert b'hello' in result[1]

    def test_commandaction_run_with_error(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='ls /nonexistent_directory_12345')
        result = action.run()
        assert not result[0]

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
