#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import time

import requests
import simplejson

import texts
from authentication import signature
from helpers.configurationhelpers import get_host, get_port, get_key, get_secret, get_spellbook_uri
from validators.validators import valid_distribution

# Make sure we are in the correct working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ----------------------------------------------------------------------------------------------------------------

host, port = get_host(), get_port()
key, secret = get_key(), get_secret()

# ----------------------------------------------------------------------------------------------------------------

# Create main parser
parser = argparse.ArgumentParser(description='Valyrian spellbook command line interface', formatter_class=argparse.RawDescriptionHelpFormatter)
subparsers = parser.add_subparsers(title='Spellbook subcommands', metavar='', dest='command')

# Create parser for the get_llms subcommand
get_llms_parser = subparsers.add_parser(name='get_llms',
                                        help='Get list of configured LLMs',
                                        formatter_class=argparse.RawDescriptionHelpFormatter,
                                        description=texts.GET_LLMS_DESCRIPTION,
                                        epilog=texts.GET_LLMS_EPILOG)

# Create parser for the get_llm_config subcommand
get_llm_config_parser = subparsers.add_parser(name='get_llm_config',
                                              help='Get configuration info about a specific LLM',
                                              formatter_class=argparse.RawDescriptionHelpFormatter,
                                              description=texts.GET_LLM_CONFIG_DESCRIPTION,
                                              epilog=texts.GET_LLM_CONFIG_EPILOG)

get_llm_config_parser.add_argument('id', help='id of the LLM')

# Create parser for the save_llm_config subcommand
save_llm_config_parser = subparsers.add_parser(name='save_llm_config',
                                               help='Save or update an LLM in the spellbook',
                                               formatter_class=argparse.RawDescriptionHelpFormatter,
                                               description=texts.SAVE_LLM_CONFIG_DESCRIPTION,
                                               epilog=texts.SAVE_LLM_CONFIG_EPILOG)

save_llm_config_parser.add_argument('id', help='id of the LLM')
save_llm_config_parser.add_argument('host', help='host of the server that runs the LLM')
save_llm_config_parser.add_argument('-p', '--port', help='port of the server that runs the LLM', default=None)
save_llm_config_parser.add_argument('-t', '--server_type', help='server type that runs the LLM', default='Oobabooga')
save_llm_config_parser.add_argument('-m', '--model_name', help='name of the model', default=None)
save_llm_config_parser.add_argument('-d', '--description', help='description of the model', default='')
save_llm_config_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
save_llm_config_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)

# Create parser for the delete_llm subcommand
delete_llm_parser = subparsers.add_parser(name='delete_llm',
                                          help='Delete a specific LLM',
                                          formatter_class=argparse.RawDescriptionHelpFormatter,
                                          description=texts.DELETE_LLM_DESCRIPTION,
                                          epilog=texts.DELETE_LLM_EPILOG)

delete_llm_parser.add_argument('id', help='id of the LLM')
delete_llm_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
delete_llm_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)

# Create parser for the get_explorers subcommand
get_explorers_parser = subparsers.add_parser(name='get_explorers',
                                             help='Get list of configured explorers',
                                             formatter_class=argparse.RawDescriptionHelpFormatter,
                                             description=texts.GET_EXPLORERS_DESCRIPTION,
                                             epilog=texts.GET_EXPLORERS_EPILOG)

# Create parser for the save_explorer subcommand
save_explorer_parser = subparsers.add_parser(name='save_explorer',
                                             help='Save or update an explorer in the spellbook',
                                             formatter_class=argparse.RawDescriptionHelpFormatter,
                                             description=texts.SAVE_EXPLORER_DESCRIPTION,
                                             epilog=texts.SAVE_EXPLORER_EPILOG)

save_explorer_parser.add_argument('name', help='name of the explorer')
save_explorer_parser.add_argument('type', help='type of the explorer', choices=['BTC.com', 'Blockchain.info', 'Insight', 'Blocktrail.com', 'Chain.so'])
save_explorer_parser.add_argument('priority', help='priority of the explorer')
save_explorer_parser.add_argument('--testnet', help='use TESTNET instead of mainnet', action='store_true')
save_explorer_parser.add_argument('-u', '--url', help='URL of the explorer (only needed for Insight explorers)')
save_explorer_parser.add_argument('-b', '--blocktrail_key', help='API key for the explorer (only needed for blocktrail.com)', default='')
save_explorer_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
save_explorer_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)

# Create parser for the get_explorer_config subcommand
get_explorer_config_parser = subparsers.add_parser(name='get_explorer_config',
                                                   help='Get configuration info about a specific explorer',
                                                   formatter_class=argparse.RawDescriptionHelpFormatter,
                                                   description=texts.GET_EXPLORER_CONFIG_DESCRIPTION,
                                                   epilog=texts.GET_EXPLORER_CONFIG_EPILOG)

get_explorer_config_parser.add_argument('name', help='Name of the explorer')
get_explorer_config_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
get_explorer_config_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)

# Create parser for the delete_explorer subcommand
delete_explorer_parser = subparsers.add_parser(name='delete_explorer',
                                               help='Delete a specific explorer',
                                               formatter_class=argparse.RawDescriptionHelpFormatter,
                                               description=texts.DELETE_EXPLORER_DESCRIPTION,
                                               epilog=texts.DELETE_EXPLORER_EPILOG)

delete_explorer_parser.add_argument('name', help='Name of the explorer')
delete_explorer_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
delete_explorer_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)

# ----------------------------------------------------------------------------------------------------------------

