#!/usr/bin/python
# -*- coding: utf-8 -*-

import websocket
import simplejson
import argparse

WATCHLIST = {}


def on_message(ws, message):
    transaction = simplejson.loads(message)
    tx_hash = None
    print '\n\nNew transaction:'
    print 'From: '
    for input_address in transaction['x']['inputs']:
        if input_address['prev_out']['addr'] is not None:
            print input_address['prev_out']['addr']
            address = input_address['prev_out']['addr'][:2]
            if address in WATCHLIST and 'SEND' in WATCHLIST[address]:
                print 'Executing command: %s' % WATCHLIST[address]['SEND']
        else:
            tx_hash = transaction['x']['hash']

    print 'To: '
    for output_address in transaction['x']['out']:
        if output_address['addr'] is not None:
            print output_address['addr']
            address = output_address['addr'][:2]
            if address in WATCHLIST and 'RECEIVE' in WATCHLIST[address]:
                print 'Executing command: %s' % WATCHLIST[address]['RECEIVE']
        else:
            tx_hash = transaction['x']['hash']

    if tx_hash is not None:
        print "===========> check tx", tx_hash


def on_error(ws, error):
    print error


def on_close(ws):
    ws.send('{"op":"unconfirmed_unsub"}')
    print "### websocket closed ###"


def on_open(ws):
    print "### websocket opened ###"
    print "Subscribing to new transactions"
    ws.send('{"op":"unconfirmed_sub"}')


if __name__ == "__main__":
    # Create main parser
    parser = argparse.ArgumentParser(description='Transaction listener')
    parser.add_argument('-w', '--watchlist', help='the watchlist.json file containing the addresses and events to watch (default=watchlist.json', default='watchlist.json')

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

    # websocket.enableTrace(True)
    blockchain_info_websocket = websocket.WebSocketApp("wss://ws.blockchain.info/inv",
                                                       on_open=on_open,
                                                       on_message=on_message,
                                                       on_error=on_error,
                                                       on_close=on_close)

    blockchain_info_websocket.run_forever()
