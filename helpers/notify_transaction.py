#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from subprocess import Popen, PIPE

if __name__ == "__main__":
    # Create main parser
    parser = argparse.ArgumentParser(description='Notify transaction')
    parser.add_argument('url', help='The url to send the notification to')
    parser.add_argument('pr', help='The id of the payment request')
    parser.add_argument('txid', help='The transaction id')

    args = parser.parse_args()

    command = r'curl %s -H "Content-Type: application/json" -d "{\"payment_request_id\":\"%s\",\"txid\":\"%s\"}"' % (args.url, args.pr, args.txid)

    command_process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
    output, error = command_process.communicate()

