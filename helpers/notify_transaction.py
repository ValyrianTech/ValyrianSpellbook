#!/usr/bin/env python
"""Standalone script that sends a transaction notification to a webhook URL via an HTTP POST."""

import argparse
import requests

if __name__ == "__main__":
    # Create main parser
    parser = argparse.ArgumentParser(description='Notify transaction')
    parser.add_argument('url', help='The url to send the notification to')
    parser.add_argument('pr', help='The id of the payment request')
    parser.add_argument('txid', help='The transaction id')

    args = parser.parse_args()

    resp = requests.post(args.url, json={'payment_request_id': args.pr, 'txid': args.txid}, timeout=10)
    resp.raise_for_status()

