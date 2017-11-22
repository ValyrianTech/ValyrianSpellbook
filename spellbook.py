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

# ----------------------------------------------------------------------------------------------------------------------

# Create parser for the get_sil subcommand
get_lal_parser = subparsers.add_parser(name='get_sil',
                                       help='Get the Simplified Inputs List (SIL) of an address',
                                       formatter_class=argparse.RawDescriptionHelpFormatter,
                                       description='''
Get the Simplified Inputs List (SIL) of an address.
                                       ''',
                                       epilog='''
examples:
  - spellbook.py get_sil 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8
    -> Get the SIL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the default explorer
  - spellbook.py get_sil 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 -b=478000
    -> Get the SIL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 at block height 478000 using the default explorer
  - spellbook.py get_sil 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 --explorer=blockchain.info
    -> Get the SIL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the blockchain.info explorer to retrieve the data
                                       ''')

get_lal_parser.add_argument('address', help='The address')
get_lal_parser.add_argument('-b', '--block_height', help='The block height for the SIL (optional, default=latest block)', default=0)
get_lal_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')


# Create parser for the get_profile subcommand
get_profile_parser = subparsers.add_parser(name='get_profile',
                                           help='Get the profile of an address',
                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                           description='''
Get the profile of an address.
                                           ''',
                                           epilog='''
examples:
  - spellbook.py get_profile 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8
    -> Get the profile of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the default explorer
  - spellbook.py get_profile 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 -b=478000
    -> Get the profile of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 at block height 478000 using the default explorer
  - spellbook.py get_profile 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 --explorer=blockchain.info
    -> Get the profile of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the blockchain.info explorer to retrieve the data
                                           ''')

get_profile_parser.add_argument('address', help='The address')
get_profile_parser.add_argument('-b', '--block_height', help='The block height for the profile (optional, default=latest block)', default=0)
get_profile_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')

# ----------------------------------------------------------------------------------------------------------------

# Create parser for the get_lal subcommand
get_lal_parser = subparsers.add_parser(name='get_lal',
                                       help='Get the Linked Address List (LAL) of an address and an xpub key',
                                       formatter_class=argparse.RawDescriptionHelpFormatter,
                                       description='''
Get the Linked Address List (LAL) of an address and an xpub key.
                                       ''',
                                       epilog='''
examples:
  - spellbook.py get_lal 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD
    -> Get the LAL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 with xpub key xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD using the default explorer
  
  - spellbook.py get_lal 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD -b=478000
    -> Get the LAL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 with xpub key xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD at block height 478000 using the default explorer
  
  - spellbook.py get_lal 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD --explorer=blockchain.info
    -> Get the LAL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 with xpub key xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD using the blockchain.info explorer to retrieve the data
                                       ''')

get_lal_parser.add_argument('address', help='The address')
get_lal_parser.add_argument('xpub', help='The xpub key')
get_lal_parser.add_argument('-b', '--block_height', help='The block height for the SIL to link with the corresponding address from the xpub (optional, default=latest block)', default=0)
get_lal_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')


# Create parser for the get_lbl subcommand
get_lbl_parser = subparsers.add_parser(name='get_lbl',
                                       help='Get the Linked Balance List (LBL) of an address and an xpub key',
                                       formatter_class=argparse.RawDescriptionHelpFormatter,
                                       description='''
Get the Linked Balance List (LBL) of an address and an xpub key.
                                       ''',
                                       epilog='''
examples:
  - spellbook.py get_lbl 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD
    -> Get the LBL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 with xpub key xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD using the default explorer
  
  - spellbook.py get_lbl 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD -b=478000
    -> Get the LBL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 with xpub key xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD at block height 478000 using the default explorer
  
  - spellbook.py get_lbl 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD --explorer=blockchain.info
    -> Get the LBL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 with xpub key xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD using the blockchain.info explorer to retrieve the data
                                       ''')

get_lbl_parser.add_argument('address', help='The address')
get_lbl_parser.add_argument('xpub', help='The xpub key')
get_lbl_parser.add_argument('-b', '--block_height', help='The block height for the SIL to link with the corresponding address from the xpub (optional, default=latest block)', default=0)
get_lbl_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')


