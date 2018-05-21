#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ipfsapi
import logging
import time

from helpers.configurationhelpers import get_ipfs_host, get_ipfs_port

IPFS_API = None
IPFS_CACHE = {}

# Check if IPFS node is running
try:
    IPFS_API = ipfsapi.connect(get_ipfs_host(), get_ipfs_port())
except Exception as ex:
    logging.getLogger('Spellbook').error('IPFS node is not running: %s' % ex)


def add_json(data):
    global IPFS_API

    try:
        multihash = IPFS_API.add_json(data)
    except Exception as e:
        logging.getLogger('Spellbook').error('Failed to store json data on IPFS: %s' % e)
        logging.getLogger('Spellbook').error('Sleeping 1 second before trying again...')
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
        logging.getLogger('Spellbook').error('Failed to retrieve json data from IPFS hash %s: %s' % (multihash, e))
        logging.getLogger('Spellbook').error('Sleeping 1 second before trying again...')
        time.sleep(1)
        json = IPFS_API.get_json(multihash)

    if multihash not in IPFS_CACHE:
        IPFS_CACHE[multihash] = json

    return json
