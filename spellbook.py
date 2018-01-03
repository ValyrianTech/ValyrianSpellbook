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


# ----------------------------------------------------------------------------------------------------------------

# Create parser for the get_triggers subcommand
get_triggers_parser = subparsers.add_parser(name='get_triggers',
                                            help='Get the list of configured triggers',
                                            formatter_class=argparse.RawDescriptionHelpFormatter,
                                            description='''
Get the list of configured triggers.
                                            ''',
                                            epilog='''
examples:
  - spellbook.py get_triggers
    -> Get the list of all configured triggers
    
  - spellbook.py get_triggers --active
    -> Get the list of active triggers
                                            ''')

get_triggers_parser.add_argument('-a', '--active', help='Only get the triggers that are currently active')

# Create parser for the get_trigger subcommand
get_trigger_config_parser = subparsers.add_parser(name='get_trigger_config',
                                                  help='Get the configuration of specified trigger',
                                                  formatter_class=argparse.RawDescriptionHelpFormatter,
                                                  description='''
Get the configuration of specified trigger.
                                           ''',
                                                  epilog='''
examples:
  - spellbook.py get_trigger_config mytrigger
    -> Get the configuration of the trigger with id 'mytrigger'

                                           ''')

get_trigger_config_parser.add_argument('trigger_id', help='The id of the trigger')
get_trigger_config_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
get_trigger_config_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)


# Create parser for the save_trigger subcommand
save_trigger_parser = subparsers.add_parser(name='save_trigger',
                                            help='Save or update the configuration of a trigger',
                                            formatter_class=argparse.RawDescriptionHelpFormatter,
                                            description='''
Save or update the configuration of a trigger.
                                            ''',
                                            epilog='''
examples:
  - spellbook.py save_trigger mytrigger --reset
   -> Reset the trigger with id mytrigger in case it has been triggered already

  - spellbook.py save_trigger mytrigger -t=Balance
    -> Save or update a trigger with id 'mytrigger' of type 'Balance'

  - spellbook.py save_trigger mytrigger -d='A short description'
    -> Save or update a trigger with id 'mytrigger' with a description
                                            ''')

save_trigger_parser.add_argument('trigger_id', help='The id of the trigger')
save_trigger_parser.add_argument('-r', '--reset', help='Reset the trigger in case it has been triggered already', action='store_true')
save_trigger_parser.add_argument('-t', '--type', help='The type of the trigger', choices=['Manual', 'Balance', 'Received', 'Sent', 'Block_height'])
save_trigger_parser.add_argument('-a', '--address', help='The address to check the final balance, total received or total sent')
save_trigger_parser.add_argument('-am', '--amount', help='The amount', type=int)
save_trigger_parser.add_argument('-c', '--confirmations', help='The number of confirmations before the trigger is activated', default=3, type=int)
save_trigger_parser.add_argument('-b', '--block_height', help='The block height at which the trigger will be activated', type=int)
save_trigger_parser.add_argument('-d', '--description', help='A description of the trigger')
save_trigger_parser.add_argument('-cn', '--creator_name', help='The name of the creator the trigger')
save_trigger_parser.add_argument('-ce', '--creator_email', help='The email of the creator of the trigger')
save_trigger_parser.add_argument('-y', '--youtube', help='A video on youtube belonging to the trigger')
save_trigger_parser.add_argument('-v', '--visibility', help='The visibility of the trigger (Public or Private)', choices=['Public', 'Private'])
save_trigger_parser.add_argument('-st', '--status', help='The status of the trigger (Pending, Active or Disabled)', choices=['Pending', 'Active', 'Disabled'])
save_trigger_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
save_trigger_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)


# Create parser for the delete_trigger subcommand
delete_trigger_parser = subparsers.add_parser(name='delete_trigger',
                                              help='Delete a specified trigger',
                                              formatter_class=argparse.RawDescriptionHelpFormatter,
                                              description='''
Delete a specified trigger.
                                              ''',
                                              epilog='''
examples:
  - spellbook.py delete_trigger mytrigger
    -> Delete the trigger with id 'mytrigger'

                                              ''')

delete_trigger_parser.add_argument('trigger_id', help='The id of the trigger to delete')
delete_trigger_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
delete_trigger_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)


