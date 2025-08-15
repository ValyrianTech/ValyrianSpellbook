#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import argparse
import simplejson
import getpass

from helpers.configurationhelpers import get_use_testnet
from helpers.privatekeyhelpers import privkey_to_address
from AESCipher import AESCipher
from configparser import ConfigParser
from pprint import pprint


# Make sure we are in the correct working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Read the spellbook configuration file
spellbook_configuration_file = 'configuration/spellbook.conf'
config = ConfigParser()
config.read(spellbook_configuration_file)

# Check if the spellbook configuration file contains a [Wallet] section
if not config.has_section('Wallet'):
    raise Exception('Configuration file %s does not have a [Wallet] section ' % spellbook_configuration_file)

# Check if the [Wallet] section has options for 'wallet_dir' and 'default_wallet'
if not config.has_option('Wallet', 'wallet_dir'):
    raise Exception(
        "Configuration file %s does not have an option 'wallet_dir' in the [Wallet] section" % spellbook_configuration_file)
WALLET_DIR = config.get('Wallet', 'wallet_dir')

if not config.has_option('Wallet', 'default_wallet'):
    raise Exception(
        "Configuration file %s does not have an option 'default_wallet' in the [Wallet] section" % spellbook_configuration_file)
WALLET_ID = config.get('Wallet', 'default_wallet')

# ----------------------------------------------------------------------------------------------------------------

