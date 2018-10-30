#!/usr/bin/env python
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
from helpers.mysqlhelpers import mysql_cursor


PROGRAM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

LISTENER_LOG = logging.getLogger('transaction_listener_log')

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
LISTENER_LOG.addHandler(stream_handler)

# make the directory for logs if it doesn't exist
logs_dir = os.path.join(PROGRAM_DIR, 'logs')
if not os.path.isdir(logs_dir):
    os.makedirs(logs_dir)

file_handler = RotatingFileHandler(os.path.join(PROGRAM_DIR, 'logs', 'transaction_listener_log.txt'), maxBytes=10000000, backupCount=5)
file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
LISTENER_LOG.addHandler(file_handler)

LISTENER_LOG.setLevel(logging.WARNING)

WATCHLIST = {}
EXIT_ON_EVENT = False
EXIT_ON_TIMEOUT = None


def on_message(ws, message):
    event_found = False
    transaction = simplejson.loads(message)
    if transaction['type'] != 'new-transaction':
        return

    address_list = []
    LISTENER_LOG.info('New transaction: %s' % transaction['payload']['txid'])
    LISTENER_LOG.info('\tFrom: ')
    for tx_input in transaction['payload']['inputs']:
        for input_address in tx_input['addresses']:
            # add input_address if we are monitoring sending addresses
            if args.send is True and input_address is not '':
                address_list.append(input_address)

            LISTENER_LOG.info('\t\t%s -> %s' % (input_address, tx_input['value_int']))
            if input_address in WATCHLIST and 'SEND' in WATCHLIST[input_address]:

                event_found = True
                command = WATCHLIST[input_address]['SEND']
                command = command.replace('#txid#', transaction['payload']['txid'])
                LISTENER_LOG.info('Executing command: %s' % command)
                run_command_process = RunCommandProcess(command=command)
                run_command_process.start()

    LISTENER_LOG.info('\tTo: ')

    for tx_output in transaction['payload']['outputs']:
        for output_address in tx_output['addresses']:
            # Add output_address to list if we are monitoring receiving addresses
            if args.receive is True and output_address is not '':
                address_list.append(output_address)

            LISTENER_LOG.info('\t\t%s -> %s' % (output_address, tx_output['value_int']))
            if output_address in WATCHLIST and 'RECEIVE' in WATCHLIST[output_address]:

                event_found = True
                command = WATCHLIST[output_address]['RECEIVE']
                command = command.replace('#txid#', transaction['payload']['txid'])
                LISTENER_LOG.info('Executing command: %s' % command)
                run_command_process = RunCommandProcess(command=command)
                run_command_process.start()

    if DATABASE is not None:
        sql_query = """SELECT Address FROM Addresses 
                       WHERE Address IN (%s)""" % ", ".join(["'%s'" % output_address for output_address in address_list])

        CURSOR.execute(sql_query)
        result = CURSOR.fetchall()

        if len(result) > 0:
            LISTENER_LOG.info(result)

        for row in result:
            curl_command = COMMAND.replace('#address#', row[0])
            LISTENER_LOG.info('Executing command: %s' % curl_command)
            run_command_process = RunCommandProcess(command=curl_command)
            run_command_process.start()

    if EXIT_ON_EVENT is True and event_found is True:
        LISTENER_LOG.info('Event found, exiting now')
        ws.send('{"type":"new-transaction", "unsubscribe": true}')
        sys.exit()

    if EXIT_ON_TIMEOUT is not None and int(time.time()) >= EXIT_ON_TIMEOUT:
        LISTENER_LOG.info('Timeout occurred, exiting now')
        ws.send('{"type":"new-transaction", "unsubscribe": true}')
        sys.exit()


def on_error(ws, error):
    LISTENER_LOG.info('ERROR: %s' % error)  # use info level here instead of error level because for some reason an error is raised when the program exits


def on_close(ws):
    LISTENER_LOG.info("### websocket closed ###")


def on_open(ws):
    LISTENER_LOG.info("### websocket opened ###")
    LISTENER_LOG.info("Subscribing to new transactions")
    ws.send('{"type":"new-transaction"}')


