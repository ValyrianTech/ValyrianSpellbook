#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock
import time
from datetime import datetime

from action.action import Action, ACTIONS_DIR
from action.actiontype import ActionType
from action.transactiontype import TransactionType


class TestActionType(object):
    """Tests for ActionType constants"""

    def test_action_type_constants(self):
        assert ActionType.COMMAND == 'Command'
        assert ActionType.SPAWNPROCESS == 'SpawnProcess'
        assert ActionType.REVEALSECRET == 'RevealSecret'
        assert ActionType.SENDMAIL == 'SendMail'
        assert ActionType.WEBHOOK == 'Webhook'
        assert ActionType.SENDTRANSACTION == 'SendTransaction'
        assert ActionType.DELETETRIGGER == 'DeleteTrigger'
        assert ActionType.LAUNCHEVOLVER == 'LaunchEvolver'

    def test_twitter_action_type_constants(self):
        assert ActionType.LIKE_TWEET == 'Like tweet'
        assert ActionType.UNLIKE_TWEET == 'Unlike tweet'
        assert ActionType.RETWEET == 'Retweet'
        assert ActionType.UNRETWEET == 'Unretweet'
        assert ActionType.CREATE_TWEET == 'Create tweet'
        assert ActionType.DELETE_TWEET == 'Delete tweet'
        assert ActionType.SEND_DM_TWITTER == 'Send direct message on twitter'
        assert ActionType.FOLLOW_ON_TWITTER == 'Follow on twitter'
        assert ActionType.UNFOLLOW_ON_TWITTER == 'Unfollow on twitter'


class TestTransactionType(object):
    """Tests for TransactionType constants"""

    def test_transaction_type_constants(self):
        assert TransactionType.SEND2SINGLE == 'Send2Single'
        assert TransactionType.SEND2MANY == 'Send2Many'
        assert TransactionType.SEND2SIL == 'Send2SIL'
        assert TransactionType.SEND2LBL == 'Send2LBL'
        assert TransactionType.SEND2LRL == 'Send2LRL'
        assert TransactionType.SEND2LSL == 'Send2LSL'
        assert TransactionType.SEND2LAL == 'Send2LAL'


class ConcreteAction(Action):
    """Concrete implementation of Action for testing the abstract base class"""

    def run(self, **kwargs):
        return True


class TestAction(object):
    """Tests for the Action base class"""

    def test_action_init(self):
        action = ConcreteAction('test_action_id')
        assert action.id == 'test_action_id'
        assert action.action_type is None
        assert action.created is None

    def test_action_configure_with_created_timestamp(self):
        action = ConcreteAction('test_action_id')
        timestamp = 1609459200  # 2021-01-01 00:00:00 UTC
        action.configure(created=timestamp)
        assert action.created == datetime.fromtimestamp(timestamp)

    def test_action_configure_without_created(self):
        action = ConcreteAction('test_action_id')
        before = datetime.now()
        action.configure()
        after = datetime.now()
        assert before <= action.created <= after

    def test_action_configure_with_valid_action_type(self):
        action = ConcreteAction('test_action_id')
        action.configure(action_type='Command')
        assert action.action_type == 'Command'

    def test_action_configure_with_invalid_action_type(self):
        action = ConcreteAction('test_action_id')
        action.configure(action_type='InvalidType')
        assert action.action_type is None

    def test_action_json_encodable(self):
        action = ConcreteAction('test_action_id')
        action.configure(action_type='Command', created=1609459200)
        result = action.json_encodable()
        assert result['id'] == 'test_action_id'
        assert result['action_type'] == 'Command'
        assert result['created'] == 1609459200

    def test_action_json_encodable_sets_created_if_none(self):
        action = ConcreteAction('test_action_id')
        action.created = None
        before = int(time.mktime(datetime.now().timetuple()))
        result = action.json_encodable()
        after = int(time.mktime(datetime.now().timetuple()))
        assert before <= result['created'] <= after

    @mock.patch('action.action.save_to_json_file')
    def test_action_save(self, mock_save):
        action = ConcreteAction('test_action_id')
        action.configure(action_type='Command', created=1609459200)
        action.save()
        mock_save.assert_called_once()
        call_args = mock_save.call_args
        assert 'test_action_id.json' in call_args[0][0]

    def test_action_run(self):
        action = ConcreteAction('test_action_id')
        assert action.run() == True