# Create parser for the activate_trigger subcommand
activate_trigger_parser = subparsers.add_parser(name='activate_trigger',
                                                help='Activate a specified manual trigger',
                                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                                description='''
Activate a specified manual trigger.
The trigger must be of type 'Manual'
                                                ''',
                                                epilog='''
examples:
  - spellbook.py activate_trigger mytrigger
    -> Activate the trigger with id 'mytrigger'

                                                ''')

activate_trigger_parser.add_argument('trigger_id', help='The id of the trigger to activate')
activate_trigger_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
activate_trigger_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)


# Create parser for the check_triggers subcommand
check_triggers_parser = subparsers.add_parser(name='check_triggers',
                                              help='Check a triggers and activate it them if conditions have been fulfilled',
                                              formatter_class=argparse.RawDescriptionHelpFormatter,
                                              description='''
Check triggers and activate it them if conditions have been fulfilled
                                             ''',
                                              epilog='''
examples:
  - spellbook.py check_triggers mytrigger
    -> Check the trigger with id 'mytrigger' and activate it if conditions have been fulfilled

                                             ''')

check_triggers_parser.add_argument('trigger_id', help='The id of the trigger to check', nargs='?')
check_triggers_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')
check_triggers_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
check_triggers_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)

# ----------------------------------------------------------------------------------------------------------------

# Create parser for the get_actions subcommand
get_actions_parser = subparsers.add_parser(name='get_actions',
                                           help='Get the list of configured action_ids',
                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                           description='''
Get the list of configured action_ids.
                                           ''',
                                           epilog='''
examples:
  - spellbook.py get_actions
    -> Get the list of all configured action_ids

  - spellbook.py get_actions --trigger_id=mytrigger
    -> Get the list of all configured action_ids on trigger 'mytrigger'
                                           ''')

get_actions_parser.add_argument('-i', '--trigger_id', help='The id of the trigger')


# Create parser for the get_action_config subcommand
get_action_config_parser = subparsers.add_parser(name='get_action_config',
                                                 help='Get the configuration of specified action',
                                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                                 description='''
Get the configuration of specified action.
                                                 ''',
                                                 epilog='''
examples:
  - spellbook.py get_action_config myaction
    -> Get the configuration of the action 'myaction'

                                                 ''')

get_action_config_parser.add_argument('action_id', help='The id of the action')
get_action_config_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
get_action_config_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)


# Create parser for the save_action subcommand
save_action_parser = subparsers.add_parser(name='save_action',
                                           help='Save or update the configuration of an action',
                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                           description='''
Save or update the configuration of an action.
                                           ''',
                                           epilog='''
examples:
  - spellbook.py save_trigger myaction
   -> Save an action with id 'myaction'

  - spellbook.py save_trigger myaction -t=Command -c='ping 127.0.0.1'
   -> Save an action with id 'myaction' that runs the ping command when run

  - spellbook.py save_trigger myaction -t=SendMail -mr=info@valyrian.tech -ms='email subject' -mb=template1
   -> Save an action with id 'myaction' that sends an email to info@valyrian.tech with subject 'email subject' and uses template1 for the body
                                           ''')

save_action_parser.add_argument('action_id', help='The id of the action')
save_action_parser.add_argument('-t', '--type', help='The type of the action', choices=['Command', 'Distributer', 'Forwarder', 'OpReturnWriter', 'RevealLink', 'RevealText', 'SendMail', 'Webhook'])

save_action_parser.add_argument('-c', '--run_command', help='The command to run, only applicable to Command Actions')

save_action_parser.add_argument('-mr', '--mail_recipients', help='The recipients of the email in a SendEmail Action, separated with semicolon')
save_action_parser.add_argument('-ms', '--mail_subject', help='The subject of the email in a SendEmail Action')
save_action_parser.add_argument('-mb', '--mail_body_template', help='The name of the body template of the email in a SendEmail Action')

save_action_parser.add_argument('-w', '--webhook', help='The url of a webhook, only applicable to Webhook Actions')

save_action_parser.add_argument('-rt', '--reveal_text', help='The text to reveal when the action is activated, only applicable to RevealText Actions')
save_action_parser.add_argument('-rl', '--reveal_link', help='The link to reveal when the action is activated, only applicable to RevealText Actions and RevealLink Actions')