if __name__ == "__main__":
    # Create main parser
    parser = argparse.ArgumentParser(description='Transaction listener')
    exclusive_group = parser.add_mutually_exclusive_group()
    exclusive_group.add_argument('-a', '--address', help='Watch a single address', type=str)
    exclusive_group.add_argument('-w', '--watchlist', help='the watchlist.json file containing the addresses and events to watch (default=watchlist.json)', type=str, default='watchlist.json')
    exclusive_group.add_argument('-d', '--database', help='A MySQL database containing the addresses to watch (must contain a table addresses with a column address)', type=str)

    parser.add_argument('-s', '--send', help='Watch for an address to SEND a transaction (single address only)', action='store_true')
    parser.add_argument('-r', '--receive', help='Watch for an address to RECEIVE a transaction (single address only)', action='store_true')
    parser.add_argument('-c', '--command', help='The command to run when the watched address sends or receives a transaction (single address only)', type=str)
    parser.add_argument('-e', '--exit', help='Stop listening when a watched address sends or receives a transaction', action='store_true')
    parser.add_argument('-to', '--timeout', help='Stop listening after x seconds', type=int)
    parser.add_argument('-t', '--testnet', help='Use testnet instead of mainnet', action='store_true')
    parser.add_argument('-v', '--verbose', help='Run the listener in verbose mode ', action='store_true')

    parser.add_argument('-i', '--host', help='Ip address of the MySQL server ', default='127.0.0.1', type=str)
    parser.add_argument('-p', '--port', help='Port of the MySQL server ', default=3306, type=int)
    parser.add_argument('-u', '--user', help='Username for the MySQL server ', type=str)
    parser.add_argument('-pw', '--password', help='Password for the MySQL server ', type=str)

    args = parser.parse_args()

    if args.verbose is True:
        LISTENER_LOG.setLevel(logging.INFO)

    LISTENER_LOG.info('Starting transaction listener')

    EXIT_ON_EVENT = args.exit

    if args.timeout is not None:
        EXIT_ON_TIMEOUT = int(time.time()) + args.timeout

    WATCHLIST = {}
    DATABASE = None
    COMMAND = None

    if args.database is not None:
        LISTENER_LOG.info('Database mode selected')
        DATABASE = args.database

        if args.user is None:
            LISTENER_LOG.error('Must specify a database user')
            sys.exit(1)

        if args.password is None:
            LISTENER_LOG.error('Must specify a database password')
            sys.exit(1)

        if args.command is None:
            LISTENER_LOG.error('No command given!')
            sys.exit(1)

        COMMAND = ''.join(args.command)
        LISTENER_LOG.info('Command to run when event is detected: %s' % COMMAND)

        if args.send is False and args.receive is False:
            LISTENER_LOG.error('Must specify at least on of the options --send or --receive')
            sys.exit(1)

        if args.send is True:
            LISTENER_LOG.info('Sending addresses are monitored')

        if args.receive is True:
            LISTENER_LOG.info('Receiving addresses are monitored')

    elif args.address is not None:
        LISTENER_LOG.info('Single address mode selected')

        WATCHLIST = {args.address: {}}
        if args.send is True:
            WATCHLIST[args.address]['SEND'] = ''.join(args.command)

        if args.receive is True:
            WATCHLIST[args.address]['RECEIVE'] = ''.join(args.command)

        LISTENER_LOG.info('Watchlist:')
        LISTENER_LOG.info(WATCHLIST)

    else:
        LISTENER_LOG.info('Watchlist mode selected')

        # Load the json file
        try:
            with open(args.watchlist, 'r') as input_file:
                try:
                    WATCHLIST = simplejson.load(input_file)
                except Exception as ex:
                    raise Exception('%s does not contain a valid dictionary: %s' % (args.watchlist, ex))
        except IOError:
            raise Exception('File %s does not exists' % args.watchlist)

        LISTENER_LOG.info('Watchlist:')
        LISTENER_LOG.info(WATCHLIST)

    # Set the url for testnet or mainnet
    if args.testnet is True:
        url = "wss://testnet-ws.smartbit.com.au/v1/blockchain"
    else:
        url = "wss://ws.smartbit.com.au/v1/blockchain"

    # Create the websocket
    # websocket.enableTrace(True)
    websocket = websocket.WebSocketApp(url=url,
                                       on_open=on_open,
                                       on_message=on_message,
                                       on_error=on_error,
                                       on_close=on_close)

    # when running in database mode, a mysql cursor must be available while the listener is running
    if DATABASE is not None:
        with mysql_cursor(user=args.user,
                          password=args.password,
                          database=args.database,
                          host=args.host,
                          port=args.port) as CURSOR:
            websocket.run_forever()
    else:
        websocket.run_forever()
