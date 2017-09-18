#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import simplejson
import random
import string
import hashlib
import hmac
import base64

from jsonhelpers import save_to_json_file, load_from_json_file


class AuthenticationStatus(object):
    OK = 'OK'
    INVALID_API_KEY = 'Invalid API key'
    NO_API_KEY = 'No API key supplied'
    INVALID_SIGNATURE = 'Invalid signature'
    NO_SIGNATURE = 'No signature supplied'
    INVALID_JSON_FILE = 'Invalid json file'


API_KEYS_FILE = 'api_keys.json'


def initialize_api_keys_file():
    """
    Initialize the api_keys.json file with a new random api key and secret for the admin
    """
    # Create a random string of characters (uppercase letters and digits) for a api_key and api_secret pair
    api_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
    api_secret = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))

    data = {api_key: {'secret:': api_secret,
                      'permissions': 'all'}}

    save_to_json_file(API_KEYS_FILE, data)


def check_authentication(headers, body):
    if 'API_Key' in headers:
        api_key = headers['API_Key']
        api_keys = load_from_json_file(API_KEYS_FILE)

        if api_keys is None:
            authentication_status = AuthenticationStatus.INVALID_JSON_FILE

        elif api_key in api_keys:
            if 'API_Sign' in headers:
                signature = str(headers['API_Sign'])
                message = hashlib.sha256(body).digest()
                if signature != base64.b64encode(hmac.new(base64.b64decode(api_keys[api_key].secret),
                                                          message,
                                                          hashlib.sha512).digest()):
                    authentication_status = AuthenticationStatus.INVALID_SIGNATURE
                else:
                    authentication_status = AuthenticationStatus.OK
            else:
                authentication_status = AuthenticationStatus.NO_SIGNATURE
        else:
            authentication_status = AuthenticationStatus.INVALID_API_KEY
    else:
        authentication_status = AuthenticationStatus.NO_API_KEY

    return authentication_status