# Create parser for the get_latest_block subcommand
get_latest_block_parser = subparsers.add_parser(name='get_latest_block',
                                                help='Get the latest block',
                                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                                description=texts.GET_LATEST_BLOCK_DESCRIPTION,
                                                epilog=texts.GET_LATEST_BLOCK_EPILOG)

get_latest_block_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')

# Create parser for the get_block subcommand
get_block_parser = subparsers.add_parser(name='get_block',
                                         help='Get a block by height or hash',
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         description=texts.GET_BLOCK_DESCRIPTION,
                                         epilog=texts.GET_BLOCK_EPILOG)

get_block_parser.add_argument('id', help='The height OR the hash of the block')
get_block_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')

# Create parser for the get_prime_input_address subcommand
get_prime_input_address_parser = subparsers.add_parser(name='get_prime_input_address',
                                                       help='Get the prime input address of a transaction',
                                                       formatter_class=argparse.RawDescriptionHelpFormatter,
                                                       description=texts.GET_PRIME_INPUT_ADDRESS_DESCRIPTION,
                                                       epilog=texts.GET_PRIME_INPUT_ADDRESS_EPILOG)

get_prime_input_address_parser.add_argument('txid', help='The txid of the transaction')
get_prime_input_address_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')

# Create parser for the get_transaction subcommand
get_transaction_parser = subparsers.add_parser(name='get_transaction',
                                               help='Get a transaction',
                                               formatter_class=argparse.RawDescriptionHelpFormatter,
                                               description=texts.GET_TRANSACTION_DESCRIPTION,
                                               epilog=texts.GET_TRANSACTION_EPILOG)

get_transaction_parser.add_argument('txid', help='The txid of the transaction')
get_transaction_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')

# Create parser for the get_transactions subcommand
get_transactions_parser = subparsers.add_parser(name='get_transactions',
                                                help='Get all transactions that a specific address has received or sent',
                                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                                description=texts.GET_TRANSACTIONS_DESCRIPTION,
                                                epilog=texts.GET_TRANSACTIONS_EPILOG)

get_transactions_parser.add_argument('address', help='The address')
get_transactions_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')

# Create parser for the get_balance subcommand
get_balance_parser = subparsers.add_parser(name='get_balance',
                                           help='Get the current balance of an address',
                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                           description=texts.GET_BALANCE_DESCRIPTION,
                                           epilog=texts.GET_BALANCE_EPILOG)

get_balance_parser.add_argument('address', help='The address')
get_balance_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')

# Create parser for the get_utxos subcommand
get_utxos_parser = subparsers.add_parser(name='get_utxos',
                                         help='Get the current UTXOs of an address',
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         description=texts.GET_UTXOS_DESCRIPTION,
                                         epilog=texts.GET_UTXOS_EPILOG)

get_utxos_parser.add_argument('address', help='The address')
get_utxos_parser.add_argument('-c', '--confirmations', help='The number of confirmations required (default=1)', default=1)
get_utxos_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')

# ----------------------------------------------------------------------------------------------------------------------

# Create parser for the get_sil subcommand
get_sil_parser = subparsers.add_parser(name='get_sil',
                                       help='Get the Simplified Inputs List (SIL) of an address',
                                       formatter_class=argparse.RawDescriptionHelpFormatter,
                                       description=texts.GET_SIL_DESCRIPTION,
                                       epilog=texts.GET_SIL_EPILOG)

get_sil_parser.add_argument('address', help='The address')
get_sil_parser.add_argument('-b', '--block_height', help='The block height for the SIL (optional, default=latest block)', default=0)
get_sil_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')

# Create parser for the get_profile subcommand
get_profile_parser = subparsers.add_parser(name='get_profile',
                                           help='Get the profile of an address',
                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                           description=texts.GET_PROFILE_DESCRIPTION,
                                           epilog=texts.GET_PROFILE_EPILOG)

get_profile_parser.add_argument('address', help='The address')
get_profile_parser.add_argument('-b', '--block_height', help='The block height for the profile (optional, default=latest block)', default=0)
get_profile_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')

# Create parser for the get_sul subcommand
get_sul_parser = subparsers.add_parser(name='get_sul',
                                       help='Get the Simplified UTXO List (SIL) of an address',
                                       formatter_class=argparse.RawDescriptionHelpFormatter,
                                       description=texts.GET_SUL_DESCRIPTION,
                                       epilog=texts.GET_SUL_EPILOG)

get_sul_parser.add_argument('address', help='The address')
get_sul_parser.add_argument('-c', '--confirmations', help='The number of confirmations a utxo must have to be included in the SUL (optional, default=1)', default=1)
get_sul_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')

# ----------------------------------------------------------------------------------------------------------------

# Create parser for the get_lal subcommand
get_lal_parser = subparsers.add_parser(name='get_lal',
                                       help='Get the Linked Address List (LAL) of an address and an xpub key',
                                       formatter_class=argparse.RawDescriptionHelpFormatter,
                                       description=texts.GET_LAL_DESCRIPTION,
                                       epilog=texts.GET_LAL_EPILOG)

get_lal_parser.add_argument('address', help='The address')
get_lal_parser.add_argument('xpub', help='The xpub key')
get_lal_parser.add_argument('-b', '--block_height', help='The block height for the SIL to link with the corresponding address from the xpub (optional, default=latest block)', default=0)
get_lal_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')

