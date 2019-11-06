#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
try:
    from ConfigParser import ConfigParser
except:
    from configparser import ConfigParser
from helpers.jsonhelpers import load_from_json_file
from authentication import initialize_api_keys_file

PROGRAM_DIR = os.path.abspath(os.path.dirname(__file__))

configuration_file = os.path.join(PROGRAM_DIR, 'configuration', 'spellbook.conf')

config = ConfigParser()
if not os.path.isfile(configuration_file):
    config.read(os.path.join(PROGRAM_DIR, 'configuration', 'example_configuration_file.conf'))
else:
    config.read(os.path.join(PROGRAM_DIR, 'configuration', 'spellbook.conf'))


# RESTAPI settings
current_host = config.get(section='RESTAPI', option='host')
host = input('Enter the IP address of the server or press enter to keep the current value (%s) ' % current_host) or current_host
config.set(section='RESTAPI', option='host', value=host)

current_port = config.get(section='RESTAPI', option='port')
port = input('Enter the port of the server or press enter to keep the current value (%s) ' % current_port) or current_port
config.set(section='RESTAPI', option='port', value=port)

current_notification_email = config.get(section='RESTAPI', option='notification_email', fallback='someone@example.com')
notification_email = input('Enter the email address for notifications (%s) ' % current_notification_email) or current_notification_email
config.set(section='RESTAPI', option='notification_email', value=notification_email)

current_mail_on_exception = config.get(section='RESTAPI', option='mail_on_exception', fallback='false')
mail_on_exception = input('Send email to notification email address when exceptions occur (%s) ' % current_mail_on_exception) or current_mail_on_exception
config.set(section='RESTAPI', option='mail_on_exception', value=mail_on_exception)

# Authentication settings
api_keys_file = os.path.join(PROGRAM_DIR, 'json', 'private', 'api_keys.json')
if not os.path.isfile(api_keys_file):
    print('Initializing api keys')
    initialize_api_keys_file()

api_keys = load_from_json_file(filename=api_keys_file)

current_key = list(api_keys.keys())[0]
key = input('Enter the API key or press enter to keep the current value (%s) ' % current_key) or current_key
config.set(section='Authentication', option='key', value=key)

current_secret = api_keys[key]['secret']
secret = input('Enter the API secret or press enter to keep the current value (%s) ' % current_secret) or current_secret
config.set(section='Authentication', option='secret', value=secret)


# Wallet settings
current_wallet_dir = config.get(section='Wallet', option='wallet_dir')
wallet_dir = input('Enter the directory for the hot wallet or press enter to keep the current value (%s) ' % current_wallet_dir) or current_wallet_dir
config.set(section='Wallet', option='wallet_dir', value=wallet_dir)

current_default_wallet = config.get(section='Wallet', option='default_wallet')
default_wallet = input('Enter the name of the hot wallet or press enter to keep the current value (%s) ' % current_default_wallet) or current_default_wallet
config.set(section='Wallet', option='default_wallet', value=default_wallet)

current_use_testnet = config.get(section='Wallet', option='use_testnet')
use_testnet = input('Enter if the wallet should use testnet or press enter to keep the current value (%s) ' % current_use_testnet) or current_use_testnet
config.set(section='Wallet', option='use_testnet', value=use_testnet)


# Transactions settings
current_minimum_output_value = config.get(section='Transactions', option='minimum_output_value')
minimum_output_value = input('Enter the minimum output value or press enter to keep the current value (%s) ' % current_minimum_output_value) or current_minimum_output_value
config.set(section='Transactions', option='minimum_output_value', value=minimum_output_value)

current_max_tx_fee_percentage = config.get(section='Transactions', option='max_tx_fee_percentage')
max_tx_fee_percentage = input('Enter the maximum tx fee percentage or press enter to keep the current value (%s) ' % current_max_tx_fee_percentage) or current_max_tx_fee_percentage
config.set(section='Transactions', option='max_tx_fee_percentage', value=max_tx_fee_percentage)


