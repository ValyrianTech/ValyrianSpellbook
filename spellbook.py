#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import requests
import argparse
import time
from ConfigParser import ConfigParser
from authentication import signature


# Make sure we are in the correct working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

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

save_explorer_parser.add_argument('name', help='name of the explorer')
save_explorer_parser.add_argument('type', help='type of the explorer', choices=['Blockchain.info', 'Blocktrail.com', 'Insight'])
save_explorer_parser.add_argument('url', help='URL of the explorer')
save_explorer_parser.add_argument('priority', help='priority of the explorer')
save_explorer_parser.add_argument('-b', '--blocktrail_key', help='API key for the explorer (only needed for blocktrail.com)', default='')
save_explorer_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
save_explorer_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)

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
delete_explorer_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
delete_explorer_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)

# ----------------------------------------------------------------------------------------------------------------

# Create parser for the get_latest_block subcommand
get_latest_block_parser = subparsers.add_parser(name='get_latest_block',
                                                help='Get the latest block',
                                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                                description='''
Get the latest block
                                                ''',
                                                epilog='''
examples:
  - spellbook.py get_latest_block
    -> Get the latest block using the default explorer
  - spellbook.py get_latest_block --explorer=blockchain.info
    -> Get the latest block using the blockchain.info explorer to retrieve the data
                                                ''')

get_latest_block_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')

# Create parser for the get_block subcommand
get_block_parser = subparsers.add_parser(name='get_block',
                                         help='Get a block by height or hash',
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         description='''
Get a block by height or hash
                                         ''',
                                         epilog='''
examples:
  - spellbook.py get_block 488470
    -> Get block 488470 using the default explorer
  - spellbook.py get_block 000000000000000000f6af507822a695390bada30cbd0c517c12442effb277af
    -> Get block 000000000000000000f6af507822a695390bada30cbd0c517c12442effb277af using the default explorer
  - spellbook.py get_block 488470 --explorer=blockchain.info
    -> Get block 488470 using the blockchain.info explorer to retrieve the data
                                         ''')

get_block_parser.add_argument('id', help='The height OR the hash of the block')
get_block_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')


# Create parser for the get_prime_input_address subcommand
get_prime_input_address_parser = subparsers.add_parser(name='get_prime_input_address',
                                                       help='Get the prime input address of a transaction',
                                                       formatter_class=argparse.RawDescriptionHelpFormatter,
                                                       description='''
Get the prime input address of a transaction. This is the input address that comes first alphabetically.
                                                       ''',
                                                       epilog='''
examples:
  - spellbook.py get_prime_input_address 39bb5f5d50882227f93b980df15ea676414f0363770a0174a13c8f55c877b598
    -> Get the prime input address of tx 39bb5f5d50882227f93b980df15ea676414f0363770a0174a13c8f55c877b598 using the default explorer
  - spellbook.py get_prime_input_address 39bb5f5d50882227f93b980df15ea676414f0363770a0174a13c8f55c877b598 --explorer=blockchain.info
    -> Get the prime input address of tx 39bb5f5d50882227f93b980df15ea676414f0363770a0174a13c8f55c877b598 using the blockchain.info explorer to retrieve the data
                                                       ''')

get_prime_input_address_parser.add_argument('txid', help='The txid of the transaction')
get_prime_input_address_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')


# Create parser for the get_transactions subcommand
get_transactions_parser = subparsers.add_parser(name='get_transactions',
                                                help='Get all transactions that a specific address has received or sent',
                                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                                description='''
Get all transactions that a specific address has received or sent.
                                                ''',
                                                epilog='''
examples:
  - spellbook.py get_transactions 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8
    -> Get all transactions of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the default explorer
  - spellbook.py get_transactions 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 --explorer=blockchain.info
    -> Get all transactions of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the blockchain.info explorer to retrieve the data
                                                ''')

get_transactions_parser.add_argument('address', help='The address')
get_transactions_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')


# Create parser for the get_balance subcommand
get_balance_parser = subparsers.add_parser(name='get_balance',
                                           help='Get the current balance of an address',
                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                           description='''
Get the current balance of an address.
                                           ''',
                                           epilog='''
examples:
  - spellbook.py get_balance 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8
    -> Get the balance of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the default explorer
  - spellbook.py get_balance 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 --explorer=blockchain.info
    -> Get the balance of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the blockchain.info explorer to retrieve the data
                                           ''')

get_balance_parser.add_argument('address', help='The address')
get_balance_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')


