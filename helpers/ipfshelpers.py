#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ipfsapi
import time

from helpers.loghelpers import LOG
from helpers.configurationhelpers import get_ipfs_host, get_ipfs_port

IPFS_API = None
IPFS_CACHE = {}

# Check if IPFS node is running
try:
    IPFS_API = ipfsapi.connect(get_ipfs_host(), get_ipfs_port())
except Exception as ex:
    LOG.error('IPFS node is not running: %s' % ex)


def add_json(data):
    global IPFS_API

    try:
        multihash = IPFS_API.add_json(data)
    except Exception as e:
        LOG.error('Failed to store json data on IPFS: %s' % e)
        LOG.error('Sleeping 1 second before trying again...')
        time.sleep(1)
        multihash = IPFS_API.add_json(data)

    return multihash


def get_json(multihash):
    global IPFS_API, IPFS_CACHE

    if multihash in IPFS_CACHE:
        return IPFS_CACHE[multihash]

    try:
        json = IPFS_API.get_json(multihash)
    except Exception as e:
        LOG.error('Failed to retrieve json data from IPFS hash %s: %s' % (multihash, e))
        LOG.error('Sleeping 1 second before trying again...')
        time.sleep(1)
        json = IPFS_API.get_json(multihash)

    if multihash not in IPFS_CACHE:
        IPFS_CACHE[multihash] = json

    return json


class IPFSDict(object):
    def __init__(self, multihash=None):
        self.multihash = multihash

        if self.multihash is not None:
            self.load(multihash=multihash)

    def save(self):
        data = {key: value for key, value in self.__dict__.items() if key != 'multihash'}

        return add_json(data=data)

    def load(self, multihash):
        self.multihash = multihash

        if not isinstance(multihash, (str, unicode)):
            LOG.error('Can not retrieve IPFS data: multihash must be a string or unicode, got %s instead' % type(multihash))
            return

        try:
            data = get_json(multihash=multihash)
        except Exception as e:
            LOG.error('Can not retrieve IPFS data of %s: %s' % (multihash, e))
            return

        if not isinstance(data, dict):
            LOG.error('IPFS multihash %s does not contain a dict!' % multihash)
            return

        if self.is_valid(data=data):
            for key, value in data.items():
                if key != 'multihash':
                    self.__setattr__(key, value)

    def is_valid(self, data):
        # Override this method to add validation for the data such as required keys and the contents of the values
        return True
