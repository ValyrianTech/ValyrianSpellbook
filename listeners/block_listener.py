#!/usr/bin/env python
# -*- coding: utf-8 -*-

import websocket
import simplejson


def on_message(ws, message):
    block = simplejson.loads(message)
    print '\n\nNew block:'
    print 'height:', block['x']['height']
    print 'hash:', block['x']['hash']
    print 'nTx:', block['x']['nTx']
    print 'time:', block['x']['time']


def on_error(ws, error):
    print error


def on_close(ws):
    print "### websocket closed ###"


def on_open(ws):
    print "### websocket opened ###"
    print "Subscribing to new blocks"
    ws.send('{"op":"blocks_sub"}')


if __name__ == "__main__":
    # websocket.enableTrace(True)
    blockchain_info_websocket = websocket.WebSocketApp("wss://ws.blockchain.info/inv",
                                                       on_open=on_open,
                                                       on_message=on_message,
                                                       on_error=on_error,
                                                       on_close=on_close)

    blockchain_info_websocket.run_forever()
