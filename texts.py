#!/usr/bin/python
# -*- coding: utf-8 -*-

########################################################################################################
# get_explorers                                                                                        #
########################################################################################################
GET_EXPLORERS_DESCRIPTION = 'Get the list of explorer_ids that are configured on the spellbook server.'
GET_EXPLORERS_EPILOG = '''
examples:
  - spellbook.py get_explorers
    -> Get a list of configured explorers
'''

########################################################################################################
# save_explorer                                                                                        #
########################################################################################################
SAVE_EXPLORER_DESCRIPTION = 'Save or update the configuration of an explorer in the spellbook.'
SAVE_EXPLORER_EPILOG = '''
examples:
  - spellbook.py save_explorer blockchain.info Blockchain.info https://blockchain.info 1
    -> Save or update an explorer with name 'blockchain.info' in the spellbook with priority 1
    
  - spellbook.py save_explorer blockchain.info Blockchain.info https://testnet.blockchain.info 1 --TESTNET
    -> Save or update an explorer with name 'blockchain.info' in the spellbook with priority 1 to use the testnet instead of mainnet
    
  - spellbook.py save_explorer blocktrail Blocktrail.com https://api.blocktrail.com/v1 2 -b='ABC123'
    -> Save or update an explorer with name 'blocktrail.com' in the spellbook with priority 2 and given blocktrail api key    
   
  - spellbook.py save_explorer ... -k=<myapikey> -s=<myapisecret>
    -> Use given api key and api secret to authenticate with the REST API
'''

########################################################################################################
# get_explorer_config                                                                                  #
########################################################################################################
GET_EXPLORER_CONFIG_DESCRIPTION = 'Get configuration info about a specific explorer.'
GET_EXPLORER_CONFIG_EPILOG = '''
examples:
  - spellbook.py get_explorer_config blocktrail.com
    -> Get configuration info about a specific explorer with id 'blocktrail.com'
    
  - spellbook.py get_explorer_config ... -k=<myapikey> -s=<myapisecret>
    -> Use given api key and api secret to authenticate with the REST API
'''

########################################################################################################
# delete_explorer                                                                                      #
########################################################################################################
DELETE_EXPLORER_DESCRIPTION = 'Delete a specific explorer.'
DELETE_EXPLORER_EPILOG = '''
examples:
  - spellbook.py delete_explorer blocktrail.com
    -> Delete the explorer with id 'blocktrail.com'
  
  - spellbook.py delete_explorer ... -k=<myapikey> -s=<myapisecret>
    -> Use given api key and api secret to authenticate with the REST API
'''

########################################################################################################
# get_latest_block                                                                                     #
########################################################################################################
GET_LATEST_BLOCK_DESCRIPTION = 'Get the latest block.'
GET_LATEST_BLOCK_EPILOG = '''
examples:
  - spellbook.py get_latest_block
    -> Get the latest block using the default explorer
    
  - spellbook.py get_latest_block --explorer=blockchain.info
    -> Get the latest block using the blockchain.info explorer to retrieve the data    
'''

########################################################################################################
# get_block                                                                                            #
########################################################################################################
GET_BLOCK_DESCRIPTION = 'Get a block by a block hash or a block height.'
GET_BLOCK_EPILOG = '''
examples:
  - spellbook.py get_block 488470
    -> Get block at height 488470 using the default explorer
  
  - spellbook.py get_block 000000000000000000f6af507822a695390bada30cbd0c517c12442effb277af
    -> Get block with hash 000000000000000000f6af507822a695390bada30cbd0c517c12442effb277af using the default explorer
  
  - spellbook.py get_block 488470 --explorer=blockchain.info
    -> Get block at height 488470 using the blockchain.info explorer to retrieve the data
'''