# Apps settings
current_app_data_dir = config.get(section='APPS', option='app_data_dir')
app_data_dir = input('Enter the directory for the app data or press enter to keep the current value (%s) ' % current_app_data_dir) or current_app_data_dir
config.set(section='APPS', option='app_data_dir', value=app_data_dir)


# SMTP settings
current_enable_smtp = config.get(section='SMTP', option='enable_smtp')
enable_smtp = input('Would you like to enable SMTP? (current=%s): ' % current_enable_smtp) or current_enable_smtp
enable_smtp = 'true' if enable_smtp in ['true', 'True', True, 'Yes' 'yes', 'y', 'Y'] else 'false'
config.set(section='SMTP', option='enable_smtp', value=enable_smtp)


if config.getboolean(section='SMTP', option='enable_smtp') is True:
    current_from_address = config.get(section='SMTP', option='from_address')
    from_address = input('Enter the FROM address for sending emails or press enter to keep the current value (%s) ' % current_from_address) or current_from_address
    config.set(section='SMTP', option='from_address', value=from_address)

    current_host = config.get(section='SMTP', option='host')
    host = input('Enter the host address of the SMTP server or press enter to keep the current value (%s) ' % current_host) or current_host
    config.set(section='SMTP', option='host', value=host)

    current_port = config.get(section='SMTP', option='port')
    port = input('Enter the port of the SMTP server or press enter to keep the current value (%s) ' % current_port) or current_port
    config.set(section='SMTP', option='port', value=port)

    current_user = config.get(section='SMTP', option='user')
    user = input('Enter the username for the SMTP server or press enter to keep the current value (%s) ' % current_user) or current_user
    config.set(section='SMTP', option='user', value=user)

    current_password = config.get(section='SMTP', option='password')
    password = input('Enter the password for the SMTP server or press enter to keep the current value (%s) ' % current_password) or current_password
    config.set(section='SMTP', option='password', value=password)


# IPFS settings
current_enable_ipfs = config.get(section='IPFS', option='enable_ipfs')
enable_ipfs = input('Would you like to enable IPFS? (current=%s): ' % current_enable_ipfs) or current_enable_ipfs
enable_ipfs = 'true' if enable_ipfs in ['true', 'True', True, 'Yes' 'yes', 'y', 'Y'] else 'false'
config.set(section='IPFS', option='enable_ipfs', value=enable_ipfs)

if config.getboolean(section='IPFS', option='enable_ipfs') is True:
    current_host = config.get(section='IPFS', option='api_host')
    api_host = input('Enter the IP address of the IPFS API or press enter to keep the current value (%s) ' % current_host) or current_host
    config.set(section='IPFS', option='api_host', value=api_host)

    current_port = config.get(section='IPFS', option='api_port')
    api_port = input('Enter the port of the IPFS API or press enter to keep the current value (%s) ' % current_port) or current_port
    config.set(section='IPFS', option='api_port', value=api_port)

    current_host = config.get(section='IPFS', option='gateway_host')
    gateway_host = input('Enter the IP address of the IPFS Gateway or press enter to keep the current value (%s) ' % current_host) or current_host
    config.set(section='IPFS', option='gateway_host', value=gateway_host)

    current_port = config.get(section='IPFS', option='gateway_port')
    gateway_port = input('Enter the port of the IPFS Gateway or press enter to keep the current value (%s) ' % current_port) or current_port
    config.set(section='IPFS', option='gateway_port', value=gateway_port)

with open(configuration_file, 'w') as output_file:
    config.write(output_file)
    print('spellbook.conf file updated')

print("")
print("Don't forget to initialize the hot wallet before starting the spellbookserver")
print("use command: ./hot_wallet.py set_bip44 <your 12 or 24 mnemonic words>")
print("")
print("To start the server, use command: ./spellbookserver.py")
print("")

