#!/usr/bin/python
# -*- coding: utf-8 -*-

import websocket
import simplejson
import argparse
import sys

WATCHLIST = {}
EXIT_ON_EVENT = False


def on_message(ws, message):
    event_found = False
    transaction = simplejson.loads(message)
    if transaction['type'] != 'new-transaction':
        return

    print '\n\nNew transaction:', transaction['payload']['txid']
    print 'From: '
    for tx_input in transaction['payload']['inputs']:
        for input_address in tx_input['addresses']:
            print input_address, tx_input['value_int']
            if input_address in WATCHLIST and 'SEND' in WATCHLIST[input_address]:
                print 'Executing command: %s' % WATCHLIST[input_address]['SEND']
                event_found = True

    print 'To: '
    for tx_output in transaction['payload']['outputs']:
        for output_address in tx_output['addresses']:
            print output_address, tx_output['value_int']
            if output_address in WATCHLIST and 'RECEIVE' in WATCHLIST[output_address]:
                print 'Executing command: %s' % WATCHLIST[output_address]['RECEIVE']
                event_found = True

    if EXIT_ON_EVENT is True and event_found is True:
        ws.send('{"type":"new-transaction", "unsubscribe": true}')
        sys.exit()


def on_error(ws, error):
    print error


def on_close(ws):
    print "### websocket closed ###"


def on_open(ws):
    print "### websocket opened ###"
    print "Subscribing to new transactions"
    ws.send('{"type":"new-transaction"}')


if __name__ == "__main__":
    # Create main parser
    parser = argparse.ArgumentParser(description='Transaction listener')
    exclusive_group = parser.add_mutually_exclusive_group()
    exclusive_group.add_argument('-a', '--address', help='Watch a single address')
    exclusive_group.add_argument('-w', '--watchlist', help='the watchlist.json file containing the addresses and events to watch (default=watchlist.json)', default='watchlist.json')

    parser.add_argument('-s', '--send', help='Watch for an address to SEND a transaction', action='store_true')
    parser.add_argument('-r', '--receive', help='Watch for an address to RECEIVE a transaction', action='store_true')
    parser.add_argument('-c', '--command', help='The command to run when the watched address sends or receives a transaction', type=str)
    parser.add_argument('-e', '--exit', help='Stop listening when a watched address sends or receives a transaction', action='store_true')
    parser.add_argument('-t', '--testnet', help='Use testnet instead of mainnet', action='store_true')

    args = parser.parse_args()

    EXIT_ON_EVENT = args.exit

    if args.address is not None:
        WATCHLIST = {args.address: {}}
        if args.send is True:
            WATCHLIST[args.address]['SEND'] = args.command

        if args.receive is True:
            WATCHLIST[args.address]['RECEIVE'] = args.command
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

    # websocket.enableTrace(True)
    websocket = websocket.WebSocketApp(url=url,
                                       on_open=on_open,
                                       on_message=on_message,
                                       on_error=on_error,
                                       on_close=on_close)

    websocket.run_forever()
