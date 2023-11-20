#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from configparser import ConfigParser
from helpers.jsonhelpers import load_from_json_file
from authentication import initialize_api_keys_file
from helpers.configurationhelpers import what_is_my_ip


def update_config(config, section, option, prompt, current_value=None, fallback=None):
    if current_value is None:
        current_value = config.get(section=section, option=option, fallback=fallback)

    new_value = input(prompt % current_value) or current_value
    config.set(section=section, option=option, value=new_value)


PROGRAM_DIR = os.path.abspath(os.path.dirname(__file__))

configuration_file = os.path.join(PROGRAM_DIR, 'configuration', 'spellbook.conf')

config = ConfigParser()
if not os.path.isfile(configuration_file):
    config.read(os.path.join(PROGRAM_DIR, 'configuration', 'example_configuration_file.conf'))
else:
    config.read(os.path.join(PROGRAM_DIR, 'configuration', 'spellbook.conf'))

# RESTAPI settings
update_config(config, 'RESTAPI', 'host', 'Enter the IP address of the server or press enter to keep the current value (%s) ')
if config.get(section='RESTAPI', option='host') == '':
    config.set(section='RESTAPI', option='host', value=what_is_my_ip())

update_config(config, 'RESTAPI', 'port', 'Enter the port of the server or press enter to keep the current value (%s) ')
update_config(config, 'RESTAPI', 'notification_email', 'Enter the email address for notifications (%s) ', fallback='someone@example.com')
update_config(config, 'RESTAPI', 'mail_on_exception', 'Send email to notification email address when exceptions occur (%s) ', fallback='false')
update_config(config, 'RESTAPI', 'python_exe', 'Enter the python exe to use (%s) ', fallback='python3.10')
update_config(config, 'RESTAPI', 'websocket_port', 'Enter the websocket port to use (%s) ', fallback='8765')

# Authentication settings
api_keys_file = os.path.join(PROGRAM_DIR, 'json', 'private', 'api_keys.json')
if not os.path.isfile(api_keys_file):
    print('Initializing api keys')
    initialize_api_keys_file()

api_keys = load_from_json_file(filename=api_keys_file)

update_config(config, 'Authentication', 'key', 'Enter the API key or press enter to keep the current value (%s) ')
update_config(config, 'Authentication', 'secret', 'Enter the API secret or press enter to keep the current value (%s) ')

# Wallet settings
update_config(config, 'Wallet', 'wallet_dir', 'Enter the directory for the hot wallet or press enter to keep the current value (%s) ')
update_config(config, 'Wallet', 'default_wallet', 'Enter the name of the hot wallet or press enter to keep the current value (%s) ')
update_config(config, 'Wallet', 'use_testnet', 'Enter if the wallet should use testnet or press enter to keep the current value (%s) ')

# Transactions settings
update_config(config, 'Transactions', 'minimum_output_value', 'Enter the minimum output value or press enter to keep the current value (%s) ')
update_config(config, 'Transactions', 'max_tx_fee_percentage', 'Enter the maximum tx fee percentage or press enter to keep the current value (%s) ')

# Apps settings
update_config(config, 'APPS', 'app_data_dir', 'Enter the directory for the app data or press enter to keep the current value (%s) ')

# SMTP settings
update_config(config, 'SMTP', 'enable_smtp', 'Would you like to enable SMTP? (current=%s): ')

if config.getboolean(section='SMTP', option='enable_smtp') is True:
    update_config(config, 'SMTP', 'from_address', 'Enter the FROM address for sending emails or press enter to keep the current value (%s) ')
    update_config(config, 'SMTP', 'host', 'Enter the host address of the SMTP server or press enter to keep the current value (%s) ')
    update_config(config, 'SMTP', 'port', 'Enter the port of the SMTP server or press enter to keep the current value (%s) ')
    update_config(config, 'SMTP', 'user', 'Enter the username for the SMTP server or press enter to keep the current value (%s) ')
    update_config(config, 'SMTP', 'password', 'Enter the password for the SMTP server or press enter to keep the current value (%s) ')

# IPFS settings
update_config(config, 'IPFS', 'enable_ipfs', 'Would you like to enable IPFS? (current=%s): ')