# Create parser for the get_lbl subcommand
get_lbl_parser = subparsers.add_parser(name='get_lbl',
                                       help='Get the Linked Balance List (LBL) of an address and an xpub key',
                                       formatter_class=argparse.RawDescriptionHelpFormatter,
                                       description=texts.GET_LBL_DESCRIPTION,
                                       epilog=texts.GET_LBL_EPILOG)

get_lbl_parser.add_argument('address', help='The address')
get_lbl_parser.add_argument('xpub', help='The xpub key')
get_lbl_parser.add_argument('-b', '--block_height', help='The block height for the SIL to link with the corresponding address from the xpub (optional, default=latest block)', default=0)
get_lbl_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')

# Create parser for the get_lrl subcommand
get_lrl_parser = subparsers.add_parser(name='get_lrl',
                                       help='Get the Linked Received List (LRL) of an address and an xpub key',
                                       formatter_class=argparse.RawDescriptionHelpFormatter,
                                       description=texts.GET_LRL_DESCRIPTION,
                                       epilog=texts.GET_LRL_EPILOG)

get_lrl_parser.add_argument('address', help='The address')
get_lrl_parser.add_argument('xpub', help='The xpub key')
get_lrl_parser.add_argument('-b', '--block_height', help='The block height for the SIL to link with the corresponding address from the xpub (optional, default=latest block)', default=0)
get_lrl_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')

# Create parser for the get_lsl subcommand
get_lsl_parser = subparsers.add_parser(name='get_lsl',
                                       help='Get the Linked Sent List (LSL) of an address and an xpub key',
                                       formatter_class=argparse.RawDescriptionHelpFormatter,
                                       description=texts.GET_LSL_DESCRIPTION,
                                       epilog=texts.GET_LSL_EPILOG)

get_lsl_parser.add_argument('address', help='The address')
get_lsl_parser.add_argument('xpub', help='The xpub key')
get_lsl_parser.add_argument('-b', '--block_height', help='The block height for the SIL to link with the corresponding address from the xpub (optional, default=latest block)', default=0)
get_lsl_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')

# ----------------------------------------------------------------------------------------------------------------

# Create parser for the get_random_address subcommand
get_random_address_parser = subparsers.add_parser(name='get_random_address',
                                                  help='Get a random address from SIL, LBL, LRL or LSL where the chance of an address being picked is proportional to its value in the list',
                                                  formatter_class=argparse.RawDescriptionHelpFormatter,
                                                  description=texts.GET_RANDOM_ADDRESS_DESCRIPTION,
                                                  epilog=texts.GET_RANDOM_ADDRESS_EPILOG)

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
                                            description=texts.GET_TRIGGERS_DESCRIPTION,
                                            epilog=texts.GET_TRIGGERS_EPILOG)

get_triggers_parser.add_argument('-a', '--active', help='Only get the triggers that are currently active')

# Create parser for the get_trigger subcommand
get_trigger_config_parser = subparsers.add_parser(name='get_trigger_config',
                                                  help='Get the configuration of specified trigger',
                                                  formatter_class=argparse.RawDescriptionHelpFormatter,
                                                  description=texts.GET_TRIGGER_CONFIG_DESCRIPTION,
                                                  epilog=texts.GET_TRIGGER_CONFIG_EPILOG)

get_trigger_config_parser.add_argument('trigger_id', help='The id of the trigger')
get_trigger_config_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
get_trigger_config_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)

# Create parser for the save_trigger subcommand
save_trigger_parser = subparsers.add_parser(name='save_trigger',
                                            help='Save or update the configuration of a trigger',
                                            formatter_class=argparse.RawDescriptionHelpFormatter,
                                            description=texts.SAVE_TRIGGER_DESCRIPTION,
                                            epilog=texts.SAVE_TRIGGER_EPILOG)

save_trigger_parser.add_argument('trigger_id', help='The id of the trigger')
save_trigger_parser.add_argument('-r', '--reset', help='Reset the trigger in case it has been triggered already', action='store_true')
save_trigger_parser.add_argument('-t', '--type', help='The type of the trigger', choices=['Manual', 'Balance', 'Received', 'Sent', 'Block_height', 'Tx_confirmation', 'Timestamp', 'Recurring', 'TriggerStatus', 'DeadMansSwitch', 'SignedMessage', 'HTTPGetRequest', 'HTTPPostRequest', 'HTTPDeleteRequest'])
save_trigger_parser.add_argument('-sc', '--script', help='The script to run when the trigger activates')
save_trigger_parser.add_argument('-a', '--address', help='The address to check the final balance, total received or total sent')
save_trigger_parser.add_argument('-am', '--amount', help='The amount', type=int)
save_trigger_parser.add_argument('-c', '--confirmations', help='The number of confirmations before the trigger is activated', default=3, type=int)
save_trigger_parser.add_argument('-b', '--block_height', help='The block height at which the trigger will be activated', type=int)
save_trigger_parser.add_argument('-tx', '--txid', help='The txid to monitor the number of confirmations')
save_trigger_parser.add_argument('-ts', '--timestamp', help='The unix timestamp at which the trigger will be activated', type=int)
save_trigger_parser.add_argument('-bt', '--begin_time', help='The unix timestamp at which the recurring trigger will begin', type=int)
save_trigger_parser.add_argument('-et', '--end_time', help='The unix timestamp at which the recurring trigger will end', type=int)
save_trigger_parser.add_argument('-i', '--interval', help='The amount of seconds between each activation of the recurring trigger', type=int)
save_trigger_parser.add_argument('-pt', '--previous_trigger', help='The id of the trigger of which to check the status')
save_trigger_parser.add_argument('-pts', '--previous_trigger_status', help='The status a previous trigger must be for this trigger to activate', choices=['Succeeded', 'Failed'])
save_trigger_parser.add_argument('-ti', '--timeout', help='The amount of seconds before an activated DeadMansSwitch times out', type=int)
save_trigger_parser.add_argument('-we', '--warning_email', help='The email address to send a warning to when a DeadMansSwitch reaches 50%%, 75%% and 90%% of the timeout')
save_trigger_parser.add_argument('-m', '--multi', help='Allow the trigger to activate multiple times', action='store_true')
save_trigger_parser.add_argument('-d', '--description', help='A description of the trigger')
save_trigger_parser.add_argument('-cn', '--creator_name', help='The name of the creator the trigger')
save_trigger_parser.add_argument('-ce', '--creator_email', help='The email of the creator of the trigger')
save_trigger_parser.add_argument('-y', '--youtube', help='A video on youtube belonging to the trigger')
save_trigger_parser.add_argument('-v', '--visibility', help='The visibility of the trigger (Public or Private)', choices=['Public', 'Private'])
save_trigger_parser.add_argument('-st', '--status', help='The status of the trigger (Pending, Active or Disabled)', choices=['Pending', 'Active', 'Disabled'])
save_trigger_parser.add_argument('-ac', '--actions', help='The action ids to run when the trigger activates', nargs='*')

