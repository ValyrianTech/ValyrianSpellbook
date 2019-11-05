#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import requests

from helpers.configurationhelpers import get_host, get_port
from helpers.loghelpers import LOG
from helpers.mailhelpers import sendmail


def uptime_check(email):
    LOG.info('Checking if spellbook server is still online')

    url = 'http://{host}:{port}/spellbook/ping'.format(host=get_host(), port=get_port())
    try:
        r = requests.get(url=url)
        response = r.json()
    except Exception as ex:
        LOG.error('Unable to ping spellbook server: %s' % ex)
        response = {}

    online = True if 'success' in response and response['success'] is True else False

    if not online:
        LOG.error('Spellbook server is not online!')
        if email is not None:
            variables = {'HOST': get_host()}
            body_template = os.path.join('server_offline')
            sendmail(recipients=email,
                     subject='Spellbookserver @ %s is offline!' % get_host(),
                     body_template=body_template,
                     variables=variables)
    else:
        LOG.info('Server is online')


if __name__ == "__main__":
    # Create main parser
    parser = argparse.ArgumentParser(description='Uptime check command line interface',
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('email', help='Send and email to this address if the server is not online', type=str)

    # Parse arguments
    args = parser.parse_args()

    uptime_check(email=args.email)