if config.getboolean(section='IPFS', option='enable_ipfs') is True:
    update_config(config, 'IPFS', 'api_host', 'Enter the IP address of the IPFS API or press enter to keep the current value (%s) ')
    update_config(config, 'IPFS', 'api_port', 'Enter the port of the IPFS API or press enter to keep the current value (%s) ')
    update_config(config, 'IPFS', 'gateway_host', 'Enter the IP address of the IPFS Gateway or press enter to keep the current value (%s) ')
    update_config(config, 'IPFS', 'gateway_port', 'Enter the port of the IPFS Gateway or press enter to keep the current value (%s) ')

# SSL settings
update_config(config, 'SSL', 'enable_ssl', 'Would you like to enable SSL? (current=%s): ')

if config.getboolean(section='SSL', option='enable_ssl') is True:
    update_config(config, 'SSL', 'domain_name', 'Enter the domain name or press enter to keep the current value (%s) ')
    update_config(config, 'SSL', 'certificate', 'Enter the certificate filename or press enter to keep the current value (%s) ')
    update_config(config, 'SSL', 'private_key', 'Enter the private_key filename or press enter to keep the current value (%s) ')
    update_config(config, 'SSL', 'certificate_chain', 'Enter the certificate_chain filename or press enter to keep the current value (%s) ')

# Twitter settings
update_config(config, 'Twitter', 'enable_twitter', 'Would you like to enable Twitter? (current=%s): ')

if config.getboolean(section='Twitter', option='enable_twitter') is True:
    update_config(config, 'Twitter', 'consumer_key', 'Enter the consumer key or press enter to keep the current value (%s) ')
    update_config(config, 'Twitter', 'consumer_secret', 'Enter the consumer secret or press enter to keep the current value (%s) ')
    update_config(config, 'Twitter', 'access_token', 'Enter the access token or press enter to keep the current value (%s) ')
    update_config(config, 'Twitter', 'access_token_secret', 'Enter the access token secret or press enter to keep the current value (%s) ')
    update_config(config, 'Twitter', 'bearer_token', 'Enter the bearer token or press enter to keep the current value (%s) ')

# OpenAI settings
update_config(config, 'OpenAI', 'enable_openai', 'Would you like to enable OpenAI? (current=%s): ')

if config.getboolean(section='OpenAI', option='enable_openai') is True:
    update_config(config, 'OpenAI', 'api_key', 'Enter the API key or press enter to keep the current value (%s) ')
    update_config(config, 'OpenAI', 'organization', 'Enter the organization or press enter to keep the current value (%s) ')

# Mastodon settings
update_config(config, 'Mastodon', 'enable_mastodon', 'Would you like to enable Mastodon? (current=%s): ')

if config.getboolean(section='Mastodon', option='enable_mastodon') is True:
    update_config(config, 'Mastodon', 'client_id', 'Enter the client_id or press enter to keep the current value (%s) ')
    update_config(config, 'Mastodon', 'client_secret', 'Enter the client_secret or press enter to keep the current value (%s) ')
    update_config(config, 'Mastodon', 'access_token', 'Enter the access token or press enter to keep the current value (%s) ')
    update_config(config, 'Mastodon', 'api_base_url', 'Enter the api_base_url or press enter to keep the current value (%s) ')

# Nostr settings
if config.getboolean(section='Nostr', option='enable_nostr') is True:
    update_config(config, 'Nostr', 'nsec', 'Enter the nsec key or press enter to keep the current value (%s) ')

# Oobabooga settings
if config.getboolean(section='Oobabooga', option='enable_oobabooga') is True:
    update_config(config, 'Oobabooga', 'default_model', 'Enter the id of the default expert model (e.g. chat) or press enter to keep the current value (%s) ')

with open(configuration_file, 'w') as output_file:
    config.write(output_file)
    print('spellbook.conf file updated')

print("")
print("Don't forget to initialize the hot wallet before starting the spellbookserver")
print("use command: ./hot_wallet.py set_bip44 <your 12 or 24 mnemonic words>")
print("")
print("To start the server, use command: ./spellbookserver.py")
print("")
