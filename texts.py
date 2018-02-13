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
SAVE_EXPLORER_DESCRIPTION = 'Save or update the configuration of an explorer in the spellbook'
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
GET_EXPLORER_CONFIG_DESCRIPTION = 'Get configuration info about a specific explorer'
GET_EXPLORER_CONFIG_EPILOG = '''
examples:
  - spellbook.py get_explorer_config blocktrail.com
    -> Get configuration info about a specific explorer with id 'blocktrail.com'
    
  - spellbook.py get_explorer_config ... -k=<myapikey> -s=<myapisecret>
    -> Use given api key and api secret to authenticate with the REST API
'''