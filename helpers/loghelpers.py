#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import io
import sys
import glob
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

fmt = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
try:
    stream = sys.stdout
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")
    elif hasattr(stream, "buffer"):
        stream = io.TextIOWrapper(stream.buffer, encoding="utf-8", errors="replace", line_buffering=True)
    # else: leave as-is; handler will use whatever stream is (rare)
    stream_handler = logging.StreamHandler(stream)
except Exception:
    # Fallback if anything goes wrong
    stream_handler = logging.StreamHandler(sys.stdout)

stream_handler.setFormatter(fmt)
LOG.addHandler(stream_handler)

file_handler = RotatingFileHandler(os.path.join(logs_dir, 'spellbook.txt'), maxBytes=10000000, backupCount=backup_count, encoding='utf-8')  # Todo change to concurrent_log_handler.ConcurrentRotatingFileHandler with backupCount 5 after python3 conversion
file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
LOG.addHandler(file_handler)

LOG.setLevel(logging.DEBUG)

# Create a log file for the http requests to the REST API
REQUESTS_LOG = logging.getLogger('api_requests')

file_handler = RotatingFileHandler(os.path.join(logs_dir, 'requests.txt'), maxBytes=10000000, backupCount=backup_count, encoding='utf-8')  # Todo change to concurrent_log_handler.ConcurrentRotatingFileHandler with backupCount 5 after python3 conversion
file_handler.setFormatter(logging.Formatter('%(message)s'))
REQUESTS_LOG.addHandler(file_handler)

REQUESTS_LOG.setLevel(logging.DEBUG)


def get_logs(filter_string=''):
    """
    Get the combined log messages from all the logs files at a given time

    :param filter_string: A (partial) timestamp (e.g. 2017-07-14 13:) -> will return all log messages that start with 2017-07-14 13
    :return: A list containing all relevant log messages
    """
    # Get a list of all relevant log files
    log_files = glob.glob('logs/spellbook.txt*')

    combined_logs = []
    for log_file in log_files:
        with open(log_file, 'r', encoding='utf-8') as input_file:
            for line in input_file.readlines():
                if filter_string in line:
                    combined_logs.append(line.strip())

    # Sort the log messages by the timestamps
    ret = [line for line in sorted(combined_logs, key=lambda x: x)]

    return ret
