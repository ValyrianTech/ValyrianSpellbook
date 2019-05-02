#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import platform
import logging
from logging.handlers import RotatingFileHandler

PROGRAM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

backup_count = 5 if platform.system() == 'Linux' else 0

# make the directory for logs if it doesn't exist
logs_dir = os.path.join(PROGRAM_DIR, 'logs')
if not os.path.isdir(logs_dir):
    os.makedirs(logs_dir)

LOG = logging.getLogger('Spellbook')

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
LOG.addHandler(stream_handler)

file_handler = RotatingFileHandler(os.path.join(logs_dir, 'spellbook.txt'), maxBytes=10000000, backupCount=backup_count)  # Todo change to concurrent_log_handler.ConcurrentRotatingFileHandler with backupCount 5 after python3 conversion
file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
LOG.addHandler(file_handler)

LOG.setLevel(logging.DEBUG)

# Create a log file for the http requests to the REST API
REQUESTS_LOG = logging.getLogger('api_requests')

file_handler = RotatingFileHandler(os.path.join(logs_dir, 'requests.txt'), maxBytes=10000000, backupCount=backup_count)  # Todo change to concurrent_log_handler.ConcurrentRotatingFileHandler with backupCount 5 after python3 conversion
file_handler.setFormatter(logging.Formatter('%(message)s'))
REQUESTS_LOG.addHandler(file_handler)

REQUESTS_LOG.setLevel(logging.DEBUG)