# Create parser for the get_lrl subcommand
get_lbl_parser = subparsers.add_parser(name='get_lrl',
                                       help='Get the Linked Received List (LRL) of an address and an xpub key',
                                       formatter_class=argparse.RawDescriptionHelpFormatter,
                                       description='''
Get the Linked Received List (LRL) of an address and an xpub key.
                                       ''',
                                       epilog='''
examples:
  - spellbook.py get_lrl 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD
    -> Get the LRL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 with xpub key xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD using the default explorer
  
  - spellbook.py get_lrl 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD -b=478000
    -> Get the LRL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 with xpub key xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD at block height 478000 using the default explorer
  
  - spellbook.py get_lrl 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD --explorer=blockchain.info
    -> Get the LRL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 with xpub key xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD using the blockchain.info explorer to retrieve the data
                                       ''')

get_lbl_parser.add_argument('address', help='The address')
get_lbl_parser.add_argument('xpub', help='The xpub key')
get_lbl_parser.add_argument('-b', '--block_height', help='The block height for the SIL to link with the corresponding address from the xpub (optional, default=latest block)', default=0)
get_lbl_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')


# Create parser for the get_lsl subcommand
get_lbl_parser = subparsers.add_parser(name='get_lsl',
                                       help='Get the Linked Sent List (LSL) of an address and an xpub key',
                                       formatter_class=argparse.RawDescriptionHelpFormatter,
                                       description='''
Get the Linked Sent List (LSL) of an address and an xpub key.
                                       ''',
                                       epilog='''
examples:
  - spellbook.py get_lsl 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD
    -> Get the LSL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 with xpub key xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD using the default explorer
  
  - spellbook.py get_lsl 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD -b=478000
    -> Get the LSL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 with xpub key xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD at block height 478000 using the default explorer
  
  - spellbook.py get_lsl 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD --explorer=blockchain.info
    -> Get the LSL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 with xpub key xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD using the blockchain.info explorer to retrieve the data
                                       ''')

get_lbl_parser.add_argument('address', help='The address')
get_lbl_parser.add_argument('xpub', help='The xpub key')
get_lbl_parser.add_argument('-b', '--block_height', help='The block height for the SIL to link with the corresponding address from the xpub (optional, default=latest block)', default=0)
get_lbl_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')


# ----------------------------------------------------------------------------------------------------------------

# Create parser for the get_random_address subcommand
get_random_address_parser = subparsers.add_parser(name='get_random_address',
                                                  help='Get a random address from SIL, LBL, LRL or LSL where the chance of an address being picked is proportional to its value in the list',
                                                  formatter_class=argparse.RawDescriptionHelpFormatter,
                                                  description='''
Get a random address from SIL, LBL, LRL or LSL where the chance of an address being picked is proportional to its value in the list.
                                                  ''',
                                                  epilog='''
examples:
  - spellbook.py get_random_address SIL 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 480000
    -> Get a random address from the SIL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the blockhash of block 480000 as a random number
    
  - spellbook.py get_random_address SIL 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 480000 --block_height=450000
    -> Get a random address from the SIL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 at block 450000 using the blockhash of block 480000 as a random number

  - spellbook.py get_random_address LBL 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 480000 --xpub=xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD
    -> Get a random address from the LBL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 with given xpub key using the blockhash of block 480000 as a random number                                                 ''')

get_random_address_parser.add_argument('source', help='The source of the distribution (SIL, LBL, LRL or LSL)', choices=['SIL', 'LBL', 'LRL', 'LSL'])
get_random_address_parser.add_argument('address', help='The address')
get_random_address_parser.add_argument('rng_block_height', help='The block height of which the blockhash will be used as a random number')
get_random_address_parser.add_argument('-x', '--xpub', help='The xpub key (needed for LBL, LRL and LSL)')
get_random_address_parser.add_argument('-b', '--block_height', help='The block height for the SIL to link with the corresponding address from the xpub (optional, default=latest block)', default=0)
get_random_address_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')


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
        url = 'http://{host}:{port}/spellbook/transactions/{txid}/prime_input'.format(host=host, port=port, txid=args.txid)
        if args.explorer is not None:
            url += '?explorer={explorer}'.format(explorer=args.explorer)
        r = requests.get(url)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable get prime input address of transaction %s: %s' % (args.txid, ex)
        sys.exit(1)


def get_transactions():
    try:
        url = 'http://{host}:{port}/spellbook/addresses/{address}/transactions'.format(host=host, port=port, address=args.address)
        if args.explorer is not None:
            url += '?explorer={explorer}'.format(explorer=args.explorer)
        r = requests.get(url)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable get transactions of address %s: %s' % (args.address, ex)
        sys.exit(1)


