#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import logging
from logging.handlers import RotatingFileHandler
import multiprocessing
from subprocess import Popen, PIPE

PROGRAM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# make the directory for logs if it doesn't exist
logs_dir = os.path.join(PROGRAM_DIR, 'logs')
if not os.path.isdir(logs_dir):
    os.makedirs(logs_dir)

# Todo check why log messages happen multiple times if multiple processes are spawned, maybe store the logs in the app data dir

LOG = logging.getLogger('process_log')

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
LOG.addHandler(stream_handler)

file_handler = RotatingFileHandler(os.path.join(PROGRAM_DIR, 'logs', 'process_log.txt'), maxBytes=10000000, backupCount=5)
file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
LOG.addHandler(file_handler)

LOG.setLevel(logging.DEBUG)


class RunCommandProcess(multiprocessing.Process):
    def __init__(self, command):
        multiprocessing.Process.__init__(self)

        self.command = command

    def run(self):
        process_id = multiprocessing.current_process().name
        LOG.info('%s | Spawned new process to run command: %s' % (process_id, self.command))
        LOG.info('%s | Process starting...' % process_id)

        command_process = Popen(self.command, stdout=PIPE, stderr=PIPE, shell=True, universal_newlines=True)

        for stdout_line in iter(command_process.stdout.readline, ""):
            LOG.info('%s | %s' % (process_id, stdout_line.strip()))

        LOG.info('%s | Process finished' % process_id)

