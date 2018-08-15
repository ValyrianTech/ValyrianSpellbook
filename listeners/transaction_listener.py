#!/usr/bin/python
# -*- coding: utf-8 -*-

import websocket
import simplejson
import argparse
import sys
import os
import time
import logging
from logging.handlers import RotatingFileHandler
from helpers.runcommandprocess import RunCommandProcess

LOG = logging.getLogger('transaction_listener_log')

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
LOG.addHandler(stream_handler)

# make the directory for logs if it doesn't exist
logs_dir = os.path.join('logs')
if not os.path.isdir(logs_dir):
    os.makedirs(logs_dir)

file_handler = RotatingFileHandler(os.path.join('logs', 'transaction_listener_log.txt'), maxBytes=10000000, backupCount=5)
file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
LOG.addHandler(file_handler)

LOG.setLevel(logging.WARNING)

WATCHLIST = {}
EXIT_ON_EVENT = False
EXIT_ON_TIMEOUT = None


def on_message(ws, message):
    event_found = False
    transaction = simplejson.loads(message)
    if transaction['type'] != 'new-transaction':
        return

    LOG.info('New transaction: %s' % transaction['payload']['txid'])
    LOG.info('\tFrom: ')
    for tx_input in transaction['payload']['inputs']:
        for input_address in tx_input['addresses']:
            LOG.info('\t\t%s -> %s' % (input_address, tx_input['value_int']))
            if input_address in WATCHLIST and 'SEND' in WATCHLIST[input_address]:

                event_found = True
                command = WATCHLIST[input_address]['SEND']
                command = command.replace('#txid#', transaction['payload']['txid'])
                LOG.info('Executing command: %s' % command)
                run_command_process = RunCommandProcess(command=command)
                run_command_process.start()

    LOG.info('\tTo: ')
    for tx_output in transaction['payload']['outputs']:
        for output_address in tx_output['addresses']:
            LOG.info('\t\t%s -> %s' % (output_address, tx_output['value_int']))
            if output_address in WATCHLIST and 'RECEIVE' in WATCHLIST[output_address]:

                event_found = True
                command = WATCHLIST[output_address]['RECEIVE']
                command = command.replace('#txid#', transaction['payload']['txid'])
                LOG.info('Executing command: %s' % command)
                run_command_process = RunCommandProcess(command=command)
                run_command_process.start()

    if EXIT_ON_EVENT is True and event_found is True:
        LOG.info('Event found, exiting now')
        ws.send('{"type":"new-transaction", "unsubscribe": true}')
        sys.exit()

    if EXIT_ON_TIMEOUT is not None and int(time.time()) >= EXIT_ON_TIMEOUT:
        LOG.info('Timeout occurred, exiting now')
        ws.send('{"type":"new-transaction", "unsubscribe": true}')
        sys.exit()


def on_error(ws, error):
    LOG.info('ERROR: %s' % error)  # use info level here instead of error level because for some reason an error is raised when the program exits


def on_close(ws):
    LOG.info("### websocket closed ###")


def on_open(ws):
    LOG.info("### websocket opened ###")
    LOG.info("Subscribing to new transactions")
    ws.send('{"type":"new-transaction"}')


if __name__ == "__main__":
    # Create main parser
    parser = argparse.ArgumentParser(description='Transaction listener')
    exclusive_group = parser.add_mutually_exclusive_group()
    exclusive_group.add_argument('-a', '--address', help='Watch a single address')
    exclusive_group.add_argument('-w', '--watchlist', help='the watchlist.json file containing the addresses and events to watch (default=watchlist.json)', default='watchlist.json')

    parser.add_argument('-s', '--send', help='Watch for an address to SEND a transaction (single address only)', action='store_true')
    parser.add_argument('-r', '--receive', help='Watch for an address to RECEIVE a transaction (single address only)', action='store_true')
    parser.add_argument('-c', '--command', help='The command to run when the watched address sends or receives a transaction (single address only)', type=str)
    parser.add_argument('-e', '--exit', help='Stop listening when a watched address sends or receives a transaction', action='store_true')
    parser.add_argument('-to', '--timeout', help='Stop listening after x seconds', type=int)
    parser.add_argument('-t', '--testnet', help='Use testnet instead of mainnet', action='store_true')
    parser.add_argument('-v', '--verbose', help='Run the listener in verbose mode ', action='store_true')

    args = parser.parse_args()

    if args.verbose is True:
        LOG.setLevel(logging.INFO)

    EXIT_ON_EVENT = args.exit

    if args.timeout is not None:
        EXIT_ON_TIMEOUT = int(time.time()) + args.timeout

    if args.address is not None:
        WATCHLIST = {args.address: {}}
        if args.send is True:
            WATCHLIST[args.address]['SEND'] = ''.join(args.command)

        if args.receive is True:
            WATCHLIST[args.address]['RECEIVE'] = ''.join(args.command)
    else:
        # Load the json file
        try:
            with open(args.watchlist, 'r') as input_file:
                try:
                    WATCHLIST = simplejson.load(input_file)
                except Exception as ex:
                    raise Exception('%s does not contain a valid dictionary: %s' % (args.watchlist, ex))
        except IOError:
            raise Exception('File %s does not exists' % args.watchlist)

    if args.testnet is True:
        url = "wss://testnet-ws.smartbit.com.au/v1/blockchain"
    else:
        url = "wss://ws.smartbit.com.au/v1/blockchain"

    LOG.info('Starting transaction listener')
    LOG.info('Watchlist:')
    LOG.info(WATCHLIST)

    # websocket.enableTrace(True)
    websocket = websocket.WebSocketApp(url=url,
                                       on_open=on_open,
                                       on_message=on_message,
                                       on_error=on_error,
                                       on_close=on_close)

    websocket.run_forever()
