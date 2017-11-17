#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from bottle import Bottle, request, response
from datetime import datetime
from functools import wraps
import traceback

from data.data import get_explorers, get_explorer_config, save_explorer, delete_explorer
from data.data import latest_block, block_by_height, block_by_hash, prime_input_address
from data.data import transactions, balance, utxos
from authentication import initialize_api_keys_file
from decorators import authentication_required, use_explorer, output_json

from inputs.inputs import get_sil, get_profile
from linker.linker import get_lal, get_lbl, get_lrl, get_lsl


class SpellbookRESTAPI(Bottle):
    def __init__(self):
        super(SpellbookRESTAPI, self).__init__()

        # Initialize variables
        self.host = 'localhost'
        self.port = 8080

        # make the directory for logs if it doesn't exist
        logs_dir = os.path.join('logs')
        if not os.path.isdir(logs_dir):
            os.makedirs(logs_dir)

        # Initialize the log
        self.log = self.initialize_log(logs_dir)

        # Initialize a separate log for the http requests to the REST API
        self.requests_log = self.initialize_requests_log(logs_dir)

        # Log the requests to the REST API in a separate file by installing a custom LoggingPlugin
        self.install(self.log_to_logger)

        # Make sure that an api_keys.json file is present, the first time the server is started
        # a new random api key and secret pair will be generated
        if not os.path.isfile('api_keys.json'):
            self.log.info('Generating new API keys')
            initialize_api_keys_file()

        self.log.info('Starting Bitcoin Spellbook')

        # Initialize the routes for the REST API
        # Routes for managing blockexplorers
        self.route('/spellbook/explorers', method='GET', callback=self.get_explorers)
        self.route('/spellbook/explorers/<explorer_id:re:[a-zA-Z0-9_\-.]+>', method='POST', callback=self.save_explorer)
        self.route('/spellbook/explorers/<explorer_id:re:[a-zA-Z0-9_\-.]+>', method='GET', callback=self.get_explorer_config)
        self.route('/spellbook/explorers/<explorer_id:re:[a-zA-Z0-9_\-.]+>', method='DELETE', callback=self.delete_explorer)

        # Routes for retrieving data from the blockchain
        self.route('/spellbook/blocks/latest', method='GET', callback=self.get_latest_block)
        self.route('/spellbook/blocks/<height:int>', method='GET', callback=self.get_block_by_height)
        self.route('/spellbook/blocks/<block_hash:re:[a-f0-9]+>', method='GET', callback=self.get_block_by_hash)

        self.route('/spellbook/transactions/<txid:re:[a-f0-9]+>/prime_input', method='GET', callback=self.get_prime_input_address)
        self.route('/spellbook/addresses/<address:re:[a-km-zA-HJ-NP-Z1-9]+>/transactions', method='GET', callback=self.get_transactions)
        self.route('/spellbook/addresses/<address:re:[a-km-zA-HJ-NP-Z1-9]+>/balance', method='GET', callback=self.get_balance)
        self.route('/spellbook/addresses/<address:re:[a-km-zA-HJ-NP-Z1-9]+>/utxos', method='GET', callback=self.get_utxos)

        # Routes for Simplified Inputs List (SIL)
        self.route('/spellbook/addresses/<address:re:[a-km-zA-HJ-NP-Z1-9]+>/SIL', method='GET', callback=self.get_sil)

        # Routes for Profile
        self.route('/spellbook/addresses/<address:re:[a-km-zA-HJ-NP-Z1-9]+>/profile', method='GET', callback=self.get_profile)

        # Routes for Linked Lists
        self.route('/spellbook/addresses/<address:re:[a-km-zA-HJ-NP-Z1-9]+>/LAL', method='GET', callback=self.get_lal)
        self.route('/spellbook/addresses/<address:re:[a-km-zA-HJ-NP-Z1-9]+>/LBL', method='GET', callback=self.get_lbl)
        self.route('/spellbook/addresses/<address:re:[a-km-zA-HJ-NP-Z1-9]+>/LRL', method='GET', callback=self.get_lrl)
        self.route('/spellbook/addresses/<address:re:[a-km-zA-HJ-NP-Z1-9]+>/LSL', method='GET', callback=self.get_lsl)

        # start the webserver for the REST API
        self.run(host=self.host, port=self.port)

    @staticmethod
    def initialize_log(logs_dir):
        # Create a log file for the Core daemon
        logger = logging.getLogger('Spellbook')

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
        logger.addHandler(stream_handler)

        file_handler = RotatingFileHandler(os.path.join(logs_dir, 'spellbook.txt'), maxBytes=10000000, backupCount=5)
        file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
        logger.addHandler(file_handler)

        logger.setLevel(logging.DEBUG)

        return logger

    @staticmethod
    def initialize_requests_log(logs_dir):
        # Create a log file for the http requests to the REST API
        logger = logging.getLogger('api_requests')

        file_handler = RotatingFileHandler(os.path.join(logs_dir, 'requests.txt'), maxBytes=10000000, backupCount=5)
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(file_handler)

        logger.setLevel(logging.DEBUG)

        return logger

    def log_to_logger(self, fn):
        @wraps(fn)
        def _log_to_logger(*args, **kwargs):
            request_time = datetime.now()
            actual_response = response
            try:
                actual_response = fn(*args, **kwargs)
            except Exception as ex:
                response_status = '500 ' + str(ex)
                self.log.error('%s caused an exception: %s' % (request.url, ex))
                traceback.print_exc()
            else:
                response_status = response.status

            self.requests_log.info('%s | %s | %s | %s | %s' % (request_time,
                                                               request.remote_addr,
                                                               request.method,
                                                               request.url,
                                                               response_status))
            return actual_response
        return _log_to_logger

    @staticmethod
    @output_json
    def get_explorers():
        explorers = get_explorers()
        if explorers is not None:
            return explorers
        else:
            return {'error': 'Unable to retrieve explorer_ids'}

    @staticmethod
    @authentication_required
    def save_explorer(explorer_id):
        save_explorer(explorer_id, request.json)

    @staticmethod
    @output_json
    @authentication_required
    def get_explorer_config(explorer_id):
        explorer_config = get_explorer_config(explorer_id)
        if explorer_config is not None:
            return explorer_config
        else:
            return {'error': 'No explorer configured with id: %s' % explorer_id}

    @staticmethod
    @authentication_required
    def delete_explorer(explorer_id):
        delete_explorer(explorer_id)

    @staticmethod
    @output_json
    @use_explorer
    def get_latest_block():
        return latest_block()

    @staticmethod
    @output_json
    @use_explorer
    def get_block_by_height(height):
        return block_by_height(height)

    @staticmethod
    @output_json
    @use_explorer
    def get_block_by_hash(block_hash):
        return block_by_hash(block_hash)

    @staticmethod
    @output_json
    @use_explorer
    def get_prime_input_address(txid):
        return prime_input_address(txid)

    @staticmethod
    @output_json
    @use_explorer
    def get_transactions(address):
        return transactions(address)

    @staticmethod
    @output_json
    @use_explorer
    def get_balance(address):
        return balance(address)

    @staticmethod
    @output_json
    @use_explorer
    def get_utxos(address):
        return utxos(address, int(request.query.confirmations))

    @staticmethod
    @output_json
    @use_explorer
    def get_sil(address):
        block_height = int(request.json['block_height'])
        return get_sil(address, block_height)

    @staticmethod
    @output_json
    @use_explorer
    def get_profile(address):
        block_height = int(request.json['block_height'])
        return get_profile(address, block_height)

    @staticmethod
    @output_json
    @use_explorer
    def get_lal(address):
        block_height = int(request.json['block_height'])
        xpub = request.json['xpub']
        return get_lal(address, xpub, block_height)

    @staticmethod
    @output_json
    @use_explorer
    def get_lbl(address):
        block_height = int(request.json['block_height'])
        xpub = request.json['xpub']
        return get_lbl(address, xpub, block_height)

    @staticmethod
    @output_json
    @use_explorer
    def get_lrl(address):
        block_height = int(request.json['block_height'])
        xpub = request.json['xpub']
        return get_lrl(address, xpub, block_height)

    @staticmethod
    @output_json
    @use_explorer
    def get_lsl(address):
        block_height = int(request.json['block_height'])
        xpub = request.json['xpub']
        return get_lsl(address, xpub, block_height)


if __name__ == "__main__":
    SpellbookRESTAPI()
