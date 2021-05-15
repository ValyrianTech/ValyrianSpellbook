#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import ipfshttpclient  # needs python 3.5+ , earlier version are no longer supported
import time
import shutil
import zipfile

from helpers.loghelpers import LOG
from helpers.configurationhelpers import get_ipfs_api_host, get_ipfs_api_port, get_enable_ipfs
from helpers.jsonhelpers import save_to_json_file

IPFS_API = None
IPFS_CACHE = {}


def connect_to_ipfs():
    global IPFS_API

    # Check if IPFS node is running
    multi_address = '/ip4/{host}/tcp/{port}/http'.format(host=get_ipfs_api_host(), port=get_ipfs_api_port())
    LOG.info('Trying to connect with IPFS on %s' % multi_address)
    try:
        IPFS_API = ipfshttpclient.connect(multi_address)
        LOG.info('Connected with IPFS')
    except Exception as ex:
        LOG.error('IPFS node is not running: %s' % ex)


def check_ipfs():
    if IPFS_API is not None:
        return True
    else:
        LOG.warn('Not connected to IPFS, trying to reconnect')
        connect_to_ipfs()

    return IPFS_API is not None


class CID(object):
    def __init__(self, value):
        if not isinstance(value, str):
            raise Exception('Value of a cid must be a string, got %s instead' % (type(value)))

        self.value = value if value.startswith('/ipfs/') else '/ipfs/%s' % value

    def __str__(self):
        return self.value

    def short(self):
        return self.value[6:]

    def long(self):
        return self.value


def add_json(data):
    global IPFS_API

    try:
        cid = IPFS_API.add_json(data)
    except Exception as e:
        LOG.error('Failed to store json data on IPFS: %s' % e)
        LOG.error('Data: %s' % data)
        LOG.error('Sleeping 1 second before trying again...')
        time.sleep(1)
        try:
            cid = IPFS_API.add_json(data)
        except Exception as e:
            raise Exception('Failed to store json data on IPFS: %s' % e)

    return CID(cid).__str__()


def get_json(cid):
    global IPFS_API, IPFS_CACHE

    if cid in IPFS_CACHE:
        return IPFS_CACHE[cid]

    json = None
    try:
        json = IPFS_API.get_json(cid, timeout=2)
    except Exception as e:
        LOG.error('Failed to retrieve json data from IPFS hash %s: %s' % (cid, e))

    if cid not in IPFS_CACHE:
        IPFS_CACHE[cid] = json

    return json


def add_str(string):
    global IPFS_API

    try:
        cid = IPFS_API.add_str(string=string)
    except Exception as e:
        LOG.error('Unable to store string on IPFS: %s' % e)
        raise Exception('IPFS failure')

    return CID(cid).__str__()


def get_str(cid):
    global IPFS_API, IPFS_CACHE

    if cid in IPFS_CACHE:
        return IPFS_CACHE[cid]

    string = None
    try:
        string = IPFS_API.cat(cid=cid, timeout=1)
    except Exception as e:
        LOG.error('Unable to retrieve string from IPFS with cid %s: %s' % (cid, e))

    if cid not in IPFS_CACHE:
        IPFS_CACHE[cid] = string

    return string.decode('utf-8')


def add_file(filename):
    global IPFS_API

    try:
        ipfs_info = IPFS_API.add(filename)
    except Exception as e:
        LOG.error('Unable to store file on IPFS: %s' % e)
        raise Exception('IPFS failure')

    return ipfs_info['Hash'], ipfs_info['Name'], ipfs_info['Size']


def add_zipped_dir(directory_path, name):
    """
    Zip a directory and add the zip file to IPFS

    :param directory_path: The path to the directory
    :param name: The name of the zip file
    :return: A dict containing the ipfs info of the zip file (Hash, Name and Size)
    """
    if not os.path.isdir(directory_path):
        LOG.error('Can not add directory to IPFS: %s not found!' % directory_path)
        return

    shutil.make_archive(name, format='zip', root_dir=directory_path)
    zip_file_name = '%s.zip' % name
    ipfs_info = IPFS_API.add(zip_file_name)
    LOG.info('Compressed directory into zip file and added to IPFS: %s' % ipfs_info)

    # Clean up the temporary zip file
    if os.path.isfile(zip_file_name):
        os.remove(zip_file_name)

    return ipfs_info