save_trigger_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
save_trigger_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)

# Create parser for the delete_trigger subcommand
delete_trigger_parser = subparsers.add_parser(name='delete_trigger',
                                              help='Delete a specified trigger',
                                              formatter_class=argparse.RawDescriptionHelpFormatter,
                                              description=texts.DELETE_TRIGGER_DESCRIPTION,
                                              epilog=texts.DELETE_TRIGGER_EPILOG)

delete_trigger_parser.add_argument('trigger_id', help='The id of the trigger to delete')
delete_trigger_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
delete_trigger_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)

# Create parser for the activate_trigger subcommand
activate_trigger_parser = subparsers.add_parser(name='activate_trigger',
                                                help='Activate a specified manual trigger',
                                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                                description=texts.ACTIVATE_TRIGGER_DESCRIPTION,
                                                epilog=texts.ACTIVATE_TRIGGER_EPILOG)

activate_trigger_parser.add_argument('trigger_id', help='The id of the trigger to activate')
activate_trigger_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
activate_trigger_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)

# Create parser for the send_signed_message subcommand
send_signed_message_parser = subparsers.add_parser(name='send_signed_message',
                                                   help='Send a signed message to a trigger',
                                                   formatter_class=argparse.RawDescriptionHelpFormatter,
                                                   description=texts.SEND_SIGNED_MESSAGE_DESCRIPTION,
                                                   epilog=texts.SEND_SIGNED_MESSAGE_EPILOG)

send_signed_message_parser.add_argument('trigger_id', help='The id of the trigger to activate')
send_signed_message_parser.add_argument('address', help='The address that signed the message')
send_signed_message_parser.add_argument('message', help='The message that was signed OR a filename containing the message')
send_signed_message_parser.add_argument('signature', help='The signature of the message')

# Create parser for the sign_message subcommand
sign_message_parser = subparsers.add_parser(name='sign_message',
                                            help='Sign a message with the private key of an address in the hot wallet',
                                            formatter_class=argparse.RawDescriptionHelpFormatter,
                                            description=texts.SIGN_MESSAGE_DESCRIPTION,
                                            epilog=texts.SIGN_MESSAGE_EPILOG)

sign_message_parser.add_argument('address', help='The address to the message (must be in the hot wallet of the server)')
sign_message_parser.add_argument('message', help='The message to sign OR a filename containing the message (max 255 characters)', nargs='*')
sign_message_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
sign_message_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)

# Create parser for the check_triggers subcommand
check_triggers_parser = subparsers.add_parser(name='check_triggers',
                                              help='Check a triggers and activate it them if conditions have been fulfilled',
                                              formatter_class=argparse.RawDescriptionHelpFormatter,
                                              description=texts.CHECK_TRIGGERS_DESCRIPTION,
                                              epilog=texts.CHECK_TRIGGERS_EPILOG)

check_triggers_parser.add_argument('trigger_id', help='The id of the trigger to check', nargs='?')
check_triggers_parser.add_argument('-e', '--explorer', help='Use specified explorer to retrieve data from the blockchain')
check_triggers_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
check_triggers_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)

# ----------------------------------------------------------------------------------------------------------------

# Create parser for the get_actions subcommand
get_actions_parser = subparsers.add_parser(name='get_actions',
                                           help='Get the list of configured action_ids',
                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                           description=texts.GET_ACTIONS_DESCRIPTION,
                                           epilog=texts.GET_ACTIONS_EPILOG)

get_actions_parser.add_argument('-i', '--trigger_id', help='The id of the trigger')

# Create parser for the get_action_config subcommand
get_action_config_parser = subparsers.add_parser(name='get_action_config',
                                                 help='Get the configuration of specified action',
                                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                                 description=texts.GET_ACTION_CONFIG_DESCRIPTION,
                                                 epilog=texts.GET_ACTION_CONFIG_EPILOG)

get_action_config_parser.add_argument('action_id', help='The id of the action')
get_action_config_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
get_action_config_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)

