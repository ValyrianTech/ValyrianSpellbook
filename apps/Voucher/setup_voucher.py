#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from helpers.configurationhelpers import get_host, get_port
from helpers.setupscripthelpers import spellbook_call, clean_up_triggers
from helpers.triggerhelpers import TriggerType


##########################################################################################################
# Voucher parameters
##########################################################################################################

# parameters are set in the Voucher.py script

# This setup script will create a HTTP POST request trigger that will be used each time a new Voucher request is made
# A HTTP POST request must contain the key 'voucher' and must contain a valid bitcoin address


# The script will then check if the voucher is valid and send some amount of bitcoin to the address


##########################################################################################################

print 'Setting up Voucher'
print '----------------------------------------------\n'

# --------------------------------------------------------------------------------------------------------
# Clean up old triggers and actions first
# --------------------------------------------------------------------------------------------------------
clean_up_triggers(trigger_ids=['RedeemVoucher'])

# --------------------------------------------------------------------------------------------------------
# Create Triggers
# --------------------------------------------------------------------------------------------------------
print '\nCreating Trigger...'
trigger_id = 'RedeemVoucher'
trigger_type = TriggerType.HTTPPOSTREQUEST
script = os.path.join('Voucher', 'RedeemVoucher.py')

response = spellbook_call('save_trigger', trigger_id,
                          '--type=%s' % trigger_type,
                          '--script=%s' % script,
                          '--multi',
                          '--status=Active')
assert response is None

print 'HTTP POST endpoint created'
print 'To create a new Voucher request, send a HTTP POST request with the voucher code as the "voucher" field ' \
      'in the request data and the bitcoin address as the "address" field to:'

url = 'http://{host}:{port}/api/RedeemVoucher'.format(host=get_host(), port=get_port())
print url