def get_zipped_dir(cid, target_dir):
    """
    Get a zipped directory from IPFS and extract it into the target directory

    :param cid: The IPFS cid of the directory in zipped format
    :param target_dir: The target directory where the contents of the zipfile will be extracted
    """
    IPFS_API.get(cid)

    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)

    try:
        with zipfile.ZipFile(cid, "r") as z:
            z.extractall(target_dir)
    except Exception as e:
        LOG.error('Can not extract zipped dir %s: %s' % (cid, e))
    finally:
        # Clean up the temporary zip file
        if os.path.isfile(cid):
            os.remove(cid)


class IPFSDict(object):
    """
    This class is meant to be a base class for saving and loading dictionaries on IPFS

    child classes must only initialize the member variables (names must be identical to the keys in the dict)
    before calling the __init__() of the base class

    optionally override the is_valid() method to add validation for the dict
    """
    def __init__(self, cid=None):
        """
        Constructor of the IPFSDict class

        :param cid: An IPFS cid
        """
        self._cid = CID(cid).__str__() if cid is not None else None

        if self._cid is not None:
            self.load(cid=self._cid)

    def get(self):
        """
        Get the contents of the dictionary

        :return: A dict
        """
        return {key: value for key, value in self.__dict__.items() if key[0] != '_'}

    def cid(self):
        return self._cid

    def save(self):
        """
        Save the dictionary on IPFS

        :return: The IPFS cid of the dictionary
        """
        self._cid = add_json(data=self.get())
        return self._cid

    def save_as_json(self, filename):
        """
        Save the dictionary as a json file and also include the cid of the data itself in the json file

        :param filename: The filename of the json file
        """
        self.save()
        data = self.get()
        data['cid'] = self._cid

        save_to_json_file(filename=filename, data=data)
        return self._cid

    def load(self, cid):
        """
        Load a dictionary from IPFS

        :param cid: An IPFS cid
        """
        if not isinstance(cid, str):
            LOG.error('Can not retrieve IPFS data: cid must be a string or unicode, got %s instead' % type(cid))
            return

        try:
            data = get_json(cid=cid)
        except Exception as e:
            LOG.error('Can not retrieve IPFS data of %s: %s' % (cid, e))
            return

        if not isinstance(data, dict):
            LOG.error('IPFS cid %s does not contain a dict!' % cid)
            return

        self._cid = CID(cid).__str__()

        if self.is_valid(data=data):
            for key, value in data.items():
                if key != '_cid':
                    self.__setattr__(key, value)
        else:
            raise Exception('Invalid cid for IPFSDict object')

    def is_valid(self, data):
        """
        Validate the contents of the dictionary

        Override this method to add validation for the data such as required keys and the contents of the values

        :param data: A Dictionary object
        :return: True or False
        """
        required_keys = [key for key in self.__dict__.keys() if key[0] != '_']
        for required_key in required_keys:
            if required_key not in data:
                LOG.error('%s is not a valid IPFSDict hash: it does not contain the key "%s"' % (self._cid, required_key))
                return False

        return True


class IPFSDictChain(IPFSDict):
    """
    An IPFSDict object that also keeps track of changes made to the contents
    """
    def __init__(self, cid=None):
        """
        Constructor of the IPFSDictChain class

        :param cid: An IPFS cid (optional)
        """
        self.previous_cid = None

        super(IPFSDictChain, self).__init__(cid=cid)

    def save(self):
        """
        Save the dictionary on IPFS with a reference to the previous state

        :return: An IPFS cid of the dict
        """
        self.previous_cid = self._cid
        self._cid = add_json(data=self.get())
        return self._cid

    def changes(self):
        """
        Get the changes between this state and the previous state

        :return: A dict containing the changed values
        """
        changes = {}
        if self.previous_cid is not None:
            old_data = IPFSDictChain(cid=self.previous_cid).get()

            for key in old_data:
                if old_data[key] != self.__getattribute__(key):
                    changes[key] = {'old': old_data[key], 'new': self.__getattribute__(key)}

            for key in self.get():
                if key not in old_data:
                    changes[key] = {'new': self.__getattribute__(key)}

        else:
            for key in self.get():
                changes[key] = {'new': self.__getattribute__(key)}

        return changes

    def change_log(self, max_depth=None):
        """
        Get the change log of the IPFSDictChain

        :param max_depth: An integer indicating how deep to follow the chain (optional)
        :return: A list containing the changes between each item on the chain
        """
        depth = 0
        change_log = [self.changes()]

        previous_cid = self.previous_cid
        while previous_cid is not None:
            if max_depth is not None and depth >= max_depth:
                break

            previous_state = IPFSDictChain(cid=previous_cid)
            change_log.append(previous_state.changes())
            previous_cid = previous_state.previous_cid

            depth += 1

        return change_log


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
    connect_to_ipfs()