#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from configparser import ConfigParser
from decorators import verify_config

CONFIGURATION_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "configuration", "spellbook.conf"))


def spellbook_config():
    # Read the spellbook configuration file
    config = ConfigParser(interpolation=None)
    config.read(CONFIGURATION_FILE)
    return config


@verify_config('RESTAPI', 'host')
def get_host():
    return spellbook_config().get('RESTAPI', 'host')


@verify_config('RESTAPI', 'port')
def get_port():
    return int(spellbook_config().get('RESTAPI', 'port'))


@verify_config('RESTAPI', 'notification_email')
def get_notification_email():
    return spellbook_config().get('RESTAPI', 'notification_email')


@verify_config('RESTAPI', 'mail_on_exception')
def get_mail_on_exception():
    return spellbook_config().getboolean('RESTAPI', 'mail_on_exception')


@verify_config('RESTAPI', 'python_exe')
def get_python_exe():
    return spellbook_config().get('RESTAPI', 'python_exe')


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


@verify_config('SSL', 'enable_ssl')
def get_enable_ssl():
    return spellbook_config().getboolean('SSL', 'enable_ssl')


@verify_config('SSL', 'certificate')
def get_ssl_certificate():
    return spellbook_config().get('SSL', 'certificate')


@verify_config('SSL', 'private_key')
def get_ssl_private_key():
    return spellbook_config().get('SSL', 'private_key')


@verify_config('SSL', 'certificate_chain')
def get_ssl_certificate_chain():
    return spellbook_config().get('SSL', 'certificate_chain')


def get_spellbook_uri():
    if get_enable_ssl() is True:
        uri = 'https://{host}:{port}'.format(host=get_host(), port=get_port())
    else:
        uri = 'http://{host}:{port}'.format(host=get_host(), port=get_port())

    return uri


@verify_config('Twitter', 'enable_twitter')
def get_enable_twitter():
    return spellbook_config().getboolean('Twitter', 'enable_twitter')


@verify_config('Twitter', 'consumer_key')
def get_twitter_consumer_key():
    return spellbook_config().get('Twitter', 'consumer_key')


@verify_config('Twitter', 'consumer_secret')
def get_twitter_consumer_secret():
    return spellbook_config().get('Twitter', 'consumer_secret')


@verify_config('Twitter', 'access_token')
def get_twitter_access_token():
    return spellbook_config().get('Twitter', 'access_token')


@verify_config('Twitter', 'access_token_secret')
def get_twitter_access_token_secret():
    return spellbook_config().get('Twitter', 'access_token_secret')


@verify_config('Twitter', 'bearer_token')
def get_twitter_bearer_token():
    return spellbook_config().get('Twitter', 'bearer_token')
