#!/usr/bin/python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
from decorators import verify_config


CONFIGURATION_FILE = 'configuration/Spellbook.conf'


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


@verify_config('Transactions', 'max_tx_fee_percentage')
def get_max_tx_fee_percentage():
    return float(spellbook_config().get('Transactions', 'max_tx_fee_percentage'))


@verify_config('Transactions', 'minimum_output_value')
def get_minimum_output_value():
    return int(spellbook_config().get('Transactions', 'minimum_output_value'))