# Create main parser
parser = argparse.ArgumentParser(description='Hot wallet command line interface',
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
subparsers = parser.add_subparsers(title='Hot wallet subcommands', metavar='', dest='command')

# Create parser for the add_key subcommand
add_key_parser = subparsers.add_parser(name='add_key',
                                       help='Add a private key to the hot wallet',
                                       formatter_class=argparse.RawDescriptionHelpFormatter,
                                       description='''
Add a private key to the hot wallet
                                       ''',
                                       epilog='''
examples:
  - hot_wallet.py add_key 5myprivatekey54989
    -> add a private key to the default hot wallet
  - hot_wallet.py add_key 5myprivatekey54989 -w=mywallet
    -> add a private key to the hot wallet named 'mywallet'
  - hot_wallet.py add_key 5myprivatekey54989 -w=mywallet --wallet-password=mypassword
    -> add a private key to the hot wallet named 'mywallet' with password 'mypassword'
                                       ''')

add_key_parser.add_argument('private_key', help='The private key')
add_key_parser.add_argument('-w', '--wallet', help='name of the hot wallet')
add_key_parser.add_argument('--wallet-password', help='password for wallet encryption/decryption (if not provided, will prompt interactively)')

# Create parser for the delete_key subcommand
delete_key_parser = subparsers.add_parser(name='delete_key',
                                          help='Delete the private key belonging to the given address from the hot wallet',
                                          formatter_class=argparse.RawDescriptionHelpFormatter,
                                          description='''
Delete the private key belonging to the given address from the hot wallet.
                                          ''',
                                          epilog='''
examples:
  - hot_wallet.py delete_key 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8
    -> delete the private key belonging to address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 from the default hot wallet
  - hot_wallet.py delete_key 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 -w=mywallet
    -> delete the private key belonging to address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 from the hot wallet named 'mywallet'
  - hot_wallet.py delete_key 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 -w=mywallet --wallet-password=mypassword
    -> delete the private key belonging to address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 from the hot wallet named 'mywallet' with password 'mypassword'
                                          ''')

delete_key_parser.add_argument('address', help='The address')
delete_key_parser.add_argument('-w', '--wallet', help='name of the hot wallet')
delete_key_parser.add_argument('--wallet-password', help='password for wallet encryption/decryption (if not provided, will prompt interactively)')

# Create parser for the set_bip44 subcommand
set_bip44_parser = subparsers.add_parser(name='set_bip44',
                                         help='Set the BIP44 mnemonic and passphrase for a hot wallet',
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         description='''
Set the BIP44 mnemonic and passphrase for a hot wallet
                                         ''',
                                         epilog='''
examples:
  - hot_wallet.py set_bip44 bench cabin ...
    -> set the 12 or 24 mnemonic words for the default hot wallet

  - hot_wallet.py set_bip44 bench cabin ... -p=mysecretpassword
    -> set the 12 or 24 mnemonic words for the default hot wallet with an additional passphrase

  - hot_wallet.py set_bip44 bench cabin ... -w=mywallet
    -> set the 12 or 24 mnemonic words for the hot wallet with id 'mywallet'

  - hot_wallet.py set_bip44 bench cabin ... -w=mywallet --wallet-password=mypassword
    -> set the 12 or 24 mnemonic words for the hot wallet with id 'mywallet' with password 'mypassword'
                                         ''')

set_bip44_parser.add_argument('mnemonic', help='The mnemonic of the BIP44 wallet (12 or 24 words)', nargs='+')
set_bip44_parser.add_argument('-p', '--passphrase', help='The passphrase of the BIP44 wallet (optional)')
set_bip44_parser.add_argument('-w', '--wallet', help='name of the hot wallet')
set_bip44_parser.add_argument('--wallet-password', help='password for wallet encryption/decryption (if not provided, will prompt interactively)')

# Create parser for the show subcommand
show_parser = subparsers.add_parser(name='show',
                                    help='Show the private keys and/or mnemonic of a hot wallet',
                                    formatter_class=argparse.RawDescriptionHelpFormatter,
                                    description='''
Show the private keys and/or mnemonic of a hot wallet
                                    ''',
                                    epilog='''
examples:
  - hot_wallet.py show -w=mywallet
    -> show the private keys and/or mnemonic for the hot wallet with id 'mywallet'
  - hot_wallet.py show -w=mywallet --wallet-password=mypassword
    -> show the private keys and/or mnemonic for the hot wallet with id 'mywallet' with password 'mypassword'
                                    ''')

show_parser.add_argument('-w', '--wallet', help='name of the hot wallet')
show_parser.add_argument('--wallet-password', help='password for wallet encryption/decryption (if not provided, will prompt interactively')


# ----------------------------------------------------------------------------------------------------------------

def load_wallet():
    global WALLET_ID
    if args.wallet is not None:
        WALLET_ID = args.wallet

    if not os.path.isfile(os.path.join(WALLET_DIR, '%s.enc' % WALLET_ID)):
        return {}

    if args.wallet_password is not None:
        cipher = AESCipher(key=args.wallet_password)
    else:
        cipher = AESCipher(key=getpass.getpass('Enter the password to decrypt the hot wallet: '))

    try:
        with open(os.path.join(WALLET_DIR, '%s.enc' % WALLET_ID), 'r') as input_file:
            encrypted_data = input_file.read()
            return simplejson.loads(cipher.decrypt(encrypted_data))

    except IOError as ex:
        print('Unable to load encrypted wallet: %s' % ex, file=sys.stderr)
        sys.exit(1)
    except Exception as ex:
        print('Unable to decrypt wallet: %s' % ex, file=sys.stderr)
        sys.exit(1)


def save_wallet(wallet):
    if args.wallet_password is not None:
        password1 = args.wallet_password
        password2 = args.wallet_password
    else:
        password1 = getpass.getpass('Enter the password to encrypt the hot wallet: ')
        password2 = getpass.getpass('Re-enter the password to encrypt the hot wallet: ')

    if password1 != password2:
        print('Passwords do not match!', file=sys.stderr)
        sys.exit(1)

    cipher = AESCipher(key=password1)
    unencrypted_data = bytes(simplejson.dumps(wallet, sort_keys=True, indent=4), 'utf-8')

    with open(os.path.join(WALLET_DIR, '%s.enc' % WALLET_ID), 'w') as output_file:
        output_file.write(str(cipher.encrypt(unencrypted_data), 'utf-8'))


def add_key():
    wallet = load_wallet()

    try:
        address = privkey_to_address(args.private_key, magicbyte=0 if get_use_testnet() is False else 111)
    except AssertionError:
        print('Invalid private key: %s' % args.private_key, file=sys.stderr)
        sys.exit(1)

    new_key = {address: args.private_key}
    wallet.update(new_key)

    save_wallet(wallet)


def delete_key():
    wallet = load_wallet()

    if args.address in wallet:
        del wallet[args.address]

    save_wallet(wallet)


def set_bip44():
    wallet = load_wallet()

    if len(args.mnemonic) not in [12, 24]:
        print('Mnemonic must contain 12 or 24 words!', file=sys.stderr)
        sys.exit(1)

    bip44 = {'mnemonic': args.mnemonic,
             'passphrase': args.passphrase if args.passphrase is not None else ''}

    wallet.update(bip44)

    save_wallet(wallet)


def show():
    wallet = load_wallet()
    pprint(wallet)


# ----------------------------------------------------------------------------------------------------------------
# Parse the command line arguments
args = parser.parse_args()

# Execute the correct command based on the arguments given
if args.command == 'add_key':
    add_key()
elif args.command == 'delete_key':
    delete_key()
elif args.command == 'set_bip44':
    set_bip44()
elif args.command == 'show':
    show()
