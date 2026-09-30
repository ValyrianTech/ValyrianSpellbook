#!/usr/bin/env python
"""Standalone script that sends a transaction notification via curl to a webhook URL."""

import argparse
from subprocess import PIPE, Popen

if __name__ == "__main__":
    # Create main parser
    parser = argparse.ArgumentParser(description='Notify transaction')
    parser.add_argument('url', help='The url to send the notification to')
    parser.add_argument('pr', help='The id of the payment request')
    parser.add_argument('txid', help='The transaction id')

    args = parser.parse_args()

    command = rf'curl {args.url} -H "Content-Type: application/json" -d "{{\"payment_request_id\":\"{args.pr}\",\"txid\":\"{args.txid}\"}}"'

    command_process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
    output, error = command_process.communicate()

