#!/usr/bin/env python

"""Action that sends data to a webhook URL."""

from urllib.parse import urlparse, urlunparse

import requests

from helpers.loghelpers import LOG
from validators.validators import resolve_and_validate_webhook_url, valid_webhook_url

from .action import Action
from .actionresult import ActionResult
from .actiontype import ActionType


class PinnedIPAdapter(requests.adapters.HTTPAdapter):
    """HTTPAdapter that pins the connection to a pre-resolved, validated IP address."""

    def __init__(self, resolved_ip, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resolved_ip = resolved_ip

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        parsed = urlparse(request.url)
        userinfo = ''
        if '@' in parsed.netloc:
            userinfo = parsed.netloc.rsplit('@', 1)[0] + '@'
        netloc = f'{userinfo}{self.resolved_ip}'
        if parsed.port is not None:
            netloc = f'{userinfo}{self.resolved_ip}:{parsed.port}'
        request.url = urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))

        host_header = parsed.hostname
        if parsed.port is not None:
            host_header = f'{parsed.hostname}:{parsed.port}'
        request.headers['Host'] = host_header

        return super().send(request, stream=stream, timeout=timeout, verify=verify, cert=cert, proxies=proxies)

    def build_connection_pool_key_attributes(self, request, verify, cert=None):
        host_params, pool_kwargs = super().build_connection_pool_key_attributes(request, verify, cert)

        # The Host header was pinned to the original hostname by send(). Derive the
        # server hostname from that header (immutable per-call request data) rather than
        # from mutable instance state shared across method calls.
        host_header = request.headers.get('Host')
        if host_header is not None:
            hostname = host_header.split(':', 1)[0]
            pool_kwargs['server_hostname'] = hostname

        return host_params, pool_kwargs


class WebhookAction(Action):
    """Action that sends data to a webhook URL."""
    def __init__(self, action_id):
        super().__init__(action_id=action_id)
        self.action_type = ActionType.WEBHOOK
        self.webhook = None
        self.body = None
        self.request_type = 'GET'

    def run(self):
        """
        Run the action

        :return: An ActionResult indicating success or failure, along with the
                 webhook response text on success
        """
        if self.webhook is None:
            return ActionResult(success=False)

        LOG.info(f'executing webhook: {self.webhook}')

        resolved_ip = resolve_and_validate_webhook_url(self.webhook)
        if resolved_ip is None:
            LOG.error(f'Webhook failed: {self.webhook} does not resolve to a public IP address')
            return ActionResult(success=False)

        session = requests.Session()
        adapter = PinnedIPAdapter(resolved_ip)
        try:
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            if self.request_type == 'GET':
                r = session.get(self.webhook, timeout=10, allow_redirects=False)
            elif self.request_type == 'POST':
                r = session.post(self.webhook, data=self.body, timeout=10, allow_redirects=False)
            else:
                LOG.error(f'Webhook failed: unsupported request type: {self.request_type}')
                return ActionResult(success=False)

        except (ValueError, KeyError, TypeError, OSError, requests.RequestException) as ex:
            LOG.error(f'Webhook failed: {ex}')
            return ActionResult(success=False)
        else:
            if r.status_code == 200:
                LOG.info(f'status code webhook: {r.status_code}')
                return ActionResult(success=True, stdout=r.text)
            else:
                LOG.error(f'Webhook failed: status code webhook: {r.status_code}')
                return ActionResult(success=False, stdout=r.text)
        finally:
            session.close()

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['webhook']    : An url of the webhook

        Note: the webhook URL must pass valid_webhook_url (which resolves DNS and rejects
        non-public/unresolvable hosts); invalid URLs are silently ignored and self.webhook
        remains None.
        """
        super().configure(**config)
        if 'webhook' in config and valid_webhook_url(config['webhook']):
            self.webhook = config['webhook']

        self.body = config.get('body', None)
        self.request_type = config.get('request_type', 'GET')

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super().json_encodable()
        ret.update({'webhook': self.webhook,
                    'body': self.body,
                    'request_type': self.request_type})
        return ret