# Create parser for the save_action subcommand
save_action_parser = subparsers.add_parser(name='save_action',
                                           help='Save or update the configuration of an action',
                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                           description=texts.SAVE_ACTION_DESCRIPTION,
                                           epilog=texts.SAVE_ACTION_EPILOG)

save_action_parser.add_argument('action_id', help='The id of the action')
save_action_parser.add_argument('-t', '--type', help='The type of the action', choices=['Command', 'SpawnProcess', 'SendTransaction', 'RevealSecret', 'SendMail', 'Webhook', 'LaunchEvolver'])

save_action_parser.add_argument('-c', '--run_command', help='The command to run, only applicable to Command Actions')
save_action_parser.add_argument('-j', '--job_config', help='Configuration file for a LaunchEvolver action')

save_action_parser.add_argument('-mr', '--mail_recipients', help='The recipients of the email in a SendEmail Action, separated with comma')
save_action_parser.add_argument('-ms', '--mail_subject', help='The subject of the email in a SendEmail Action')
save_action_parser.add_argument('-mb', '--mail_body_template', help='The name of the body template of the email in a SendEmail Action')

save_action_parser.add_argument('-w', '--webhook', help='The url of a webhook, only applicable to Webhook Actions')

save_action_parser.add_argument('-rt', '--reveal_text', help='The text to reveal when the action is activated, only applicable to RevealSecret Actions')
save_action_parser.add_argument('-rl', '--reveal_link', help='The link to reveal when the action is activated, only applicable to RevealSecret Actions')

save_action_parser.add_argument('-fa', '--fee_address', help='The address to send the spellbook fee to')
save_action_parser.add_argument('-fp', '--fee_percentage', help='The spellbook fee as a percentage', type=float)

save_action_parser.add_argument('-wt', '--wallet_type', help='The type of the wallet of the sending address (Single or BIP44)', choices=['Single', 'BIP44'])
save_action_parser.add_argument('-sa', '--sending_address', help='The address to send the funds from')
save_action_parser.add_argument('-ba', '--bip44_account', help='The account in a BIP44 wallet', type=int)
save_action_parser.add_argument('-bi', '--bip44_index', help='The index in a BIP44 wallet of the sending address', type=int)

save_action_parser.add_argument('-ra', '--receiving_address', help='The address to receive the funds')
save_action_parser.add_argument('-rx', '--receiving_xpub', help='The xpub key to construct the LAL for the receiving addresses')
save_action_parser.add_argument('-a', '--amount', help='The amount in satoshis to send in a SendTransaction action, if omitted all available funds are sent', type=int)
save_action_parser.add_argument('-ma', '--minimum_amount', help='The minimum amount in satoshis to forward', type=int)
save_action_parser.add_argument('-ca', '--change_address', help='The address to receive the change if there is any, if not specified the sending address will receive the change')

save_action_parser.add_argument('-or', '--op_return_data', help='The data to include as a OP_RETURN output in a SendTransaction action (max 80 chars)')

save_action_parser.add_argument('-d', '--distribution', help='The filename of a json file containing a custom distribution')

save_action_parser.add_argument('-tt', '--transaction_type', help='The type of the transaction to send', choices=['Send2Single', 'Send2Many', 'Send2SIL', 'Send2LBL', 'Send2LRL', 'Send2LSL', 'Send2LAL'])
save_action_parser.add_argument('-reg_a', '--registration_address', help='The address used for the registration of a distribution')
save_action_parser.add_argument('-reg_b', '--registration_block_height', help='The block height used for the registration of a distribution, 0=latest block height', default=0, type=int)
save_action_parser.add_argument('-reg_x', '--registration_xpub', help='The xpub key used for the registration of a distribution')
save_action_parser.add_argument('-tft', '--tx_fee_type', help='The type of transaction fee to use: High, Medium, Low or Fixed', choices=['High', 'Medium', 'Low', 'Fixed'], default='Medium')
save_action_parser.add_argument('-tf', '--tx_fee', help='The transaction fee in satoshis per byte to use in case of Fixed fee type', type=int)

save_action_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
save_action_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)

# Create parser for the delete_action subcommand
delete_action_parser = subparsers.add_parser(name='delete_action',
                                             help='Delete a specified action',
                                             formatter_class=argparse.RawDescriptionHelpFormatter,
                                             description=texts.DELETE_ACTION_DESCRIPTION,
                                             epilog=texts.DELETE_ACTION_EPILOG)

delete_action_parser.add_argument('action_id', help='The id of the action')
delete_action_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
delete_action_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)

# Create parser for the run_action subcommand
run_action_parser = subparsers.add_parser(name='run_action',
                                          help='Run a specified action',
                                          formatter_class=argparse.RawDescriptionHelpFormatter,
                                          description=texts.RUN_ACTION_DESCRIPTION,
                                          epilog=texts.RUN_ACTION_EPILOG)

run_action_parser.add_argument('action_id', help='The id of the action')
run_action_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
run_action_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)

# Create parser for the get_reveal subcommand
get_reveal_parser = subparsers.add_parser(name='get_reveal',
                                          help='Get the reveal text or link from a RevealSecret action',
                                          formatter_class=argparse.RawDescriptionHelpFormatter,
                                          description=texts.GET_REVEAL_DESCRIPTION,
                                          epilog=texts.GET_REVEAL_EPILOG)

get_reveal_parser.add_argument('action_id', help='The id of the action')

# Create parser for the get_logs subcommand
get_logs_parser = subparsers.add_parser(name='get_logs',
                                        help='Get the log messages',
                                        formatter_class=argparse.RawDescriptionHelpFormatter,
                                        description=texts.GET_LOGS_DESCRIPTION,
                                        epilog=texts.GET_LOGS_EPILOG)

