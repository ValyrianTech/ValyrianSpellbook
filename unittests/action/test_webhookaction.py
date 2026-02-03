#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock

from action.webhookaction import WebhookAction
from action.actiontype import ActionType


class TestWebhookAction(object):
    """Tests for WebhookAction"""

    def test_webhookaction_init(self):
        action = WebhookAction('test_webhook_action')
        assert action.id == 'test_webhook_action'
        assert action.action_type == ActionType.WEBHOOK
        assert action.webhook is None
        assert action.body is None
        assert action.request_type == 'GET'

    def test_webhookaction_configure_with_valid_url(self):
        action = WebhookAction('test_webhook_action')
        action.configure(webhook='http://example.com/webhook')
        assert action.webhook == 'http://example.com/webhook'

    def test_webhookaction_configure_with_invalid_url(self):
        action = WebhookAction('test_webhook_action')
        action.configure(webhook='not_a_valid_url')
        assert action.webhook is None

    def test_webhookaction_configure_with_body_and_request_type(self):
        action = WebhookAction('test_webhook_action')
        action.configure(
            webhook='http://example.com/webhook',
            body='{"key": "value"}',
            request_type='POST'
        )
        assert action.body == '{"key": "value"}'
        assert action.request_type == 'POST'

    def test_webhookaction_json_encodable(self):
        action = WebhookAction('test_webhook_action')
        action.configure(
            webhook='http://example.com/webhook',
            body='test body',
            request_type='POST',
            created=1609459200
        )
        result = action.json_encodable()
        assert result['id'] == 'test_webhook_action'
        assert result['action_type'] == ActionType.WEBHOOK
        assert result['webhook'] == 'http://example.com/webhook'
        assert result['body'] == 'test body'
        assert result['request_type'] == 'POST'

    def test_webhookaction_run_with_no_webhook(self):
        action = WebhookAction('test_webhook_action')
        assert action.run() == False

    @mock.patch('action.webhookaction.requests.get')
    def test_webhookaction_run_get_success(self, mock_get):
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'success'
        mock_get.return_value = mock_response

        action = WebhookAction('test_webhook_action')
        action.configure(webhook='http://example.com/webhook')
        result = action.run()
        assert result == (True, 'success')
        mock_get.assert_called_once_with('http://example.com/webhook')

    @mock.patch('action.webhookaction.requests.get')
    def test_webhookaction_run_get_failure_status(self, mock_get):
        mock_response = mock.MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'error'
        mock_get.return_value = mock_response

        action = WebhookAction('test_webhook_action')
        action.configure(webhook='http://example.com/webhook')
        result = action.run()
        assert result == (False, 'error')

    @mock.patch('action.webhookaction.requests.post')
    def test_webhookaction_run_post_success(self, mock_post):
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'posted'
        mock_post.return_value = mock_response

        action = WebhookAction('test_webhook_action')
        action.configure(
            webhook='http://example.com/webhook',
            body='test data',
            request_type='POST'
        )
        result = action.run()
        assert result == (True, 'posted')
        mock_post.assert_called_once_with('http://example.com/webhook', data='test data')

    def test_webhookaction_run_unsupported_request_type(self):
        action = WebhookAction('test_webhook_action')
        action.webhook = 'http://example.com/webhook'
        action.request_type = 'PUT'
        result = action.run()
        assert result == False

    @mock.patch('action.webhookaction.requests.get')
    def test_webhookaction_run_exception(self, mock_get):
        mock_get.side_effect = Exception('Connection error')

        action = WebhookAction('test_webhook_action')
        action.configure(webhook='http://example.com/webhook')
        result = action.run()
        assert result == False
