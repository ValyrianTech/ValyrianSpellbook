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


def get_wallet_info():
    # Read the spellbook configuration file
    config = ConfigParser()
    config.read(CONFIGURATION_FILE)

    # Check if the spellbook configuration file contains a [Wallet] section
    if not config.has_section('Wallet'):
        raise Exception('Configuration file %s does not have a [Wallet] section ' % CONFIGURATION_FILE)

    # Check if the [Wallet] section has options for 'wallet_dir' and 'default_wallet'
    if not config.has_option('Wallet', 'wallet_dir'):
        raise Exception(
            "Configuration file %s does not have an option 'wallet_dir' in the [Wallet] section" % CONFIGURATION_FILE)
    wallet_dir = config.get('Wallet', 'wallet_dir')

    if not config.has_option('Wallet', 'default_wallet'):
        raise Exception(
            "Configuration file %s does not have an option 'default_wallet' in the [Wallet] section" % CONFIGURATION_FILE)
    wallet_id = config.get('Wallet', 'default_wallet')

    return wallet_dir, wallet_id


@verify_config('Transactions', 'max_tx_fee_percentage')
def get_max_tx_fee_percentage():
    # Read the spellbook configuration file
    config = ConfigParser()
    config.read(CONFIGURATION_FILE)

    return float(config.get('Transactions', 'max_tx_fee_percentage'))


@verify_config('Transactions', 'minimum_output_value')
def get_minimum_output_value():
    # Read the spellbook configuration file
    config = ConfigParser()
    config.read(CONFIGURATION_FILE)

    return int(config.get('Transactions', 'minimum_output_value'))