# Create parser for the get_utxos subcommand
get_utxos_parser = subparsers.add_parser(name='get_utxos',
                                         help='Get the current UTXOs of an address',
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         description='''
Get the UTXOs of an address with at least the specified number of confirmations (default=3).
                                         ''',
                                         epilog='''
examples:
  - spellbook.py get_utxos 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8
    -> Get the UTXOs of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 with at least 3 confirmations using the default explorer
  - spellbook.py get_utxos 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 -c=6
    -> Get the UTXOs of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 with at least 6 confirmations using the default explorer
  - spellbook.py get_utxos 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 --explorer=blockchain.info
    -> Get the UTXOs of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the blockchain.info explorer to retrieve the data
                                         ''')

get_utxos_parser.add_argument('address', help='The address')
get_utxos_parser.add_argument('-c', '--confirmations', help='The number of confirmations required (default=3)', default=3)
get_utxos_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')

# ----------------------------------------------------------------------------------------------------------------


def add_authentication_headers(headers=None, data=None):
    """
    Add custom headers for API_Key and API_Sign
    The data that is sent with the HTTP request is signed with the shared secret of the API key,
    this ensures that the request is made from an authenticated source and the data cannot be modified
    by a man-in-the-middle attack

    :param headers: A dict containing headers (optional)
    :param data: A json string containing the data (optional)
    :return: A dict containing the updated headers
    """
    if headers is None:
        headers = {'Content-Type': 'application/json'}

    nonce = int(time.time())

    headers.update({'API_Key': args.api_key,
                    'API_Sign': signature(data, nonce, args.api_secret),
                    'API_Nonce': str(nonce)})

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
        r = requests.get('http://{host}:{port}/spellbook/explorers/{explorer_id}'.format(host=host, port=port, explorer_id=args.name), headers=add_authentication_headers())
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to get explorer config: %s' % ex
        sys.exit(1)


def save_explorer():
    data = {'type': args.type,
            'api_key': args.blocktrail_key,
            'url': args.url,
            'priority': args.priority}

    try:
        r = requests.post('http://{host}:{port}/spellbook/explorers/{explorer_id}'.format(host=host, port=port, explorer_id=args.name), headers=add_authentication_headers(data=data), json=data)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to get explorer config: %s' % ex
        sys.exit(1)


def delete_explorer():
    try:
        r = requests.delete('http://{host}:{port}/spellbook/explorers/{explorer_id}'.format(host=host, port=port, explorer_id=args.name), headers=add_authentication_headers())
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to delete explorer: %s' % ex
        sys.exit(1)

# ----------------------------------------------------------------------------------------------------------------


def get_latest_block():
    try:
        url = 'http://{host}:{port}/spellbook/blocks/latest'.format(host=host, port=port)
        if args.explorer is not None:
            url += '?explorer={explorer}'.format(explorer=args.explorer)
        r = requests.get(url)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable get latest block: %s' % ex
        sys.exit(1)


def get_block():
    try:
        url = 'http://{host}:{port}/spellbook/blocks/{id}'.format(host=host, port=port, id=args.id)
        if args.explorer is not None:
            url += '?explorer={explorer}'.format(explorer=args.explorer)
        r = requests.get(url)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable get block %s: %s' % (args.id, ex)
        sys.exit(1)


def get_prime_input_address():
    try:
        url = 'http://{host}:{port}/spellbook/prime_input/{txid}'.format(host=host, port=port, txid=args.txid)
        if args.explorer is not None:
            url += '?explorer={explorer}'.format(explorer=args.explorer)
        r = requests.get(url)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable get prime input address of transaction %s: %s' % (args.txid, ex)
        sys.exit(1)


def get_transactions():
    try:
        url = 'http://{host}:{port}/spellbook/transactions/{address}'.format(host=host, port=port, address=args.address)
        if args.explorer is not None:
            url += '?explorer={explorer}'.format(explorer=args.explorer)
        r = requests.get(url)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable get transactions of address %s: %s' % (args.address, ex)
        sys.exit(1)


def get_balance():
    try:
        url = 'http://{host}:{port}/spellbook/balances/{address}'.format(host=host, port=port, address=args.address)
        if args.explorer is not None:
            url += '?explorer={explorer}'.format(explorer=args.explorer)
        r = requests.get(url)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable get balance of address %s: %s' % (args.address, ex)
        sys.exit(1)


def get_utxos():
    try:
        url = 'http://{host}:{port}/spellbook/utxos/{address}?confirmations={confirmations}'.format(host=host, port=port, address=args.address, confirmations=args.confirmations)
        if args.explorer is not None:
            url += '&explorer={explorer}'.format(explorer=args.explorer)
        r = requests.get(url)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable get UTXOs of address %s: %s' % (args.address, ex)
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
elif args.command == 'get_latest_block':
    get_latest_block()
elif args.command == 'get_block':
    get_block()
elif args.command == 'get_prime_input_address':
    get_prime_input_address()
elif args.command == 'get_transactions':
    get_transactions()
elif args.command == 'get_balance':
    get_balance()
elif args.command == 'get_utxos':
    get_utxos()
