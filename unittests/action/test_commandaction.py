#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock
import os

from action.commandaction import CommandAction
from action.actiontype import ActionType


class TestCommandAction(object):
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
        assert action.run() == False

    def test_commandaction_run_with_empty_command(self):
        action = CommandAction('test_command_action')
        action.run_command = ''
        assert action.run() == False

    def test_commandaction_run_success(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo hello')
        result = action.run()
        assert result[0] == True
        assert b'hello' in result[1]

    def test_commandaction_run_with_error(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='ls /nonexistent_directory_12345')
        result = action.run()
        assert result[0] == False

    def test_commandaction_run_with_placeholders(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo {MESSAGE}')
        result = action.run(placeholders={'{MESSAGE}': 'test_placeholder'})
        assert result[0] == True
        assert b'test_placeholder' in result[1]

    def test_commandaction_run_with_working_dir(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='pwd', working_dir='/tmp')
        original_dir = os.getcwd()
        result = action.run()
        assert result[0] == True
        assert b'/tmp' in result[1]
        # Verify we're back to original directory
        assert os.getcwd() == original_dir

    def test_commandaction_run_switches_back_to_original_dir(self):
        action = CommandAction('test_command_action')
        action.configure(run_command='echo test', working_dir='/tmp')
        original_dir = os.getcwd()
        action.run()
        assert os.getcwd() == original_dir
