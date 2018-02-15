#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import simplejson


def save_to_json_file(filename, data):
    """
    Save data to a json file
    :param filename: The filename of the json file
    :param data: A dict containing the data to save (must be json-encodable)
    """
    try:
        with open(filename, 'w') as output_file:
            simplejson.dump(data, output_file, indent=4, sort_keys=True)
    except Exception as ex:
        logging.getLogger('Spellbook').error('Failed to save data to json file %s: %s' % (filename, ex))


def load_from_json_file(filename):
    """
    Load data from a json file

    :return: a dict containing the data from the json file
    """
    data = None
    # Load the json file
    with open(filename, 'r') as input_file:
        try:
            data = simplejson.load(input_file)
        except Exception as ex:
            logging.getLogger('Spellbook').error('Failed to load %s: %s' % (filename, ex))

    return data
