#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Configuration helpers for reading Spellbook settings from the config file."""

import os
import requests
from configparser import ConfigParser
from decorators import verify_config

CONFIGURATION_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "configuration", "spellbook.conf"))


def spellbook_config():
    """Read and return the Spellbook configuration parser."""
    # Read the spellbook configuration file
    config = ConfigParser(interpolation=None)
    config.read(CONFIGURATION_FILE)
    return config


def what_is_my_ip() -> str:
    """
    Get my public facing ip address

    :return: String - ip address
    """
    try:
        ip = requests.get("https://api.ipify.org/?format=json").json()['ip']
    except Exception as ex:
        print(f'Unable to get ip: {ex}')
        return ''

    return ip


@verify_config('RESTAPI', 'host')
def get_host():
    """Get the REST API host from the configuration."""
    return spellbook_config().get('RESTAPI', 'host')


@verify_config('RESTAPI', 'port')
def get_port():
    """Get the REST API port from the configuration as an integer."""
    return int(spellbook_config().get('RESTAPI', 'port'))


@verify_config('RESTAPI', 'notification_email')
def get_notification_email():
    """Get the notification email address from the configuration."""
    return spellbook_config().get('RESTAPI', 'notification_email')


@verify_config('RESTAPI', 'mail_on_exception')
def get_mail_on_exception():
    """Get whether to send email on exceptions from the configuration."""
    return spellbook_config().getboolean('RESTAPI', 'mail_on_exception')


@verify_config('RESTAPI', 'python_exe')
def get_python_exe():
    """Get the Python executable path from the configuration."""
    return spellbook_config().get('RESTAPI', 'python_exe')


@verify_config('RESTAPI', 'websocket_port')
def get_websocket_port():
    """Get the WebSocket server port from the configuration."""
    return spellbook_config().get('RESTAPI', 'websocket_port')


@verify_config('Authentication', 'key')
def get_key():
    """Get the API authentication key from the configuration."""
    return spellbook_config().get('Authentication', 'key')


@verify_config('Authentication', 'secret')
def get_secret():
    """Get the API authentication secret from the configuration."""
    return spellbook_config().get('Authentication', 'secret')


@verify_config('Wallet', 'enable_wallet')
def get_enable_wallet():
    """Get whether the wallet is enabled from the configuration."""
    return spellbook_config().get('Wallet', 'enable_wallet')


@verify_config('Wallet', 'wallet_dir')
def get_wallet_dir():
    """Get the wallet directory path from the configuration."""
    return spellbook_config().get('Wallet', 'wallet_dir')


@verify_config('Wallet', 'default_wallet')
def get_default_wallet():
    """Get the default wallet ID from the configuration."""
    return spellbook_config().get('Wallet', 'default_wallet')


@verify_config('Wallet', 'use_testnet')
def get_use_testnet():
    """Get whether testnet mode is enabled from the configuration."""
    return True if spellbook_config().get('Wallet', 'use_testnet') in ['True', 'true'] else False


@verify_config('Transactions', 'max_tx_fee_percentage')
def get_max_tx_fee_percentage():
    """Get the maximum transaction fee percentage from the configuration."""
    return float(spellbook_config().get('Transactions', 'max_tx_fee_percentage'))


@verify_config('Transactions', 'minimum_output_value')
def get_minimum_output_value():
    """Get the minimum output value for transactions from the configuration."""
    return int(spellbook_config().get('Transactions', 'minimum_output_value'))


@verify_config('SMTP', 'enable_smtp')
def get_enable_smtp():
    """Get whether SMTP email is enabled from the configuration."""
    return spellbook_config().get('SMTP', 'enable_smtp')


@verify_config('SMTP', 'from_address')
def get_smtp_from_address():
    """Get the SMTP sender email address from the configuration."""
    return spellbook_config().get('SMTP', 'from_address')


@verify_config('SMTP', 'host')
def get_smtp_host():
    """Get the SMTP server host from the configuration."""
    return spellbook_config().get('SMTP', 'host')


@verify_config('SMTP', 'port')
def get_smtp_port():
    """Get the SMTP server port from the configuration."""
    return spellbook_config().get('SMTP', 'port')


@verify_config('SMTP', 'user')
def get_smtp_user():
    """Get the SMTP username from the configuration."""
    return spellbook_config().get('SMTP', 'user')


