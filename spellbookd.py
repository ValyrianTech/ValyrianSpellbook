#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import argparse
import daemon
from spellbook import Spellbook


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Bitcoin Spellbook')
    parser.add_argument('--daemon', action='store_true', help='run as daemon')
    cli_args = parser.parse_args()

    print("Starting Bitcoin Spellbook")

    if cli_args.daemon:
        pid_file = open("spellbook.pid", "w")
        pid_file.write(str(os.getpid()))
        pid_file.close()

        with daemon.DaemonContext(stderr=open("spellbook-err.txt", "w"),
                                  working_directory=os.path.dirname(__file__)):
            Spellbook()

    else:
        Spellbook()
