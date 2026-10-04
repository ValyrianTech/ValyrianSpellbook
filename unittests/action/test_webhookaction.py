#!/usr/bin/env python
from unittest import mock

import pytest
import requests

from action.actiontype import ActionType
from action.webhookaction import PinnedIPAdapter, WebhookAction


@pytest.fixture(autouse=True)
def _mock_valid_webhook_url():
    with mock.patch('action.webhookaction.valid_webhook_url', side_effect=lambda url: isinstance(url, str) and url.startswith('http')):
        yield


class TestWebhookAction:
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
        assert not action.run()

    @mock.patch('action.webhookaction.resolve_and_validate_webhook_url', return_value='8.8.8.8')
    @mock.patch('action.webhookaction.requests.Session')
    def test_webhookaction_run_get_success(self, mock_session_cls, _mock_resolve):
        mock_session = mock_session_cls.return_value
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'success'
        mock_session.get.return_value = mock_response

        action = WebhookAction('test_webhook_action')
        action.configure(webhook='http://example.com/webhook')
        result = action.run()
        assert result == (True, 'success')
        mock_session.get.assert_called_once_with('http://example.com/webhook', timeout=10, allow_redirects=False)

    @mock.patch('action.webhookaction.resolve_and_validate_webhook_url', return_value='8.8.8.8')
    @mock.patch('action.webhookaction.requests.Session')
    def test_webhookaction_run_get_failure_status(self, mock_session_cls, _mock_resolve):
        mock_session = mock_session_cls.return_value
        mock_response = mock.MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'error'
        mock_session.get.return_value = mock_response

        action = WebhookAction('test_webhook_action')
        action.configure(webhook='http://example.com/webhook')
        result = action.run()
        assert result == (False, 'error')

    @mock.patch('action.webhookaction.resolve_and_validate_webhook_url', return_value='8.8.8.8')
    @mock.patch('action.webhookaction.requests.Session')
    def test_webhookaction_run_post_success(self, mock_session_cls, _mock_resolve):
        mock_session = mock_session_cls.return_value
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'posted'
        mock_session.post.return_value = mock_response

        action = WebhookAction('test_webhook_action')
        action.configure(
            webhook='http://example.com/webhook',
            body='test data',
            request_type='POST'
        )
        result = action.run()
        assert result == (True, 'posted')
        mock_session.post.assert_called_once_with('http://example.com/webhook', data='test data', timeout=10, allow_redirects=False)

    @mock.patch('action.webhookaction.resolve_and_validate_webhook_url', return_value='8.8.8.8')
    def test_webhookaction_run_unsupported_request_type(self, _mock_resolve):
        action = WebhookAction('test_webhook_action')
        action.webhook = 'http://example.com/webhook'
        action.request_type = 'PUT'
        result = action.run()
        assert not result

    @mock.patch('action.webhookaction.resolve_and_validate_webhook_url', return_value=None)
    def test_webhookaction_run_request_time_revalidation_failure(self, _mock_resolve):
        action = WebhookAction('test_webhook_action')
        action.configure(webhook='http://example.com/webhook')
        result = action.run()
        assert not result

    def test_webhookaction_run_mounts_pinned_ip_adapter_on_both_schemes(self):
        with mock.patch('action.webhookaction.resolve_and_validate_webhook_url', return_value='8.8.8.8'), \
                mock.patch.object(requests.Session, 'mount') as mock_mount, \
                mock.patch.object(requests.Session, 'get') as mock_get:
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.text = 'ok'
            mock_get.return_value = mock_response

            action = WebhookAction('test_webhook_action')
            action.configure(webhook='http://example.com/webhook')
            result = action.run()

            assert result == (True, 'ok')

            adapter_mounts = [
                call for call in mock_mount.call_args_list
                if call.args and isinstance(call.args[1], PinnedIPAdapter)
            ]
            assert len(adapter_mounts) == 2
            assert {call.args[0] for call in adapter_mounts} == {'http://', 'https://'}
            adapters = [call.args[1] for call in adapter_mounts]
            assert adapters[0] is adapters[1]
            assert adapters[0].resolved_ip == '8.8.8.8'

    @mock.patch('action.webhookaction.resolve_and_validate_webhook_url', return_value='8.8.8.8')
    @mock.patch('action.webhookaction.requests.Session')
    def test_webhookaction_run_exception(self, mock_session_cls, _mock_resolve):
        mock_session = mock_session_cls.return_value
        mock_session.get.side_effect = ValueError('Connection error')

        action = WebhookAction('test_webhook_action')
        action.configure(webhook='http://example.com/webhook')
        result = action.run()
        assert not result

    @mock.patch('action.webhookaction.resolve_and_validate_webhook_url', return_value='8.8.8.8')
    @mock.patch('action.webhookaction.requests.Session')
    def test_webhookaction_run_requests_exception(self, mock_session_cls, _mock_resolve):
        mock_session = mock_session_cls.return_value
        mock_session.get.side_effect = requests.RequestException('Connection error')

        action = WebhookAction('test_webhook_action')
        action.configure(webhook='http://example.com/webhook')
        result = action.run()
        assert not result


class TestPinnedIPAdapter:
    """Tests for the SSRF-safe PinnedIPAdapter."""

    def test_init(self):
        adapter = PinnedIPAdapter('8.8.8.8')
        assert adapter.resolved_ip == '8.8.8.8'
        assert adapter.hostname is None

    def test_send_rewrites_url_and_host_without_port(self):
        adapter = PinnedIPAdapter('8.8.8.8')
        request = requests.Request('GET', 'http://example.com/webhook').prepare()
        with mock.patch.object(requests.adapters.HTTPAdapter, 'send', return_value='response') as mock_send:
            result = adapter.send(request)
        assert result == 'response'
        assert request.url == 'http://8.8.8.8/webhook'
        assert request.headers['Host'] == 'example.com'
        assert adapter.hostname == 'example.com'
        mock_send.assert_called_once_with(request, stream=False, timeout=None, verify=True, cert=None, proxies=None)

    def test_send_rewrites_url_and_host_with_port(self):
        adapter = PinnedIPAdapter('8.8.8.8')
        request = requests.Request('GET', 'http://example.com:8080/webhook').prepare()
        with mock.patch.object(requests.adapters.HTTPAdapter, 'send', return_value='response'):
            adapter.send(request)
        assert request.url == 'http://8.8.8.8:8080/webhook'
        assert request.headers['Host'] == 'example.com:8080'

    def test_build_connection_pool_key_attributes_sets_server_hostname(self):
        adapter = PinnedIPAdapter('8.8.8.8')
        adapter.hostname = 'example.com'
        request = requests.Request('GET', 'https://8.8.8.8/webhook').prepare()
        host_params, pool_kwargs = adapter.build_connection_pool_key_attributes(request, True, None)
        assert host_params['host'] == '8.8.8.8'
        assert pool_kwargs['server_hostname'] == 'example.com'

    def test_build_connection_pool_key_attributes_no_hostname(self):
        adapter = PinnedIPAdapter('8.8.8.8')
        request = requests.Request('GET', 'http://8.8.8.8/webhook').prepare()
        _host_params, pool_kwargs = adapter.build_connection_pool_key_attributes(request, True, None)
        assert 'server_hostname' not in pool_kwargs