@verify_config('SMTP', 'password')
def get_smtp_password():
    """Get the SMTP password from the configuration."""
    return spellbook_config().get('SMTP', 'password')


@verify_config('IPFS', 'enable_ipfs')
def get_enable_ipfs():
    """Get whether IPFS is enabled from the configuration."""
    return spellbook_config().getboolean('IPFS', 'enable_ipfs')


@verify_config('IPFS', 'api_host')
def get_ipfs_api_host():
    """Get the IPFS API host from the configuration."""
    return spellbook_config().get('IPFS', 'api_host')


@verify_config('IPFS', 'api_port')
def get_ipfs_api_port():
    """Get the IPFS API port from the configuration."""
    return spellbook_config().get('IPFS', 'api_port')


@verify_config('IPFS', 'gateway_host')
def get_ipfs_gateway_host():
    """Get the IPFS gateway host from the configuration."""
    return spellbook_config().get('IPFS', 'gateway_host')


@verify_config('IPFS', 'gateway_port')
def get_ipfs_gateway_port():
    """Get the IPFS gateway port from the configuration."""
    return spellbook_config().get('IPFS', 'gateway_port')


@verify_config('APPS', 'app_data_dir')
def get_app_data_dir():
    """Get the application data directory from the configuration."""
    return spellbook_config().get('APPS', 'app_data_dir')


@verify_config('SSL', 'enable_ssl')
def get_enable_ssl():
    """Get whether SSL is enabled from the configuration."""
    return spellbook_config().getboolean('SSL', 'enable_ssl')


@verify_config('SSL', 'domain_name')
def get_domain_name():
    """Get the SSL domain name from the configuration."""
    return spellbook_config().get('SSL', 'domain_name')


@verify_config('SSL', 'certificate')
def get_ssl_certificate():
    """Get the SSL certificate file path from the configuration."""
    return spellbook_config().get('SSL', 'certificate')


@verify_config('SSL', 'private_key')
def get_ssl_private_key():
    """Get the SSL private key file path from the configuration."""
    return spellbook_config().get('SSL', 'private_key')


@verify_config('SSL', 'certificate_chain')
def get_ssl_certificate_chain():
    """Get the SSL certificate chain file path from the configuration."""
    return spellbook_config().get('SSL', 'certificate_chain')


def get_spellbook_uri():
    """Get the full Spellbook URI (https or http) based on SSL settings."""
    if get_enable_ssl() is True:
        uri = 'https://{domain_name}:{port}'.format(domain_name=get_domain_name(), port=get_port())
    else:
        uri = 'http://{host}:{port}'.format(host=get_host(), port=get_port())

    return uri


@verify_config('Twitter', 'enable_twitter')
def get_enable_twitter():
    """Get whether Twitter integration is enabled from the configuration."""
    return spellbook_config().getboolean('Twitter', 'enable_twitter')


@verify_config('Twitter', 'consumer_key')
def get_twitter_consumer_key():
    """Get the Twitter consumer key from the configuration."""
    return spellbook_config().get('Twitter', 'consumer_key')


@verify_config('Twitter', 'consumer_secret')
def get_twitter_consumer_secret():
    """Get the Twitter consumer secret from the configuration."""
    return spellbook_config().get('Twitter', 'consumer_secret')


@verify_config('Twitter', 'access_token')
def get_twitter_access_token():
    """Get the Twitter access token from the configuration."""
    return spellbook_config().get('Twitter', 'access_token')


@verify_config('Twitter', 'access_token_secret')
def get_twitter_access_token_secret():
    """Get the Twitter access token secret from the configuration."""
    return spellbook_config().get('Twitter', 'access_token_secret')


@verify_config('Twitter', 'bearer_token')
def get_twitter_bearer_token():
    """Get the Twitter bearer token from the configuration."""
    return spellbook_config().get('Twitter', 'bearer_token')


@verify_config('OpenAI', 'enable_openai')
def get_enable_openai():
    """Get whether OpenAI integration is enabled from the configuration."""
    return spellbook_config().getboolean('OpenAI', 'enable_openai')


@verify_config('OpenAI', 'api_key')
def get_openai_api_key():
    """Get the OpenAI API key from the configuration."""
    return spellbook_config().get('OpenAI', 'api_key')