save_action_parser.add_argument('-fa', '--fee_address', help='The address to send the fee to')
save_action_parser.add_argument('-fp', '--fee_percentage', help='The fee as a percentage', type=float)

save_action_parser.add_argument('-ks', '--key_source', help='The source of the private key for the sending address (PrivKey or BIP44)', choices=['PrivKey', 'BIP44'])
save_action_parser.add_argument('-pk', '--priv_key', help='The private key of the sending address')
save_action_parser.add_argument('-ba', '--bip44_account', help='The account in a BIP44 wallet', type=int)
save_action_parser.add_argument('-bi', '--bip44_index', help='The index in a BIP44 wallet of the sending address', type=int)

save_action_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
save_action_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)

# Create parser for the delete_action subcommand
delete_action_parser = subparsers.add_parser(name='delete_action',
                                             help='Delete a specified action',
                                             formatter_class=argparse.RawDescriptionHelpFormatter,
                                             description='''
Delete a specified action.
                                             ''',
                                             epilog='''
examples:
  - spellbook.py delete_action myaction
    -> Delete the action with id 'myaction'

                                             ''')

delete_action_parser.add_argument('action_id', help='The id of the action')
delete_action_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
delete_action_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)


# Create parser for the run_action subcommand
run_action_parser = subparsers.add_parser(name='run_action',
                                          help='Run a specified action',
                                          formatter_class=argparse.RawDescriptionHelpFormatter,
                                          description='''
Run a specified action.
                                          ''',
                                          epilog='''
examples:
  - spellbook.py run_action myaction
    -> Run the action with id 'myaction'

                                          ''')

run_action_parser.add_argument('action_id', help='The id of the action')
run_action_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
run_action_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)


# Create parser for the get_reveal subcommand
get_reveal_parser = subparsers.add_parser(name='get_reveal',
                                          help='Get the reveal text or link from a RevealText or RevealLink action',
                                          formatter_class=argparse.RawDescriptionHelpFormatter,
                                          description='''
Get the reveal text or link from a RevealText or RevealLink action.
                                          ''',
                                          epilog='''
examples:
  - spellbook.py get_reveal myaction
    -> Get the reveal text or link of the action with id 'myaction'

                                          ''')

get_reveal_parser.add_argument('action_id', help='The id of the action')
get_reveal_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
get_reveal_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)


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

    nonce = int(round(time.time() * 1000))

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
# Triggers
# ----------------------------------------------------------------------------------------------------------------


def get_triggers():
    try:
        r = requests.get('http://{host}:{port}/spellbook/triggers'.format(host=host, port=port))
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to get triggers: %s' % ex
        sys.exit(1)


def get_trigger():
    try:
        r = requests.get('http://{host}:{port}/spellbook/triggers/{trigger_id}'.format(host=host, port=port, trigger_id=args.trigger_id), headers=add_authentication_headers())
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to get trigger config: %s' % ex
        sys.exit(1)


def save_trigger():
    data = {}
    if args.type is not None:
        data['trigger_type'] = args.type

    if args.address is not None:
        data['address'] = args.address

    if args.amount is not None:
        data['amount'] = args.amount

    if args.confirmations is not None:
        data['confirmations'] = args.confirmations

    if args.block_height is not None:
        data['block_height'] = args.block_height

    if args.reset is not None:
        data['reset'] = True

    if args.description is not None:
        data['description'] = args.description

    if args.creator_name is not None:
        data['creator_name'] = args.creator_name

    if args.creator_email is not None:
        data['creator_email'] = args.creator_email

    if args.youtube is not None:
        data['youtube'] = args.youtube

    if args.visibility is not None:
        data['visibility'] = args.visibility

    if args.status is not None:
        data['status'] = args.status

    try:
        r = requests.post('http://{host}:{port}/spellbook/triggers/{trigger_id}'.format(host=host, port=port, trigger_id=args.trigger_id), headers=add_authentication_headers(data=data), json=data)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to get explorer config: %s' % ex
        sys.exit(1)


def delete_trigger():
    try:
        r = requests.delete('http://{host}:{port}/spellbook/triggers/{trigger_id}'.format(host=host, port=port, trigger_id=args.trigger_id), headers=add_authentication_headers())
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to delete trigger: %s' % ex
        sys.exit(1)


