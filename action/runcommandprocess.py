#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import logging
from logging.handlers import RotatingFileHandler
import multiprocessing
from subprocess import Popen, PIPE

# make the directory for logs if it doesn't exist
logs_dir = os.path.join('logs')
if not os.path.isdir(logs_dir):
    os.makedirs(logs_dir)

LOG = logging.getLogger('process_log')

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
LOG.addHandler(stream_handler)

file_handler = RotatingFileHandler(os.path.join('logs', 'process_log.txt'), maxBytes=10000000, backupCount=5)
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
        LOG.info('%s | Running command...' % process_id)

        command_process = Popen(self.command, stdout=PIPE, stderr=PIPE, shell=True)
        output, error = command_process.communicate()

        LOG.info('%s | Command finished' % process_id)
        stripped_output = output.strip()
        LOG.info('%s | Command output:' % process_id)
        for line in stripped_output.split('\n'):
            LOG.info('%s | %s' % (process_id, line.strip()))

        stripped_error = error.strip()
        if len(stripped_error):
            LOG.error('%s | Command error:' % process_id)
            for line in stripped_error.split('\n'):
                LOG.error('%s | %s' % (process_id, line.strip()))

        LOG.info('%s | process finished' % process_id)

