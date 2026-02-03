#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock

from action.deletetriggeraction import DeleteTriggerAction
from action.actiontype import ActionType


class TestDeleteTriggerAction(object):
    """Tests for DeleteTriggerAction"""

    def test_deletetriggeraction_init(self):
        action = DeleteTriggerAction('test_delete_action')
        assert action.id == 'test_delete_action'
        assert action.action_type == ActionType.DELETETRIGGER
        assert action.trigger_ids == []

    def test_deletetriggeraction_configure(self):
        action = DeleteTriggerAction('test_delete_action')
        action.configure(trigger_ids=['trigger1', 'trigger2'])
        assert action.trigger_ids == ['trigger1', 'trigger2']

    def test_deletetriggeraction_json_encodable(self):
        action = DeleteTriggerAction('test_delete_action')
        action.configure(trigger_ids=['trigger1'], created=1609459200)
        result = action.json_encodable()
        assert result['id'] == 'test_delete_action'
        assert result['action_type'] == ActionType.DELETETRIGGER
        assert result['trigger_ids'] == ['trigger1']

    def test_deletetriggeraction_run_with_no_trigger_ids(self):
        action = DeleteTriggerAction('test_delete_action')
        action.trigger_ids = None
        result = action.run()
        assert result == False

    def test_deletetriggeraction_run_with_empty_trigger_ids(self):
        action = DeleteTriggerAction('test_delete_action')
        action.trigger_ids = []
        result = action.run()
        assert result == False

    @mock.patch('helpers.triggerhelpers.delete_trigger')
    @mock.patch('helpers.triggerhelpers.get_triggers')
    def test_deletetriggeraction_run_success(self, mock_get_triggers, mock_delete_trigger):
        mock_get_triggers.return_value = {'trigger1': {}, 'trigger2': {}}

        action = DeleteTriggerAction('test_delete_action')
        action.configure(trigger_ids=['trigger1', 'trigger2'])
        result = action.run()

        assert result == True
        assert mock_delete_trigger.call_count == 2
        mock_delete_trigger.assert_any_call(trigger_id='trigger1')
        mock_delete_trigger.assert_any_call(trigger_id='trigger2')

    @mock.patch('helpers.triggerhelpers.delete_trigger')
    @mock.patch('helpers.triggerhelpers.get_triggers')
    def test_deletetriggeraction_run_unknown_trigger(self, mock_get_triggers, mock_delete_trigger):
        mock_get_triggers.return_value = {'trigger1': {}}

        action = DeleteTriggerAction('test_delete_action')
        action.configure(trigger_ids=['trigger1', 'unknown_trigger'])
        result = action.run()

        assert result == True
        # Only trigger1 should be deleted, unknown_trigger is skipped
        mock_delete_trigger.assert_called_once_with(trigger_id='trigger1')
