#!/usr/bin/env python

"""Standalone uptime monitoring script for the Spellbook server."""

import argparse
import os
import platform

import psutil
import requests

from helpers.configurationhelpers import get_host, get_port
from helpers.ipfshelpers import check_ipfs
from helpers.loghelpers import LOG, logs_dir
from helpers.mailhelpers import sendmail
from helpers.runcommandprocess import RunCommandProcess


def uptime_check(email, ipfs=False, reboot=False, ssl=None):
    """Check if the Spellbook server is online and optionally verify IPFS node status."""
    LOG.info(f'CPU: {psutil.cpu_percent()}%')
    LOG.info(f'RAM: {psutil.virtual_memory()!s}')
    LOG.info('Checking if spellbook server is still online')

    if ssl is None:
        url = f'http://{get_host()}:{get_port()}/spellbook/ping'
    else:
        url = f'https://{ssl}:{get_port()}/spellbook/ping'
    try:
        r = requests.get(url=url, timeout=10)
        response = r.json()
    except (ValueError, KeyError, TypeError, OSError) as ex:
        LOG.error(f'Unable to ping spellbook server: {ex}')
        response = {}

    online = bool('success' in response and response['success'] is True)

    if not online:
        LOG.error('Spellbook server is not online!')
        if email is not None:
            variables = {'HOST': get_host(),
                         'SPELLBOOK_LOG': get_recent_spellbook_log(),
                         'REQUESTS_LOG': get_recent_requests_log()}
            body_template = os.path.join('server_offline')
            success = sendmail(recipients=email,
                               subject=f'Spellbookserver @ {get_host()} is offline!',
                               body_template=body_template,
                               variables=variables)
            if success is True:
                LOG.info('Email sent successfully')

                if reboot is True and platform.system() == 'Linux':
                    LOG.info('Rebooting server because uptime check failed!')
                    RunCommandProcess(command='sudo reboot').run()

            else:
                LOG.error(f'Email to {email} failed!')
    else:
        LOG.info('Server is online')

    if ipfs is True:
        try:
            response = check_ipfs()
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'IPFS node is offline: {ex}')
            if email is not None:
                variables = {'HOST': get_host()}
                body_template = os.path.join('ipfs_offline')
                success = sendmail(recipients=email,
                                   subject=f'IPFS node @ {get_host()} is offline!',
                                   body_template=body_template,
                                   variables=variables)
                if success is True:
                    LOG.info('Email sent successfully')

                    if reboot is True and platform.system() == 'Linux':
                        LOG.info('Rebooting server because ipfs node is offline!')
                        RunCommandProcess(command='sudo reboot').run()

                else:
                    LOG.error(f'Email to {email} failed!')


def get_recent_spellbook_log():
    """Return the last 100 lines of the spellbook log as an HTML string."""
    with open(os.path.join(logs_dir, 'spellbook.txt'), 'r') as input_file:
        recent_messages = input_file.readlines()[-100:]

    return '<br>'.join(recent_messages)


def get_recent_requests_log():
    """Return the last 100 lines of the requests log as an HTML string."""
    with open(os.path.join(logs_dir, 'requests.txt'), 'r') as input_file:
        recent_messages = input_file.readlines()[-100:]

    return '<br>'.join(recent_messages)


if __name__ == "__main__":
    # Create main parser
    parser = argparse.ArgumentParser(description='Uptime check command line interface',
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('email', help='Send and email to this address if the server is not online', type=str)
    parser.add_argument('--ipfs', help='Also check if ipfs node is still online', action='store_true')
    parser.add_argument('--reboot', help='Immediately reboot the server when ping fails, only works on linux', action='store_true')
    parser.add_argument('--ssl', help='This server is configured to use SSL', type=str)

    # Parse arguments
    args = parser.parse_args()

    uptime_check(email=args.email, ipfs=args.ipfs, reboot=args.reboot, ssl=args.ssl)
