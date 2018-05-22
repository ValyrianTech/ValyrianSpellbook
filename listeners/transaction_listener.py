#!/usr/bin/python
# -*- coding: utf-8 -*-

import websocket
import simplejson
import argparse

WATCHLIST = {}


def on_message(ws, message):
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

    print 'To: '
    for tx_output in transaction['payload']['outputs']:
        for output_address in tx_output['addresses']:
            print output_address, tx_output['value_int']
            if output_address in WATCHLIST and 'RECEIVE' in WATCHLIST[output_address]:
                print 'Executing command: %s' % WATCHLIST[output_address]['RECEIVE']


def on_error(ws, error):
    print error


def on_close(ws):
    ws.send('{"type":"new-transaction", "unsubscribe": true}')
    print "### websocket closed ###"


def on_open(ws):
    print "### websocket opened ###"
    print "Subscribing to new transactions"
    ws.send('{"type":"new-transaction"}')


if __name__ == "__main__":
    # Create main parser
    parser = argparse.ArgumentParser(description='Transaction listener')
    parser.add_argument('-w', '--watchlist', help='the watchlist.json file containing the addresses and events to watch (default=watchlist.json', default='watchlist.json')
    parser.add_argument('-t', '--testnet', help='Use testnet instead of mainnet', action='store_true')

    args = parser.parse_args()

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
