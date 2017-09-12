#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from bottle import Bottle, request, response
from datetime import datetime
from functools import wraps
import simplejson


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

        self.log.info('Starting Bitcoin Spellbook')

        # Initialize the routes for the REST API
        # Routes for managing blockexplorers
        self.route('/spellbook/explorers', method='GET', callback=self.get_explorers)
        self.route('/spellbook/explorers', method='POST', callback=self.save_explorer)
        self.route('/spellbook/explorers', method='DELETE', callback=self.delete_explorer)

        # Routes for retrieving data from the blockchain
        self.route('/spellbook/block', method='GET', callback=self.get_block)

        # start the webserver for the REST API
        self.run(host=self.host, port=self.port)

    @staticmethod
    def initialize_log(logs_dir):
        # Create a log file for the Core daemon
        logger = logging.getLogger('Bitcoin Spellbook')

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
            actual_response = fn(*args, **kwargs)
            self.requests_log.info('%s | %s | %s | %s | %s' % (request_time,
                                                               request.remote_addr,
                                                               request.method,
                                                               request.url,
                                                               response.status))
            return actual_response
        return _log_to_logger

    def get_explorers(self):
        return simplejson.dumps('get explorers')

    def save_explorer(self):
        return simplejson.dumps('save explorer')

    def delete_explorer(self):
        return simplejson.dumps('delete explorer')

    def get_block(self):
        return simplejson.dumps('block data')


if __name__ == "__main__":
    SpellbookRESTAPI()

