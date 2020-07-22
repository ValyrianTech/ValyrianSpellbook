#!/usr/bin/env python
# -*- coding: utf-8 -*-
import simplejson

from helpers.loghelpers import LOG
from abc import abstractmethod, ABCMeta
from validators.validators import valid_address
from helpers.ipfshelpers import get_json, add_json


class SpellbookScript(object):
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        self.address = kwargs['address'] if 'address' in kwargs else None
        if self.address is not None and not valid_address(self.address):
            raise Exception('%s is not a valid address!' % self.address)

        self.message = kwargs['message'] if 'message' in kwargs else None
        self.signature = kwargs['signature'] if 'signature' in kwargs else None

        self.trigger_id = kwargs['trigger_id'] if 'trigger_id' in kwargs else None
        self.trigger_type = kwargs['trigger_type'] if 'trigger_type' in kwargs else None
        self.script = kwargs['script'] if 'script' in kwargs else None
        self.data = kwargs['data'] if 'data' in kwargs else None
        self.triggered = kwargs['triggered'] if 'triggered' in kwargs else None
        self.multi = kwargs['multi'] if 'multi' in kwargs else None
        self.description = kwargs['description'] if 'description' in kwargs else None
        self.creator_name = kwargs['creator_name'] if 'creator_name' in kwargs else None
        self.creator_email = kwargs['creator_email'] if 'creator_email' in kwargs else None
        self.youtube = kwargs['youtube'] if 'youtube' in kwargs else None
        self.status = kwargs['status'] if 'status' in kwargs else None
        self.visibility = kwargs['visibility'] if 'visibility' in kwargs else None
        self.created = kwargs['created'] if 'created' in kwargs else None
        self.actions = kwargs['actions'] if 'actions' in kwargs else None

        self.json = kwargs['json'] if 'json' in kwargs else None
        self.ipfs_hash = None
        self.ipfs_object = kwargs['ipfs_object'] if 'ipfs_object' in kwargs else None
        self.text = None

        self.http_response = None
        self.new_actions = []

        if self.message is not None:
            self.process_message()

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    def process_message(self):
        if self.message[:6] == '/ipfs/':
            self.ipfs_hash = self.message[6:]
            LOG.info('Message contains a IPFS hash: %s' % self.ipfs_hash)
            return self.process_ipfs_hash(ipfs_hash=self.ipfs_hash)
        else:
            try:
                json_data = simplejson.loads(self.message)
            except ValueError:
                json_data = None

            if json_data is not None:
                LOG.info('Message contains json data: %s' % self.message)
                return self.process_json_data(json_data=json_data)

            else:
                LOG.info('Message contains simple text: %s' % self.message)
                return self.process_text(self.message)

    def process_ipfs_hash(self, ipfs_hash):
        LOG.info('Retrieving IPFS object')

        if self.ipfs_object is not None:
            LOG.info('IPFS object given with request, uploading data to local IPFS node to check that hashes are equal')
            local_ipfs_hash = add_json(data=self.ipfs_object)
            if ipfs_hash != local_ipfs_hash:
                LOG.error('Supplied object does not correspond to the given IPFS hash: %s != %s' % (ipfs_hash, local_ipfs_hash))
                return

        try:
            data = get_json(cid=ipfs_hash)
            if isinstance(data, dict):
                self.json = data
            elif isinstance(data, str):
                self.json = simplejson.loads(data)
            else:
                raise Exception('IPFS hash does not contain a dict or a json string: %s -> %s' % (ipfs_hash, data))
            LOG.info('Message contains json data: %s' % self.json)
        except Exception as ex:
            LOG.error('IPFS hash does not contain valid json data: %s' % ex)
            return

    def process_json_data(self, json_data):
        LOG.info('Processing JSON data')
        self.json = json_data

    def process_text(self, text):
        LOG.info('Processing text data')
        self.text = text

    def attach_action(self, action_id):
        """
        Add an action_id to the list of actions the trigger will execute

        :param action_id: The id of the action
        """
        self.new_actions.append(action_id)

    def exit_with_error(self, message):
        """
        Log an error message and set the http response with the same error message

        :param message: The error message
        """
        LOG.error(message)
        self.http_response = {'error': message}