get_logs_parser.add_argument('filter_string', help='A filter string for the log messages', nargs='*')
get_logs_parser.add_argument('-k', '--api_key', help='API key for the spellbook REST API', default=key)
get_logs_parser.add_argument('-s', '--api_secret', help='API secret for the spellbook REST API', default=secret)


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
# Valyrian Spellbook Commands : LLMs        #
#############################################
def get_llms():
    url = '{spellbook_uri}/spellbook/llms'.format(spellbook_uri=get_spellbook_uri())
    do_get_request(url)


def get_llm_config():
    url = '{spellbook_uri}/spellbook/llms/{llm_id}'.format(spellbook_uri=get_spellbook_uri(), llm_id=args.id)
    do_get_request(url=url)


def save_llm_config():
    data = {'host': args.host,
            'port': args.port,
            'server_type': args.server_type,
            'model_name': args.model_name,
            'description': args.description}

    url = '{spellbook_uri}/spellbook/llms/{llm_id}'.format(spellbook_uri=get_spellbook_uri(), llm_id=args.id)
    do_post_request(url=url, data=data, authenticate=True)


def delete_llm():
    url = '{spellbook_uri}/spellbook/llms/{llm_id}'.format(spellbook_uri=get_spellbook_uri(), llm_id=args.id)
    do_delete_request(url=url, authenticate=True)


#############################################
# Valyrian Spellbook Commands : explorers   #
#############################################


def get_explorers():
    url = '{spellbook_uri}/spellbook/explorers'.format(spellbook_uri=get_spellbook_uri())
    do_get_request(url)


def get_explorer_config():
    url = '{spellbook_uri}/spellbook/explorers/{explorer_id}'.format(spellbook_uri=get_spellbook_uri(), explorer_id=args.name)
    do_get_request(url=url, authenticate=True)


def save_explorer():
    data = {'type': args.type,
            'api_key': args.blocktrail_key,
            'url': args.url,
            'priority': args.priority,
            'testnet': args.testnet}

    url = '{spellbook_uri}/spellbook/explorers/{explorer_id}'.format(spellbook_uri=get_spellbook_uri(), explorer_id=args.name)
    do_post_request(url=url, authenticate=True, data=data)


def delete_explorer():
    url = '{spellbook_uri}/spellbook/explorers/{explorer_id}'.format(spellbook_uri=get_spellbook_uri(), explorer_id=args.name)
    do_delete_request(url=url, authenticate=True)


# ----------------------------------------------------------------------------------------------------------------


def get_latest_block():
    url = '{spellbook_uri}/spellbook/blocks/latest'.format(spellbook_uri=get_spellbook_uri())
    do_get_request(url=url)


def get_block():
    url = '{spellbook_uri}/spellbook/blocks/{id}'.format(spellbook_uri=get_spellbook_uri(), id=args.id)
    do_get_request(url=url)


def get_prime_input_address():
    url = '{spellbook_uri}/spellbook/transactions/{txid}/prime_input'.format(spellbook_uri=get_spellbook_uri(), txid=args.txid)
    do_get_request(url=url)


def get_transaction():
    url = '{spellbook_uri}/spellbook/transactions/{txid}'.format(spellbook_uri=get_spellbook_uri(), txid=args.txid)
    do_get_request(url=url)


def get_transactions():
    url = '{spellbook_uri}/spellbook/addresses/{address}/transactions'.format(spellbook_uri=get_spellbook_uri(), address=args.address)
    do_get_request(url=url)


def get_balance():
    url = '{spellbook_uri}/spellbook/addresses/{address}/balance'.format(spellbook_uri=get_spellbook_uri(), address=args.address)
    do_get_request(url=url)


def get_utxos():
    url = '{spellbook_uri}/spellbook/addresses/{address}/utxos?confirmations={confirmations}'.format(spellbook_uri=get_spellbook_uri(),
                                                                                                     host=host,
                                                                                                     port=port,
                                                                                                     address=args.address,
                                                                                                     confirmations=args.confirmations)
    do_get_request(url=url)


# ----------------------------------------------------------------------------------------------------------------


def get_sil():
    data = {'block_height': args.block_height}
    url = '{spellbook_uri}/spellbook/addresses/{address}/SIL'.format(spellbook_uri=get_spellbook_uri(), address=args.address)
    do_get_request(url=url, data=data)


def get_profile():
    data = {'block_height': args.block_height}
    url = '{spellbook_uri}/spellbook/addresses/{address}/profile'.format(spellbook_uri=get_spellbook_uri(), address=args.address)
    do_get_request(url=url, data=data)


def get_sul():
    data = {'confirmations': args.confirmations}
    url = '{spellbook_uri}/spellbook/addresses/{address}/SUL'.format(spellbook_uri=get_spellbook_uri(), address=args.address)
    do_get_request(url=url, data=data)


# ----------------------------------------------------------------------------------------------------------------


def get_lal():
    data = {'block_height': args.block_height,
            'xpub': args.xpub}
    url = '{spellbook_uri}/spellbook/addresses/{address}/LAL'.format(spellbook_uri=get_spellbook_uri(), address=args.address)
    do_get_request(url=url, data=data)


def get_lbl():
    data = {'block_height': args.block_height,
            'xpub': args.xpub}
    url = '{spellbook_uri}/spellbook/addresses/{address}/LBL'.format(spellbook_uri=get_spellbook_uri(), address=args.address)
    do_get_request(url=url, data=data)


