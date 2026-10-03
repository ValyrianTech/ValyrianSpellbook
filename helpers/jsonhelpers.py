#!/usr/bin/env python
"""Helper functions for saving and loading JSON files with error handling."""

import os
import tempfile
import time

import simplejson

from helpers.loghelpers import LOG


def save_to_json_file(filename, data):
    """
    Save data to a json file
    :param filename: The filename of the json file
    :param data: A dict containing the data to save (must be json-encodable)
    """

    # Make sure the destination directory exists
    if not os.path.isdir(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=os.path.dirname(filename) or '.', delete=False) as tmp_file:
            tmp_path = tmp_file.name
            simplejson.dump(data, tmp_file, indent=4, sort_keys=True)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
        os.replace(tmp_path, filename)
    except (ValueError, KeyError, TypeError, OSError) as ex:
        LOG.error(f'Failed to save data to json file {filename}: {ex}')
        if tmp_path is not None and os.path.exists(tmp_path):
            os.remove(tmp_path)


def load_from_json_file(filename):
    """
    Load data from a json file

    :return: a dict containing the data from the json file
    """
    data = None
    try:
        with open(filename, 'r') as input_file:
            data = simplejson.load(input_file)
    except (ValueError, KeyError, TypeError, OSError) as ex:
        LOG.error(f'Failed to load {filename}: {ex}')
        LOG.error('Sleeping for 1 second before retrying')
        time.sleep(1)
        LOG.error(f'Retrying to load {filename}')
        try:
            with open(filename, 'r') as input_file:
                data = simplejson.load(input_file)
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Failed to load twice {filename}: {ex}')

    return data
