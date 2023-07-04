#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ipfs_dict_chain.IPFS import connect
from ipfs_dict_chain.IPFSDictChain import IPFSDictChain
from ipfs_dict_chain.IPFSDict import IPFSDict

from helpers.loghelpers import LOG
from helpers.configurationhelpers import get_ipfs_api_host, get_ipfs_api_port, get_enable_ipfs


def check_ipfs():
    try:
        connect(host=get_ipfs_api_host(), port=get_ipfs_api_port())
        return True
    except Exception as ex:
        LOG.error('IPFS node is not running: %s' % ex)
        return False


def add_json(data):
    ipfs_dict = IPFSDict()
    for key, value in data.items():
        ipfs_dict[key] = value

    return ipfs_dict.save()


def get_json(cid):
    ipfs_dict = IPFSDict(cid=cid)
    for key, value in ipfs_dict.items():
        ipfs_dict[key] = value

    return ipfs_dict


# Todo fix this, only used in Notarize
def add_file(filename):
    global IPFS_API

    try:
        ipfs_info = IPFS_API.add(filename)
    except Exception as e:
        LOG.error('Unable to store file on IPFS: %s' % e)
        raise Exception('IPFS failure')

    return ipfs_info['Hash'], ipfs_info['Name'], ipfs_info['Size']


class FileMetaData(IPFSDictChain):
    def __init__(self, cid=None):
        self.file_name = None
        self.file_ipfs_hash = None
        self.file_sha256_hash = None
        self.file_size = None
        self.txid = None
        self.publisher_name = None
        self.publisher_address = None
        self.publisher_signature = None
        self.signed_message = None

        super(FileMetaData, self).__init__(cid=cid)


if get_enable_ipfs() is True:
    check_ipfs()