def get_lrl():
    data = {'block_height': args.block_height,
            'xpub': args.xpub}
    url = '{spellbook_uri}/spellbook/addresses/{address}/LRL'.format(spellbook_uri=get_spellbook_uri(), address=args.address)
    do_get_request(url=url, data=data)


def get_lsl():
    data = {'block_height': args.block_height,
            'xpub': args.xpub}
    url = '{spellbook_uri}/spellbook/addresses/{address}/LSL'.format(spellbook_uri=get_spellbook_uri(), address=args.address)
    do_get_request(url=url, data=data)


# ----------------------------------------------------------------------------------------------------------------


def get_random_address():
    data = {'rng_block_height': args.rng_block_height,
            'sil_block_height': args.block_height,
            'xpub': args.xpub}
    url = '{spellbook_uri}/spellbook/addresses/{address}/random/{source}'.format(spellbook_uri=get_spellbook_uri(),
                                                                                 address=args.address,
                                                                                 source=args.source)
    do_get_request(url=url, data=data)


# ----------------------------------------------------------------------------------------------------------------
# Triggers
# ----------------------------------------------------------------------------------------------------------------


def get_triggers():
    url = '{spellbook_uri}/spellbook/triggers'.format(spellbook_uri=get_spellbook_uri())
    do_get_request(url=url)


def get_trigger():
    url = '{spellbook_uri}/spellbook/triggers/{trigger_id}'.format(spellbook_uri=get_spellbook_uri(), trigger_id=args.trigger_id)
    do_get_request(url=url, authenticate=True)


def save_trigger():
    data = {}
    if args.type is not None:
        data['trigger_type'] = args.type

    if args.script is not None:
        data['script'] = args.script

    if args.address is not None:
        data['address'] = args.address

    if args.amount is not None:
        data['amount'] = args.amount

    if args.confirmations is not None:
        data['confirmations'] = args.confirmations

    if args.block_height is not None:
        data['block_height'] = args.block_height

    if args.txid is not None:
        data['txid'] = args.block_height

    if args.timestamp is not None:
        data['timestamp'] = args.timestamp

    if args.begin_time is not None:
        data['begin_time'] = args.begin_time

    if args.end_time is not None:
        data['end_time'] = args.end_time

    if args.interval is not None:
        data['interval'] = args.interval

    if args.timeout is not None:
        data['timeout'] = args.timeout

    if args.warning_email is not None:
        data['warning_email'] = args.warning_email

    if args.reset is not None:
        data['reset'] = args.reset

    if args.multi is not None:
        data['multi'] = args.multi

    if args.previous_trigger is not None:
        data['previous_trigger'] = args.previous_trigger

    if args.previous_trigger_status is not None:
        data['previous_trigger_status'] = args.previous_trigger_status

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

    if args.actions is not None:
        data['actions'] = args.actions

    url = '{spellbook_uri}/spellbook/triggers/{trigger_id}'.format(spellbook_uri=get_spellbook_uri(), trigger_id=args.trigger_id)
    do_post_request(url=url, authenticate=True, data=data)


def delete_trigger():
    url = '{spellbook_uri}/spellbook/triggers/{trigger_id}'.format(spellbook_uri=get_spellbook_uri(), trigger_id=args.trigger_id)
    do_delete_request(url=url, authenticate=True)


def activate_trigger():
    url = '{spellbook_uri}/spellbook/triggers/{trigger_id}/activate'.format(spellbook_uri=get_spellbook_uri(), trigger_id=args.trigger_id)
    do_get_request(url=url, authenticate=True)


def send_signed_message():
    data = {}
    if args.address is not None:
        data['address'] = args.address

    if args.message is not None:
        if os.path.isfile(args.message):
            with open(args.message, 'r') as input_file:
                data['message'] = input_file.read()
        else:
            data['message'] = args.message

    if args.signature is not None:
        data['signature'] = args.signature

    url = '{spellbook_uri}/spellbook/triggers/{trigger_id}/message'.format(spellbook_uri=get_spellbook_uri(), trigger_id=args.trigger_id)
    do_post_request(url=url, data=data)


def sign_message():
    data = {}
    if args.address is not None:
        data['address'] = args.address

    if args.message is not None:
        message = ' '.join(args.message)
        if os.path.isfile(message):
            with open(message, 'r') as input_file:
                data['message'] = input_file.read()
        else:
            data['message'] = message

    if len(data['message']) >= 255:
        print('Message is to long: maximum 255 characters!')
        return

    url = '{spellbook_uri}/api/sign_message'.format(spellbook_uri=get_spellbook_uri())
    do_post_request(url=url, data=data, authenticate=True)


def check_triggers():
    if args.trigger_id is not None:
        url = '{spellbook_uri}/spellbook/triggers/{trigger_id}/check'.format(spellbook_uri=get_spellbook_uri(), trigger_id=args.trigger_id)
    else:
        url = '{spellbook_uri}/spellbook/check_triggers'.format(spellbook_uri=get_spellbook_uri())

    do_get_request(url=url, authenticate=True)


# ----------------------------------------------------------------------------------------------------------------
# Actions
# ----------------------------------------------------------------------------------------------------------------


def get_actions():
    url = '{spellbook_uri}/spellbook/actions'.format(spellbook_uri=get_spellbook_uri())
    do_get_request(url=url)


def get_action():
    url = '{spellbook_uri}/spellbook/actions/{action_id}'.format(spellbook_uri=get_spellbook_uri(), action_id=args.action_id)
    do_get_request(url=url, authenticate=True)


