#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for uptime_check.py — server uptime monitoring CLI.

uptime_check.py has a __main__ guard, so functions are importable without
side effects. We test uptime_check(), get_recent_spellbook_log(), and
get_recent_requests_log() with mocked dependencies.
"""
import mock
import pytest
import os
import sys
import runpy
import subprocess

import uptime_check

_UPTIME_CHECK_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uptime_check.py')


class TestUptimeCheckOnline:

    @mock.patch('uptime_check.psutil.virtual_memory')
    @mock.patch('uptime_check.psutil.cpu_percent', return_value=10.0)
    @mock.patch('uptime_check.requests.get')
    @mock.patch('uptime_check.get_port', return_value=42069)
    @mock.patch('uptime_check.get_host', return_value='1.2.3.4')
    def test_server_online(self, mock_host, mock_port, mock_get, mock_cpu, mock_ram):
        mock_get.return_value.json.return_value = {'success': True}
        uptime_check.uptime_check(email=None)
        mock_get.assert_called_once()

    @mock.patch('uptime_check.psutil.virtual_memory')
    @mock.patch('uptime_check.psutil.cpu_percent', return_value=10.0)
    @mock.patch('uptime_check.requests.get')
    @mock.patch('uptime_check.get_port', return_value=42069)
    @mock.patch('uptime_check.get_host', return_value='1.2.3.4')
    def test_server_online_no_email(self, mock_host, mock_port, mock_get, mock_cpu, mock_ram):
        mock_get.return_value.json.return_value = {'success': True}
        uptime_check.uptime_check(email=None)
        # No email sent when server is online

    @mock.patch('uptime_check.psutil.virtual_memory')
    @mock.patch('uptime_check.psutil.cpu_percent', return_value=10.0)
    @mock.patch('uptime_check.requests.get')
    @mock.patch('uptime_check.get_port', return_value=42069)
    @mock.patch('uptime_check.get_host', return_value='1.2.3.4')
    def test_server_online_with_ssl(self, mock_host, mock_port, mock_get, mock_cpu, mock_ram):
        mock_get.return_value.json.return_value = {'success': True}
        uptime_check.uptime_check(email=None, ssl='mydomain.com')
        call_args = mock_get.call_args
        assert 'https://' in call_args[1]['url']

    @mock.patch('uptime_check.psutil.virtual_memory')
    @mock.patch('uptime_check.psutil.cpu_percent', return_value=10.0)
    @mock.patch('uptime_check.requests.get')
    @mock.patch('uptime_check.get_port', return_value=42069)
    @mock.patch('uptime_check.get_host', return_value='1.2.3.4')
    def test_server_online_without_ssl(self, mock_host, mock_port, mock_get, mock_cpu, mock_ram):
        mock_get.return_value.json.return_value = {'success': True}
        uptime_check.uptime_check(email=None, ssl=None)
        call_args = mock_get.call_args
        assert 'http://' in call_args[1]['url']


class TestUptimeCheckOffline:

    @mock.patch('uptime_check.psutil.virtual_memory')
    @mock.patch('uptime_check.psutil.cpu_percent', return_value=10.0)
    @mock.patch('uptime_check.requests.get')
    @mock.patch('uptime_check.get_port', return_value=42069)
    @mock.patch('uptime_check.get_host', return_value='1.2.3.4')
    def test_server_offline_no_email(self, mock_host, mock_port, mock_get, mock_cpu, mock_ram):
        mock_get.return_value.json.return_value = {'success': False}
        uptime_check.uptime_check(email=None)

    @mock.patch('uptime_check.psutil.virtual_memory')
    @mock.patch('uptime_check.psutil.cpu_percent', return_value=10.0)
    @mock.patch('uptime_check.requests.get')
    @mock.patch('uptime_check.get_port', return_value=42069)
    @mock.patch('uptime_check.get_host', return_value='1.2.3.4')
    def test_server_offline_sends_email(self, mock_host, mock_port, mock_get, mock_cpu, mock_ram,
                                        mock_sendmail=None):
        mock_get.return_value.json.return_value = {'success': False}
        with mock.patch('uptime_check.sendmail', return_value=True) as mock_mail, \
             mock.patch('uptime_check.get_recent_spellbook_log', return_value='log'), \
             mock.patch('uptime_check.get_recent_requests_log', return_value='req_log'):
            uptime_check.uptime_check(email='admin@example.com')
            mock_mail.assert_called_once()

    @mock.patch('uptime_check.psutil.virtual_memory')
    @mock.patch('uptime_check.psutil.cpu_percent', return_value=10.0)
    @mock.patch('uptime_check.requests.get')
    @mock.patch('uptime_check.get_port', return_value=42069)
    @mock.patch('uptime_check.get_host', return_value='1.2.3.4')
    def test_server_offline_email_failure(self, mock_host, mock_port, mock_get, mock_cpu, mock_ram):
        mock_get.return_value.json.return_value = {'success': False}
        with mock.patch('uptime_check.sendmail', return_value=False) as mock_mail, \
             mock.patch('uptime_check.get_recent_spellbook_log', return_value='log'), \
             mock.patch('uptime_check.get_recent_requests_log', return_value='req_log'):
            uptime_check.uptime_check(email='admin@example.com')
            mock_mail.assert_called_once()

    @mock.patch('uptime_check.psutil.virtual_memory')
    @mock.patch('uptime_check.psutil.cpu_percent', return_value=10.0)
    @mock.patch('uptime_check.requests.get')
    @mock.patch('uptime_check.get_port', return_value=42069)
    @mock.patch('uptime_check.get_host', return_value='1.2.3.4')
    def test_server_offline_reboot_linux(self, mock_host, mock_port, mock_get, mock_cpu, mock_ram):
        mock_get.return_value.json.return_value = {'success': False}
        with mock.patch('uptime_check.sendmail', return_value=True), \
             mock.patch('uptime_check.get_recent_spellbook_log', return_value='log'), \
             mock.patch('uptime_check.get_recent_requests_log', return_value='req_log'), \
             mock.patch('uptime_check.platform.system', return_value='Linux'), \
             mock.patch('uptime_check.RunCommandProcess') as mock_reboot:
            uptime_check.uptime_check(email='admin@example.com', reboot=True)
            mock_reboot.assert_called_once_with(command='sudo reboot')

    @mock.patch('uptime_check.psutil.virtual_memory')
    @mock.patch('uptime_check.psutil.cpu_percent', return_value=10.0)
    @mock.patch('uptime_check.requests.get')
    @mock.patch('uptime_check.get_port', return_value=42069)
    @mock.patch('uptime_check.get_host', return_value='1.2.3.4')
    def test_server_offline_no_reboot_non_linux(self, mock_host, mock_port, mock_get, mock_cpu, mock_ram):
        mock_get.return_value.json.return_value = {'success': False}
        with mock.patch('uptime_check.sendmail', return_value=True), \
             mock.patch('uptime_check.get_recent_spellbook_log', return_value='log'), \
             mock.patch('uptime_check.get_recent_requests_log', return_value='req_log'), \
             mock.patch('uptime_check.platform.system', return_value='Windows'), \
             mock.patch('uptime_check.RunCommandProcess') as mock_reboot:
            uptime_check.uptime_check(email='admin@example.com', reboot=True)
            mock_reboot.assert_not_called()

    @mock.patch('uptime_check.psutil.virtual_memory')
    @mock.patch('uptime_check.psutil.cpu_percent', return_value=10.0)
    @mock.patch('uptime_check.requests.get')
    @mock.patch('uptime_check.get_port', return_value=42069)
    @mock.patch('uptime_check.get_host', return_value='1.2.3.4')
    def test_server_offline_request_exception(self, mock_host, mock_port, mock_get, mock_cpu, mock_ram):
        mock_get.side_effect = Exception('Connection refused')
        with mock.patch('uptime_check.sendmail', return_value=True) as mock_mail, \
             mock.patch('uptime_check.get_recent_spellbook_log', return_value='log'), \
             mock.patch('uptime_check.get_recent_requests_log', return_value='req_log'):
            uptime_check.uptime_check(email='admin@example.com')
            mock_mail.assert_called_once()


class TestUptimeCheckIpfs:

    @mock.patch('uptime_check.psutil.virtual_memory')
    @mock.patch('uptime_check.psutil.cpu_percent', return_value=10.0)
    @mock.patch('uptime_check.requests.get')
    @mock.patch('uptime_check.get_port', return_value=42069)
    @mock.patch('uptime_check.get_host', return_value='1.2.3.4')
    def test_ipfs_online(self, mock_host, mock_port, mock_get, mock_cpu, mock_ram):
        mock_get.return_value.json.return_value = {'success': True}
        with mock.patch('uptime_check.check_ipfs', return_value=True):
            uptime_check.uptime_check(email=None, ipfs=True)

    @mock.patch('uptime_check.psutil.virtual_memory')
    @mock.patch('uptime_check.psutil.cpu_percent', return_value=10.0)
    @mock.patch('uptime_check.requests.get')
    @mock.patch('uptime_check.get_port', return_value=42069)
    @mock.patch('uptime_check.get_host', return_value='1.2.3.4')
    def test_ipfs_offline_sends_email(self, mock_host, mock_port, mock_get, mock_cpu, mock_ram):
        mock_get.return_value.json.return_value = {'success': True}
        with mock.patch('uptime_check.check_ipfs', side_effect=Exception('IPFS down')), \
             mock.patch('uptime_check.sendmail', return_value=True) as mock_mail:
            uptime_check.uptime_check(email='admin@example.com', ipfs=True)
            mock_mail.assert_called_once()

    @mock.patch('uptime_check.psutil.virtual_memory')
    @mock.patch('uptime_check.psutil.cpu_percent', return_value=10.0)
    @mock.patch('uptime_check.requests.get')
    @mock.patch('uptime_check.get_port', return_value=42069)
    @mock.patch('uptime_check.get_host', return_value='1.2.3.4')
    def test_ipfs_offline_reboot_linux(self, mock_host, mock_port, mock_get, mock_cpu, mock_ram):
        mock_get.return_value.json.return_value = {'success': True}
        with mock.patch('uptime_check.check_ipfs', side_effect=Exception('IPFS down')), \
             mock.patch('uptime_check.sendmail', return_value=True), \
             mock.patch('uptime_check.platform.system', return_value='Linux'), \
             mock.patch('uptime_check.RunCommandProcess') as mock_reboot:
            uptime_check.uptime_check(email='admin@example.com', ipfs=True, reboot=True)
            mock_reboot.assert_called_once_with(command='sudo reboot')

    @mock.patch('uptime_check.psutil.virtual_memory')
    @mock.patch('uptime_check.psutil.cpu_percent', return_value=10.0)
    @mock.patch('uptime_check.requests.get')
    @mock.patch('uptime_check.get_port', return_value=42069)
    @mock.patch('uptime_check.get_host', return_value='1.2.3.4')
    def test_ipfs_offline_no_email(self, mock_host, mock_port, mock_get, mock_cpu, mock_ram):
        mock_get.return_value.json.return_value = {'success': True}
        with mock.patch('uptime_check.check_ipfs', side_effect=Exception('IPFS down')):
            uptime_check.uptime_check(email=None, ipfs=True)


class TestGetRecentLogs:

    def test_get_recent_spellbook_log(self):
        lines = ['line1\n', 'line2\n', 'line3\n']
        with mock.patch('builtins.open', new_callable=mock.mock_open, read_data=''.join(lines)):
            result = uptime_check.get_recent_spellbook_log()
            assert 'line1' in result

    def test_get_recent_requests_log(self):
        lines = ['req1\n', 'req2\n']
        with mock.patch('builtins.open', new_callable=mock.mock_open, read_data=''.join(lines)):
            result = uptime_check.get_recent_requests_log()
            assert 'req1' in result


class TestUptimeCheckIpfsEmailFailure:

    @mock.patch('uptime_check.psutil.virtual_memory')
    @mock.patch('uptime_check.psutil.cpu_percent', return_value=10.0)
    @mock.patch('uptime_check.requests.get')
    @mock.patch('uptime_check.get_port', return_value=42069)
    @mock.patch('uptime_check.get_host', return_value='1.2.3.4')
    def test_ipfs_offline_email_failure(self, mock_host, mock_port, mock_get, mock_cpu, mock_ram):
        mock_get.return_value.json.return_value = {'success': True}
        with mock.patch('uptime_check.check_ipfs', side_effect=Exception('IPFS down')), \
             mock.patch('uptime_check.sendmail', return_value=False) as mock_mail:
            uptime_check.uptime_check(email='admin@example.com', ipfs=True)
            mock_mail.assert_called_once()


class TestUptimeCheckMainGuard:

    def test_main_guard_help(self):
        """Running with --help covers the argparse setup in the __main__ guard."""
        result = subprocess.run([sys.executable, _UPTIME_CHECK_PATH, '--help'],
                                capture_output=True, text=True)
        assert result.returncode == 0
        assert 'email' in result.stdout

    def test_main_guard_full_run(self):
        """Running via runpy with mocked deps covers the full __main__ guard."""
        with mock.patch('sys.argv', ['uptime_check.py', 'admin@example.com']):
            with mock.patch('helpers.configurationhelpers.get_host', return_value='1.2.3.4'), \
                 mock.patch('helpers.configurationhelpers.get_port', return_value=42069), \
                 mock.patch('requests.get') as mock_get, \
                 mock.patch('psutil.virtual_memory'), \
                 mock.patch('psutil.cpu_percent', return_value=10.0):
                mock_get.return_value.json.return_value = {'success': True}
                runpy.run_path(_UPTIME_CHECK_PATH, run_name='__main__')
