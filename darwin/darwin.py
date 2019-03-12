#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import sys

PROGRAM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, PROGRAM_DIR)

from evolver import Evolver
from helpers.jsonhelpers import load_from_json_file


if __name__ == "__main__":
    # Create main parser
    parser = argparse.ArgumentParser(description='Evolver command line interface', formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('config', help='name of the configuration file to use')

    # Parse the command line arguments
    args = parser.parse_args()

    evolver = Evolver()
    # evolver.save_config(filename=args.config)

    # Read the configuration
    config = load_from_json_file(filename=args.config)
    evolver.load_config(config)
    evolver.print_settings()

    evolver.start()