def save_action():
    data = {}
    if args.type is not None:
        data['action_type'] = args.type

    if args.run_command is not None:
        data['run_command'] = args.run_command

    if args.job_config is not None:
        data['job_config'] = args.job_config

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

    if args.wallet_type is not None:
        data['wallet_type'] = args.wallet_type

    if args.sending_address is not None:
        data['sending_address'] = args.sending_address

    if args.bip44_account is not None:
        data['bip44_account'] = args.bip44_account

    if args.bip44_index is not None:
        data['bip44_index'] = args.bip44_index

    if args.receiving_address is not None:
        data['receiving_address'] = args.receiving_address

    if args.amount is not None:
        data['amount'] = args.amount

    if args.minimum_amount is not None:
        data['minimum_amount'] = args.minimum_amount

    if args.op_return_data is not None:
        data['op_return_data'] = args.op_return_data

    if args.change_address is not None:
        data['change_address'] = args.change_address

    if args.transaction_type is not None:
        data['transaction_type'] = args.transaction_type

    if args.registration_address is not None:
        data['registration_address'] = args.registration_address

    if args.registration_block_height is not None:
        data['registration_block_height'] = args.registration_block_height

    if args.registration_xpub is not None:
        data['registration_xpub'] = args.registration_xpub

    if args.tx_fee_type is not None:
        data['tx_fee_type'] = args.tx_fee_type

    if args.tx_fee is not None and args.tx_fee_type == 'Fixed':
        data['tx_fee'] = args.tx_fee

    if args.distribution is not None and os.path.isfile(args.distribution):
        with open(args.distribution, 'r') as input_file:
            try:
                distribution = simplejson.load(input_file)
            except Exception as ex:
                print('Distribution file %s is not a valid json file: %s' % (args.distribution, ex), file=sys.stderr)
                sys.exit(1)

        if valid_distribution(distribution):
            data['distribution'] = distribution
        else:
            print('Distribution file does not contain a valid distribution: %s' % distribution, file=sys.stderr)
            print('Must be a dict where all keys are a valid address and the value is a integer greater than or equal to zero', file=sys.stderr)
            sys.exit(1)

    url = '{spellbook_uri}/spellbook/actions/{action_id}'.format(spellbook_uri=get_spellbook_uri(), action_id=args.action_id)
    do_post_request(url=url, authenticate=True, data=data)


def delete_action():
    url = '{spellbook_uri}/spellbook/actions/{action_id}'.format(spellbook_uri=get_spellbook_uri(), action_id=args.action_id)
    do_delete_request(url=url, authenticate=True)


def run_action():
    url = '{spellbook_uri}/spellbook/actions/{action_id}/run'.format(spellbook_uri=get_spellbook_uri(), action_id=args.action_id)
    do_get_request(url=url, authenticate=True)


def get_reveal():
    url = '{spellbook_uri}/spellbook/actions/{action_id}/reveal'.format(spellbook_uri=get_spellbook_uri(), action_id=args.action_id)
    do_get_request(url=url)


def get_logs():
    url = '{spellbook_uri}/spellbook/logs/{filter_string}'.format(spellbook_uri=get_spellbook_uri(), filter_string=" ".join(args.filter_string))
    do_get_request(url=url, authenticate=True)


def get_hivemind():
    url = '{spellbook_uri}/spellbook/hiveminds/{hivemind_id}'.format(spellbook_uri=get_spellbook_uri(), hivemind_id=args.hivemind_id)
    do_get_request(url=url)


def specify_explorer(url):
    try:
        explorer = getattr(args, 'explorer')
        if explorer is not None:
            url += '?' if '?' not in url else '&'
            url += 'explorer={explorer}'.format(explorer=args.explorer)
    except AttributeError:
        pass

    return url


def do_get_request(url, authenticate=False, data=None):
    url = specify_explorer(url)
    headers = add_authentication_headers(data=data) if authenticate is True else None

    try:
        r = requests.get(url, headers=headers, json=data)
        print(r.text)
    except Exception as ex:
        print('GET %s failed: %s' % (url, ex), file=sys.stderr)
        sys.exit(1)


def do_post_request(url, authenticate=False, data=None):
    url = specify_explorer(url)
    headers = add_authentication_headers(data=data) if authenticate is True else None

    try:
        r = requests.post(url, headers=headers, json=data)
        print(r.text)
    except Exception as ex:
        print('POST %s failed: %s' % (url, ex), file=sys.stderr)
        sys.exit(1)


def do_delete_request(url, authenticate=False, data=None):
    url = specify_explorer(url)
    headers = add_authentication_headers(data=data) if authenticate is True else None

    try:
        r = requests.delete(url, headers=headers, json=data)
        print(r.text)
    except Exception as ex:
        print('DELETE %s failed: %s' % (url, ex), file=sys.stderr)
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
elif args.command == 'get_transaction':
    get_transaction()
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
elif args.command == 'get_sul':
    get_sul()
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
elif args.command == 'send_signed_message':
    send_signed_message()
elif args.command == 'sign_message':
    sign_message()
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
elif args.command == 'get_logs':
    get_logs()
elif args.command == 'get_hivemind':
    get_hivemind()
elif args.command == 'get_llms':
    get_llms()
elif args.command == 'get_llm_config':
    get_llm_config()
elif args.command == 'save_llm_config':
    save_llm_config()
elif args.command == 'delete_llm':
    delete_llm()
