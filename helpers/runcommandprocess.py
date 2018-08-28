#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import logging
from logging.handlers import RotatingFileHandler
import multiprocessing
from subprocess import Popen, PIPE

from helpers.platformhelpers import format_args

PROGRAM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# make the directory for logs if it doesn't exist
logs_dir = os.path.join(PROGRAM_DIR, 'logs')
if not os.path.isdir(logs_dir):
    os.makedirs(logs_dir)

PROCESS_LOG = logging.getLogger('process_log')

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
PROCESS_LOG.addHandler(stream_handler)

file_handler = RotatingFileHandler(os.path.join(PROGRAM_DIR, 'logs', 'process_log.txt'), maxBytes=10000000, backupCount=5)
file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
PROCESS_LOG.addHandler(file_handler)

PROCESS_LOG.setLevel(logging.DEBUG)


class RunCommandProcess(multiprocessing.Process):
    def __init__(self, command):
        multiprocessing.Process.__init__(self)

        self.command = command

    def run(self):
        process_id = multiprocessing.current_process().name
        PROCESS_LOG.info('%s | Spawned new process to run command: %s' % (process_id, self.command))
        PROCESS_LOG.info('%s | Process starting...' % process_id)

        command_process = Popen(format_args(self.command), stdout=PIPE, stderr=PIPE, shell=True, universal_newlines=True)

        for stdout_line in iter(command_process.stdout.readline, ""):
            PROCESS_LOG.info('%s | %s' % (process_id, stdout_line.strip()))

        PROCESS_LOG.info('%s | Process finished' % process_id)

