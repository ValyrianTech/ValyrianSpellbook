#!/usr/bin/env python
# -*- coding: utf-8 -*-

from helpers.configurationhelpers import get_host, get_port
from helpers.setupscripthelpers import spellbook_call, clean_up_triggers
from helpers.triggerhelpers import TriggerType


##########################################################################################################
# Notary parameters
##########################################################################################################

# parameters are set in the Notary.py script

# This setup script will create a HTTP POST request trigger that will be used each time a new Notary request is made
# A HTTP POST request must contain the key 'message' and must contain a valid op_return message (max 80 characters)

# The script will then return json data containing the following keys: 'address', 'value', 'request_id', 'timeout'
# The script will create a new trigger to monitor payment and add an action that will send a transaction with the
# requested OP_RETURN output once the payment is confirmed

##########################################################################################################

print('Setting up Notary')
print('----------------------------------------------\n')

# --------------------------------------------------------------------------------------------------------
# Clean up old triggers and actions first
# --------------------------------------------------------------------------------------------------------
clean_up_triggers(trigger_ids=['Notary-request'])

# --------------------------------------------------------------------------------------------------------
# Create Triggers
# --------------------------------------------------------------------------------------------------------
print('\nCreating Trigger...')
trigger_id = 'Notary-request'
trigger_type = TriggerType.HTTPPOSTREQUEST
script = 'Notary\Notary.py'

response = spellbook_call('save_trigger', trigger_id,
                          '--type=%s' % trigger_type,
                          '--script=%s' % script,
                          '--multi')
assert response is None

print('HTTP POST endpoint created')
print('To create a new Notary request, send a HTTP POST request with the desired message as the "message" field in the request data to:')

url = 'http://{host}:{port}/spellbook/triggers/Notary-request/post'.format(host=get_host(), port=get_port())
print(url)