########################################################################################################
# get_prime_input_address                                                                              #
########################################################################################################
GET_PRIME_INPUT_ADDRESS_DESCRIPTION = 'Get the prime input address of a transaction. This is the input address that comes first alphabetically.'
GET_PRIME_INPUT_ADDRESS_EPILOG = '''
examples:
  - spellbook.py get_prime_input_address 39bb5f5d50882227f93b980df15ea676414f0363770a0174a13c8f55c877b598
    -> Get the prime input address of tx 39bb5f5d50882227f93b980df15ea676414f0363770a0174a13c8f55c877b598 using the default explorer
    
  - spellbook.py get_prime_input_address 39bb5f5d50882227f93b980df15ea676414f0363770a0174a13c8f55c877b598 --explorer=blockchain.info
    -> Get the prime input address of tx 39bb5f5d50882227f93b980df15ea676414f0363770a0174a13c8f55c877b598 using the blockchain.info explorer to retrieve the data
'''

########################################################################################################
# get_transactions                                                                                     #
########################################################################################################
GET_TRANSACTIONS_DESCRIPTION = 'Get all transactions that a specific address has received or sent.'
GET_TRANSACTIONS_EPILOG = '''
examples:
  - spellbook.py get_transactions 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8
    -> Get all transactions of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the default explorer

  - spellbook.py get_transactions 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 --explorer=blockchain.info
    -> Get all transactions of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the blockchain.info explorer to retrieve the data
'''

########################################################################################################
# get_balance                                                                                          #
########################################################################################################
GET_BALANCE_DESCRIPTION = 'Get the current balance of an address. This includes the final balance, the total received balance and total sent balance'
GET_BALANCE_EPILOG = '''
examples:
  - spellbook.py get_balance 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8
    -> Get the balance of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the default explorer

  - spellbook.py get_balance 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 --explorer=blockchain.info
    -> Get the balance of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the blockchain.info explorer to retrieve the data
'''

########################################################################################################
# get_utxos                                                                                            #
########################################################################################################
GET_UTXOS_DESCRIPTION = 'Get the UTXOs of an address with at least the specified number of confirmations (default=1).'
GET_UTXOS_EPILOG = '''
examples:
  - spellbook.py get_utxos 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8
    -> Get the UTXOs of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 with at least 1 confirmation using the default explorer

  - spellbook.py get_utxos 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 -c=6
    -> Get the UTXOs of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 with at least 6 confirmations using the default explorer

  - spellbook.py get_utxos 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 --explorer=blockchain.info
    -> Get the UTXOs of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the blockchain.info explorer to retrieve the data
'''

########################################################################################################
# get_sil                                                                                              #
########################################################################################################
GET_SIL_DESCRIPTION = 'Get the Simplified Inputs List (SIL) of an address.'
GET_SIL_EPILOG = '''
examples:
  - spellbook.py get_sil 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8
    -> Get the SIL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the default explorer

  - spellbook.py get_sil 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 -b=478000
    -> Get the SIL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 at block height 478000 using the default explorer

  - spellbook.py get_sil 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 --explorer=blockchain.info
    -> Get the SIL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the blockchain.info explorer to retrieve the data
'''

########################################################################################################
# get_profile                                                                                          #
########################################################################################################
GET_PROFILE_DESCRIPTION = 'Get the profile of an address.'
GET_PROFILE_EPILOG = '''
examples:
  - spellbook.py get_profile 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8
    -> Get the profile of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the default explorer

  - spellbook.py get_profile 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 -b=478000
    -> Get the profile of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 at block height 478000 using the default explorer

  - spellbook.py get_profile 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 --explorer=blockchain.info
    -> Get the profile of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the blockchain.info explorer to retrieve the data
'''

########################################################################################################
# get_sul                                                                                              #
########################################################################################################
GET_SUL_DESCRIPTION = 'Get the Simplified UTXO List (SUL) of an address.'
GET_SUL_EPILOG = '''
examples:
  - spellbook.py get_sul 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8
    -> Get the SUL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the default explorer

  - spellbook.py get_sul 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 -c=6
    -> Get the SUL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 with at least 6 confirmations using the default explorer

  - spellbook.py get_sul 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 --explorer=blockchain.info
    -> Get the SUL of address 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 using the blockchain.info explorer to retrieve the data
'''