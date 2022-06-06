#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import requests
import platform
import psutil

from helpers.configurationhelpers import get_host, get_port
from helpers.loghelpers import LOG, logs_dir
from helpers.mailhelpers import sendmail
from helpers.runcommandprocess import RunCommandProcess

from helpers.ipfshelpers import add_str


def uptime_check(email, ipfs=False, reboot=False, ssl=None):
    LOG.info('CPU: %s%%' % psutil.cpu_percent())
    LOG.info('RAM: %s' % str(psutil.virtual_memory()))
    LOG.info('Checking if spellbook server is still online')

    if ssl is None:
        url = 'http://{host}:{port}/spellbook/ping'.format(host=get_host(), port=get_port())
    else:
        url = 'https://{host}:{port}/spellbook/ping'.format(host=ssl, port=get_port())
    try:
        r = requests.get(url=url, timeout=10)
        response = r.json()
    except Exception as ex:
        LOG.error('Unable to ping spellbook server: %s' % ex)
        response = {}

    online = True if 'success' in response and response['success'] is True else False

    if not online:
        LOG.error('Spellbook server is not online!')
        if email is not None:
            variables = {'HOST': get_host(),
                         'SPELLBOOK_LOG': get_recent_spellbook_log(),
                         'REQUESTS_LOG': get_recent_requests_log()}
            body_template = os.path.join('server_offline')
            success = sendmail(recipients=email,
                               subject='Spellbookserver @ %s is offline!' % get_host(),
                               body_template=body_template,
                               variables=variables)
            if success is True:
                LOG.info('Email sent successfully')

                if reboot is True and platform.system() == 'Linux':
                    LOG.info('Rebooting server because uptime check failed!')
                    RunCommandProcess(command='sudo reboot').run()

            else:
                LOG.error('Email to %s failed!' % email)
    else:
        LOG.info('Server is online')

    if ipfs is True:
        try:
            response = add_str('ping')
        except Exception as ex:
            LOG.error('IPFS node is offline: %s' % ex)
            if email is not None:
                variables = {'HOST': get_host()}
                body_template = os.path.join('ipfs_offline')
                success = sendmail(recipients=email,
                                   subject='IPFS node @ %s is offline!' % get_host(),
                                   body_template=body_template,
                                   variables=variables)
                if success is True:
                    LOG.info('Email sent successfully')

                    if reboot is True and platform.system() == 'Linux':
                        LOG.info('Rebooting server because ipfs node is offline!')
                        RunCommandProcess(command='sudo reboot').run()

                else:
                    LOG.error('Email to %s failed!' % email)



def get_recent_spellbook_log():
    with open(os.path.join(logs_dir, 'spellbook.txt'), 'r') as input_file:
        recent_messages = input_file.readlines()[-100:]

    return '<br>'.join(recent_messages)


def get_recent_requests_log():
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
