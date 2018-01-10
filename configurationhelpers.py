#!/usr/bin/python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser

CONFIGURATION_FILE = 'configuration/Spellbook.conf'


def get_config():
    # Read the spellbook configuration file
    config = ConfigParser()
    config.read(CONFIGURATION_FILE)


def get_host_and_port():
    # Read the spellbook configuration file
    config = ConfigParser()
    config.read(CONFIGURATION_FILE)

    # Check if the spellbook configuration file contains a [RESTAPI] section
    if not config.has_section('RESTAPI'):
        raise Exception('Configuration file %s does not have a [RESTAPI] section ' % CONFIGURATION_FILE)

    # Check if the [RESTAPI] section has options for 'host' and 'port'
    if not config.has_option('RESTAPI', 'host'):
        raise Exception("Configuration file %s does not have an option 'host' in the [RESTAPI] section" % CONFIGURATION_FILE)
    host = config.get('RESTAPI', 'host')

    if not config.has_option('RESTAPI', 'port'):
        raise Exception("Configuration file %s does not have an option 'port' in the [RESTAPI] section" % CONFIGURATION_FILE)
    port = config.get('RESTAPI', 'port')

    return host, port


def get_key_and_secret():
    # Read the spellbook configuration file
    config = ConfigParser()
    config.read(CONFIGURATION_FILE)

    # Check if the spellbook configuration file contains a [Authentication] section
    if not config.has_section('Authentication'):
        raise Exception('Configuration file %s does not have a [Authentication] section ' % CONFIGURATION_FILE)

    # Check if the [Authentication] section has options for 'host' and 'port'
    if not config.has_option('Authentication', 'key'):
        raise Exception("Configuration file %s does not have an option 'key' in the [Authentication] section" % CONFIGURATION_FILE)
    key = config.get('Authentication', 'key')

    if not config.has_option('Authentication', 'secret'):
        raise Exception("Configuration file %s does not have an option 'secret' in the [Authentication] section" % CONFIGURATION_FILE)
    secret = config.get('Authentication', 'secret')

    return key, secret


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
