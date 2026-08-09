#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Block listener that monitors new blocks on the blockchain."""

import websocket
import simplejson


def on_message(ws, message):
    """Process incoming websocket messages and print new block details."""
    block = simplejson.loads(message)
    print('\n\nNew block:')
    print('height:', block['x']['height'])
    print('hash:', block['x']['hash'])
    print('nTx:', block['x']['nTx'])
    print('time:', block['x']['time'])


def on_error(ws, error):
    """Handle websocket errors by printing the error."""
    print(error)


def on_close(ws):
    """Handle websocket close events."""
    print("### websocket closed ###")


def on_open(ws):
    """Subscribe to new block notifications on websocket open."""
    print("### websocket opened ###")
    print("Subscribing to new blocks")
    ws.send('{"op":"blocks_sub"}')


if __name__ == "__main__":
    # websocket.enableTrace(True)
    blockchain_info_websocket = websocket.WebSocketApp("wss://ws.blockchain.info/inv",
                                                       on_open=on_open,
                                                       on_message=on_message,
                                                       on_error=on_error,
                                                       on_close=on_close)

    blockchain_info_websocket.run_forever()
