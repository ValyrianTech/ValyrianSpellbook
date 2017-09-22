#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import hashlib
import hmac
import base64
import requests
import argparse
from ConfigParser import ConfigParser


# Make sure we are in the correct working directory
os.chdir(os.path.dirname(__file__))

# ----------------------------------------------------------------------------------------------------------------

# Read the RESTAPI configuration file
spellbook_configuration_file = 'configuration/Spellbook.conf'
config = ConfigParser()
config.read(spellbook_configuration_file)

# Check if the spellbook configuration file contains a [RESTAPI] section
if not config.has_section('RESTAPI'):
    raise Exception('Configuration file %s does not have a [RESTAPI] section ' % spellbook_configuration_file)

# Check if the [RESTAPI] section has options for 'host' and 'port'
if not config.has_option('RESTAPI', 'host'):
    raise Exception("Configuration file %s does not have an option 'host' in the [RESTAPI] section" % spellbook_configuration_file)
host = config.get('RESTAPI', 'host')

if not config.has_option('RESTAPI', 'port'):
    raise Exception("Configuration file %s does not have an option 'port' in the [RESTAPI] section" % spellbook_configuration_file)
port = config.get('RESTAPI', 'port')


# Check if the spellbook configuration file contains a [Authentication] section
if not config.has_section('Authentication'):
    raise Exception('Configuration file %s does not have a [Authentication] section ' % spellbook_configuration_file)

# Check if the [Authentication] section has options for 'host' and 'port'
if not config.has_option('Authentication', 'key'):
    raise Exception("Configuration file %s does not have an option 'key' in the [Authentication] section" % spellbook_configuration_file)
key = config.get('Authentication', 'key')

if not config.has_option('Authentication', 'secret'):
    raise Exception("Configuration file %s does not have an option 'secret' in the [Authentication] section" % spellbook_configuration_file)
secret = config.get('Authentication', 'secret')

# ----------------------------------------------------------------------------------------------------------------

# Create main parser
parser = argparse.ArgumentParser(description='Bitcoin spellbook command line interface', formatter_class=argparse.RawDescriptionHelpFormatter)
subparsers = parser.add_subparsers(title='Spellbook subcommands', metavar='', dest='command')


# Create parser for the get_explorers subcommand
get_explorers_parser = subparsers.add_parser(name='get_explorers',
                                             help='Get list of configured explorers',
                                             formatter_class=argparse.RawDescriptionHelpFormatter,
                                             description='''
Get a list of configured explorers
                                             ''',
                                             epilog='''
examples:
  - spellbook.py get_explorers
    -> Get a list of configured explorers
                                             ''')

# Create parser for the save_explorer subcommand
save_explorer_parser = subparsers.add_parser(name='save_explorer',
                                             help='Save or update an explorer in the spellbook',
                                             formatter_class=argparse.RawDescriptionHelpFormatter,
                                             description='''
Save or update an explorer in the spellbook
                                             ''',
                                             epilog='''
examples:
  - spellbook.py save_explorer blocktrail
    -> Save or update an explorer with name 'blocktrail' in the spellbook
  - spellbook.py save_explorer blocktrail --key='ABC123'
    -> Save or update an explorer with name 'blocktrail' and an API-key in the spellbook
                                             ''')

save_explorer_parser.add_argument('name', help='Name of the explorer')
save_explorer_parser.add_argument('-k', '--key', help='API key for the explorer')
save_explorer_parser.add_argument('-u', '--url', help='URL of the explorer')

# Create parser for the get_explorer_config subcommand
get_explorer_config_parser = subparsers.add_parser(name='get_explorer_config',
                                                   help='Get configuration info about a specific explorer',
                                                   formatter_class=argparse.RawDescriptionHelpFormatter,
                                                   description='''
Get configuration info about a specific explorer
                                                   ''',
                                                   epilog='''
examples:
  - spellbook.py get_explorer_config blocktrail
    -> Get configuration info about a specific explorer
                                                   ''')

get_explorer_config_parser.add_argument('name', help='Name of the explorer')
get_explorer_config_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
get_explorer_config_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)


# Create parser for the delete_explorer subcommand
delete_explorer_parser = subparsers.add_parser(name='delete_explorer',
                                               help='Delete a specific explorer',
                                               formatter_class=argparse.RawDescriptionHelpFormatter,
                                               description='''
Delete a specific explorer
                                               ''',
                                               epilog='''
examples:
  - spellbook.py delete_explorer blocktrail
    -> Delete the explorer with id 'blocktrail'
                                               ''')

delete_explorer_parser.add_argument('name', help='Name of the explorer')

# ----------------------------------------------------------------------------------------------------------------


def add_authentication_headers(headers=None, data=''):
    if headers is None:
        headers = {}

    message = hashlib.sha256(data).digest()
    signature = hmac.new(base64.b64decode(args.api_secret), message, hashlib.sha512)

    headers.update({'API_Key': args.api_key,
                    'API_Sign': base64.b64encode(signature.digest())})

    return headers


#############################################
# Bitcoin Spellbook Commands : explorers    #
#############################################


def get_explorers():
    try:
        r = requests.get('http://{host}:{port}/spellbook/explorers'.format(host=host, port=port))
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to get explorers: %s' % ex
        sys.exit(1)


def get_explorer_config():
    try:
        data = ''
        r = requests.get('http://{host}:{port}/spellbook/explorers/{explorer_id}'.format(host=host, port=port, explorer_id=args.name), headers=add_authentication_headers(data=data), data=data)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to get explorer config: %s' % ex
        sys.exit(1)


def save_explorer():
    payload = {'name': args.name,
               'api_key': args.api_key,
               'url': args.url}

    try:
        r = requests.post('http://{host}:{port}/spellbook/explorers/{explorer_id}'.format(host=host, port=port, explorer_id=args.name), data=payload)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to get explorer config: %s' % ex
        sys.exit(1)


def delete_explorer():
    try:
        r = requests.delete('http://{host}:{port}/spellbook/explorers/{explorer_id}'.format(host=host, port=port, explorer_id=args.name))
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to delete explorer: %s' % ex
        sys.exit(1)

# ----------------------------------------------------------------------------------------------------------------

# Parse the command line arguments
args = parser.parse_args()

# Execute the correct command based on the arguments given
if args.command == 'get_explorers':
    get_explorers()
elif args.command == 'get_explorer_config':
    get_explorer_config()
elif args.command == 'save_explorer':
    save_explorer()
elif args.command == 'delete_explorer':
    delete_explorer()