def get_balance():
    try:
        url = 'http://{host}:{port}/spellbook/addresses/{address}/balance'.format(host=host, port=port, address=args.address)
        if args.explorer is not None:
            url += '?explorer={explorer}'.format(explorer=args.explorer)
        r = requests.get(url)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable get balance of address %s: %s' % (args.address, ex)
        sys.exit(1)


def get_utxos():
    try:
        url = 'http://{host}:{port}/spellbook/addresses/{address}/utxos?confirmations={confirmations}'.format(host=host, port=port, address=args.address, confirmations=args.confirmations)
        if args.explorer is not None:
            url += '&explorer={explorer}'.format(explorer=args.explorer)
        r = requests.get(url)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable get UTXOs of address %s: %s' % (args.address, ex)
        sys.exit(1)

# ----------------------------------------------------------------------------------------------------------------


def get_sil():
    data = {'block_height': args.block_height}

    try:
        url = 'http://{host}:{port}/spellbook/addresses/{address}/SIL'.format(host=host, port=port, address=args.address)
        if args.explorer is not None:
            url += '?explorer={explorer}'.format(explorer=args.explorer)
        r = requests.get(url, json=data)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to get SIL: %s' % ex
        sys.exit(1)


def get_profile():
    data = {'block_height': args.block_height}

    try:
        url = 'http://{host}:{port}/spellbook/addresses/{address}/profile'.format(host=host, port=port, address=args.address)
        if args.explorer is not None:
            url += '?explorer={explorer}'.format(explorer=args.explorer)
        r = requests.get(url, json=data)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to get profile: %s' % ex
        sys.exit(1)

# ----------------------------------------------------------------------------------------------------------------


def get_lal():
    data = {'block_height': args.block_height,
            'xpub': args.xpub}

    try:
        url = 'http://{host}:{port}/spellbook/addresses/{address}/LAL'.format(host=host, port=port, address=args.address)
        if args.explorer is not None:
            url += '?explorer={explorer}'.format(explorer=args.explorer)
        r = requests.get(url, json=data)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to get LAL: %s' % ex
        sys.exit(1)


def get_lbl():
    data = {'block_height': args.block_height,
            'xpub': args.xpub}

    try:
        url = 'http://{host}:{port}/spellbook/addresses/{address}/LBL'.format(host=host, port=port, address=args.address)
        if args.explorer is not None:
            url += '?explorer={explorer}'.format(explorer=args.explorer)
        r = requests.get(url, json=data)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to get LBL: %s' % ex
        sys.exit(1)


def get_lrl():
    data = {'block_height': args.block_height,
            'xpub': args.xpub}

    try:
        url = 'http://{host}:{port}/spellbook/addresses/{address}/LRL'.format(host=host, port=port, address=args.address)
        if args.explorer is not None:
            url += '?explorer={explorer}'.format(explorer=args.explorer)
        r = requests.get(url, json=data)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to get LRL: %s' % ex
        sys.exit(1)


def get_lsl():
    data = {'block_height': args.block_height,
            'xpub': args.xpub}

    try:
        url = 'http://{host}:{port}/spellbook/addresses/{address}/LSL'.format(host=host, port=port, address=args.address)
        if args.explorer is not None:
            url += '?explorer={explorer}'.format(explorer=args.explorer)
        r = requests.get(url, json=data)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to get LSL: %s' % ex
        sys.exit(1)

# ----------------------------------------------------------------------------------------------------------------


def get_random_address():
    data = {'rng_block_height': args.rng_block_height,
            'sil_block_height': args.block_height,
            'xpub': args.xpub}

    try:
        url = 'http://{host}:{port}/spellbook/addresses/{address}/random/{source}'.format(host=host, port=port, address=args.address, source=args.source)
        if args.explorer is not None:
            url += '?explorer={explorer}'.format(explorer=args.explorer)
        r = requests.get(url, json=data)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to get random address: %s' % ex
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
elif args.command == 'get_sil':
    get_sil()
elif args.command == 'get_profile':
    get_profile()
elif args.command == 'get_lal':
    get_lal()
elif args.command == 'get_lbl':
    get_lbl()
elif args.command == 'get_lrl':
    get_lrl()
elif args.command == 'get_lsl':
    get_lsl()
elif args.command == 'get_random_address':
    get_random_address()
