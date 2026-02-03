#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock

from action.sendmailaction import SendMailAction
from action.actiontype import ActionType


class TestSendMailAction(object):
    """Tests for SendMailAction"""

    def test_sendmailaction_init(self):
        action = SendMailAction('test_mail_action')
        assert action.id == 'test_mail_action'
        assert action.action_type == ActionType.SENDMAIL
        assert action.mail_recipients is None
        assert action.mail_subject is None
        assert action.mail_body_template is None
        assert action.mail_variables is None
        assert action.mail_images is None
        assert action.mail_attachments is None

    def test_sendmailaction_configure(self):
        action = SendMailAction('test_mail_action')
        action.configure(
            mail_recipients='test@example.com',
            mail_subject='Test Subject',
            mail_body_template='template.html',
            mail_variables={'name': 'Test'},
            mail_images={'logo': 'logo.png'},
            mail_attachments={'doc': 'file.pdf'}
        )
        assert action.mail_recipients == 'test@example.com'
        assert action.mail_subject == 'Test Subject'
        assert action.mail_body_template == 'template.html'
        assert action.mail_variables == {'name': 'Test'}
        assert action.mail_images == {'logo': 'logo.png'}
        assert action.mail_attachments == {'doc': 'file.pdf'}

    def test_sendmailaction_configure_ignores_non_dict_variables(self):
        action = SendMailAction('test_mail_action')
        action.configure(
            mail_variables='not a dict',
            mail_images='not a dict',
            mail_attachments='not a dict'
        )
        assert action.mail_variables is None
        assert action.mail_images is None
        assert action.mail_attachments is None

    def test_sendmailaction_json_encodable(self):
        action = SendMailAction('test_mail_action')
        action.configure(
            mail_recipients='test@example.com',
            mail_subject='Subject',
            mail_body_template='template.html',
            mail_variables={'key': 'value'},
            mail_images={'img': 'image.png'},
            mail_attachments={'att': 'file.pdf'},
            created=1609459200
        )
        result = action.json_encodable()
        assert result['id'] == 'test_mail_action'
        assert result['action_type'] == ActionType.SENDMAIL
        assert result['mail_recipients'] == 'test@example.com'
        assert result['mail_subject'] == 'Subject'
        assert result['mail_body_template'] == 'template.html'
        assert result['mail_variables'] == {'key': 'value'}
        assert result['mail_images'] == {'img': 'image.png'}
        assert result['mail_attachments'] == {'att': 'file.pdf'}

    @mock.patch('action.sendmailaction.sendmail')
    def test_sendmailaction_run(self, mock_sendmail):
        mock_sendmail.return_value = True
        action = SendMailAction('test_mail_action')
        action.configure(
            mail_recipients='test@example.com',
            mail_subject='Subject',
            mail_body_template='template.html'
        )
        result = action.run()
        assert result == True
        mock_sendmail.assert_called_once_with(
            recipients='test@example.com',
            subject='Subject',
            body_template='template.html',
            variables=None,
            images=None,
            attachments=None
        )
