#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
try:
    from ConfigParser import ConfigParser  # Python2.7
except:
    from configparser import ConfigParser  # Python3
from decorators import verify_config

CONFIGURATION_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "configuration", "spellbook.conf"))


def spellbook_config():
    # Read the spellbook configuration file
    config = ConfigParser()
    config.read(CONFIGURATION_FILE)
    return config


@verify_config('RESTAPI', 'host')
def get_host():
    return spellbook_config().get('RESTAPI', 'host')


@verify_config('RESTAPI', 'port')
def get_port():
    return int(spellbook_config().get('RESTAPI', 'port'))


@verify_config('Authentication', 'key')
def get_key():
    return spellbook_config().get('Authentication', 'key')


@verify_config('Authentication', 'secret')
def get_secret():
    return spellbook_config().get('Authentication', 'secret')


@verify_config('Wallet', 'wallet_dir')
def get_wallet_dir():
    return spellbook_config().get('Wallet', 'wallet_dir')


@verify_config('Wallet', 'default_wallet')
def get_default_wallet():
    return spellbook_config().get('Wallet', 'default_wallet')


@verify_config('Wallet', 'use_testnet')
def get_use_testnet():
    return True if spellbook_config().get('Wallet', 'use_testnet') in ['True', 'true'] else False


@verify_config('Transactions', 'max_tx_fee_percentage')
def get_max_tx_fee_percentage():
    return float(spellbook_config().get('Transactions', 'max_tx_fee_percentage'))


@verify_config('Transactions', 'minimum_output_value')
def get_minimum_output_value():
    return int(spellbook_config().get('Transactions', 'minimum_output_value'))


@verify_config('SMTP', 'enable_smtp')
def get_enable_smtp():
    return spellbook_config().get('SMTP', 'enable_smtp')


@verify_config('SMTP', 'from_address')
def get_smtp_from_address():
    return spellbook_config().get('SMTP', 'from_address')


@verify_config('SMTP', 'host')
def get_smtp_host():
    return spellbook_config().get('SMTP', 'host')


@verify_config('SMTP', 'port')
def get_smtp_port():
    return spellbook_config().get('SMTP', 'port')


@verify_config('SMTP', 'user')
def get_smtp_user():
    return spellbook_config().get('SMTP', 'user')


@verify_config('SMTP', 'password')
def get_smtp_password():
    return spellbook_config().get('SMTP', 'password')


@verify_config('IPFS', 'enable_ipfs')
def get_enable_ipfs():
    return spellbook_config().getboolean('IPFS', 'enable_ipfs')


@verify_config('IPFS', 'api_host')
def get_ipfs_api_host():
    return spellbook_config().get('IPFS', 'api_host')


@verify_config('IPFS', 'api_port')
def get_ipfs_api_port():
    return spellbook_config().get('IPFS', 'api_port')


@verify_config('IPFS', 'gateway_host')
def get_ipfs_gateway_host():
    return spellbook_config().get('IPFS', 'gateway_host')


@verify_config('IPFS', 'gateway_port')
def get_ipfs_gateway_port():
    return spellbook_config().get('IPFS', 'gateway_port')


@verify_config('APPS', 'app_data_dir')
def get_app_data_dir():
    return spellbook_config().get('APPS', 'app_data_dir')
