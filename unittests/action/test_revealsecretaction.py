#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock

from action.revealsecretaction import RevealSecretAction
from action.actiontype import ActionType


class TestRevealSecretAction(object):
    """Tests for RevealSecretAction"""

    def test_revealsecretaction_init(self):
        action = RevealSecretAction('test_reveal_action')
        assert action.id == 'test_reveal_action'
        assert action.action_type == ActionType.REVEALSECRET
        assert action.reveal_text is None
        assert action.reveal_link is None
        assert action.allow_reveal == False

    def test_revealsecretaction_configure(self):
        action = RevealSecretAction('test_reveal_action')
        action.configure(
            reveal_text='secret message',
            reveal_link='http://secret.link',
            allow_reveal=True
        )
        assert action.reveal_text == 'secret message'
        assert action.reveal_link == 'http://secret.link'
        assert action.allow_reveal == True

    def test_revealsecretaction_configure_partial(self):
        action = RevealSecretAction('test_reveal_action')
        action.configure(reveal_text='only text')
        assert action.reveal_text == 'only text'
        assert action.reveal_link is None
        assert action.allow_reveal == False

    def test_revealsecretaction_json_encodable(self):
        action = RevealSecretAction('test_reveal_action')
        action.configure(
            reveal_text='secret',
            reveal_link='http://link.com',
            allow_reveal=True,
            created=1609459200
        )
        result = action.json_encodable()
        assert result['id'] == 'test_reveal_action'
        assert result['action_type'] == ActionType.REVEALSECRET
        assert result['reveal_text'] == 'secret'
        assert result['reveal_link'] == 'http://link.com'
        assert result['allow_reveal'] == True

    @mock.patch.object(RevealSecretAction, 'save')
    def test_revealsecretaction_run(self, mock_save):
        action = RevealSecretAction('test_reveal_action')
        action.allow_reveal = False
        result = action.run()
        assert result == True
        assert action.allow_reveal == True
        mock_save.assert_called_once()