def activate_trigger():
    try:
        r = requests.get('http://{host}:{port}/spellbook/triggers/{trigger_id}/activate'.format(host=host, port=port, trigger_id=args.trigger_id), headers=add_authentication_headers())
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to activate trigger: %s' % ex
        sys.exit(1)


def check_triggers():
    if args.trigger_id is not None:
        url = 'http://{host}:{port}/spellbook/triggers/{trigger_id}/check'.format(host=host, port=port, trigger_id=args.trigger_id)
    else:
        url = 'http://{host}:{port}/spellbook/check_triggers'.format(host=host, port=port)

    if args.explorer is not None:
        url += '?explorer={explorer}'.format(explorer=args.explorer)

    try:
        r = requests.get(url, headers=add_authentication_headers())
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to check triggers: %s' % ex
        sys.exit(1)

# ----------------------------------------------------------------------------------------------------------------
# Actions
# ----------------------------------------------------------------------------------------------------------------


def get_actions():
    try:
        r = requests.get('http://{host}:{port}/spellbook/actions'.format(host=host, port=port))
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to get actions: %s' % ex
        sys.exit(1)


def get_action():
    try:
        r = requests.get('http://{host}:{port}/spellbook/actions/{action_id}'.format(host=host, port=port, action_id=args.action_id), headers=add_authentication_headers())
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to get action config: %s' % ex
        sys.exit(1)


def save_action():
    data = {}
    if args.type is not None:
        data['action_type'] = args.type

    if args.run_command is not None:
        data['run_command'] = args.run_command

    if args.mail_recipients is not None:
        data['mail_recipients'] = args.mail_recipients

    if args.mail_subject is not None:
        data['mail_subject'] = args.mail_subject

    if args.mail_body_template is not None:
        data['mail_body_template'] = args.mail_body_template

    if args.webhook is not None:
        data['webhook'] = args.webhook

    if args.reveal_text is not None:
        data['reveal_text'] = args.reveal_text

    if args.reveal_link is not None:
        data['reveal_link'] = args.reveal_link

    if args.fee_address is not None:
        data['fee_address'] = args.fee_address

    if args.fee_percentage is not None:
        data['fee_percentage'] = args.fee_percentage

    if args.key_source is not None:
        data['key_source'] = args.key_source

    if args.priv_key is not None:
        data['priv_key'] = args.priv_key

    if args.bip44_account is not None:
        data['bip44_account'] = args.bip44_account

    if args.bip44_index is not None:
        data['bip44_index'] = args.bip44_index

    try:
        r = requests.post('http://{host}:{port}/spellbook/actions/{action_id}'.format(host=host,
                                                                                      port=port,
                                                                                      action_id=args.action_id),
                          headers=add_authentication_headers(data=data),
                          json=data)
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to save action config: %s' % ex
        sys.exit(1)


def delete_action():
    try:
        r = requests.delete('http://{host}:{port}/spellbook/actions/{action_id}'.format(host=host,
                                                                                        port=port,
                                                                                        action_id=args.action_id),
                            headers=add_authentication_headers())
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to delete action: %s' % ex
        sys.exit(1)


def run_action():
    try:
        r = requests.get('http://{host}:{port}/spellbook/actions/{action_id}/run'.format(host=host, port=port, action_id=args.action_id), headers=add_authentication_headers())
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to run action: %s' % ex
        sys.exit(1)


def get_reveal():
    try:
        r = requests.get('http://{host}:{port}/spellbook/actions/{action_id}/reveal'.format(host=host, port=port, action_id=args.action_id))
        print r.text
    except Exception as ex:
        print >> sys.stderr, 'Unable to get revealed text or link: %s' % ex
        sys.exit(1)

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
elif args.command == 'get_triggers':
    get_triggers()
elif args.command == 'get_trigger_config':
    get_trigger()
elif args.command == 'save_trigger':
    save_trigger()
elif args.command == 'delete_trigger':
    delete_trigger()
elif args.command == 'activate_trigger':
    activate_trigger()
elif args.command == 'check_triggers':
    check_triggers()
elif args.command == 'get_actions':
    get_actions()
elif args.command == 'get_action_config':
    get_action()
elif args.command == 'save_action':
    save_action()
elif args.command == 'delete_action':
    delete_action()
elif args.command == 'run_action':
    run_action()
elif args.command == 'get_reveal':
    get_reveal()