@verify_config('OpenAI', 'organization')
def get_openai_organization():
    """Get the OpenAI organization from the configuration."""
    return spellbook_config().get('OpenAI', 'organization')


@verify_config('Mastodon', 'enable_mastodon')
def get_enable_mastodon():
    """Get whether Mastodon integration is enabled from the configuration."""
    return spellbook_config().getboolean('Mastodon', 'enable_mastodon')


@verify_config('Mastodon', 'client_id')
def get_mastodon_client_id():
    """Get the Mastodon client ID from the configuration."""
    return spellbook_config().get('Mastodon', 'client_id')


@verify_config('Mastodon', 'client_secret')
def get_mastodon_client_secret():
    """Get the Mastodon client secret from the configuration."""
    return spellbook_config().get('Mastodon', 'client_secret')


@verify_config('Mastodon', 'access_token')
def get_mastodon_access_token():
    """Get the Mastodon access token from the configuration."""
    return spellbook_config().get('Mastodon', 'access_token')


@verify_config('Mastodon', 'api_base_url')
def get_mastodon_api_base_url():
    """Get the Mastodon API base URL from the configuration."""
    return spellbook_config().get('Mastodon', 'api_base_url')


@verify_config('Nostr', 'enable_nostr')
def get_enable_nostr():
    """Get whether Nostr integration is enabled from the configuration."""
    return spellbook_config().getboolean('Nostr', 'enable_nostr')


@verify_config('Nostr', 'nsec')
def get_nostr_nsec():
    """Get the Nostr private key (nsec) from the configuration."""
    return spellbook_config().get('Nostr', 'nsec')


@verify_config('LLMs', 'enable_oobabooga')
def get_enable_oobabooga():
    """Get whether Oobabooga self-hosted LLM is enabled from the configuration."""
    return spellbook_config().getboolean('LLMs', 'enable_oobabooga')


@verify_config('LLMs', 'default_model')
def get_llms_default_model():
    """Get the default LLM model name from the configuration."""
    return spellbook_config().get('LLMs', 'default_model')

@verify_config('LLMs', 'enable_together_ai')
def get_enable_together_ai():
    """Get whether Together.ai integration is enabled from the configuration."""
    return spellbook_config().getboolean('LLMs', 'enable_together_ai')

@verify_config('LLMs', 'together_ai_bearer_token')
def get_together_ai_bearer_token():
    """Get the Together.ai bearer token from the configuration."""
    return spellbook_config().get('LLMs', 'together_ai_bearer_token')

@verify_config('LLMs', 'openrouter_api_key')
def get_openrouter_api_key():
    """Get the OpenRouter API key from the configuration."""
    return spellbook_config().get('LLMs', 'openrouter_api_key')

@verify_config('Uploads', 'enable_uploads')
def get_enable_uploads():
    """Get whether file uploads are enabled from the configuration."""
    return spellbook_config().getboolean('Uploads', 'enable_uploads')

@verify_config('Uploads', 'uploads_dir')
def get_uploads_dir():
    """Get the uploads directory path from the configuration."""
    return spellbook_config().get('Uploads', 'uploads_dir')

@verify_config('Uploads', 'max_file_size')
def get_max_file_size():
    """Get the maximum upload file size from the configuration."""
    return spellbook_config().getint('Uploads', 'max_file_size')

@verify_config('Uploads', 'allowed_extensions')
def get_allowed_extensions():
    """Get the allowed file extensions for uploads from the configuration."""
    return spellbook_config().get('Uploads', 'allowed_extensions')

@verify_config('Transcribe', 'enable_transcribe')
def get_enable_transcribe():
    """Get whether audio transcription is enabled from the configuration."""
    return spellbook_config().getboolean('Transcribe', 'enable_transcribe')

@verify_config('Transcribe', 'model_size')
def get_model_size_transcribe():
    """Get the transcription model size from the configuration."""
    return spellbook_config().get('Transcribe', 'model_size')

@verify_config('Transcribe', 'max_file_size')
def get_max_file_size_transcribe():
    """Get the maximum transcription file size from the configuration."""
    return spellbook_config().getint('Transcribe', 'max_file_size')

@verify_config('Transcribe', 'allowed_extensions')
def get_allowed_extensions_transcribe():
    """Get the allowed file extensions for transcription from the configuration."""
    return spellbook_config().get('Transcribe', 'allowed_extensions')