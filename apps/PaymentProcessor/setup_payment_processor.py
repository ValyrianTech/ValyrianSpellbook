#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from helpers.configurationhelpers import get_host, get_port
from helpers.setupscripthelpers import spellbook_call, clean_up_triggers


##########################################################################################################
# PaymentProcessor parameters
##########################################################################################################

# parameters are set in the paymentprocessorscript.py script

# This setup script will create a HTTP POST request trigger that will be used each time a new Payment request is made
# A HTTP POST request must contain the keys 'seller_id', 'amount_fiat', 'currency' and optionally 'note'

# The script will then return json data containing the details for the payment
# Example response:
# {
#     "address": "mxV4PVcniVJ3wNQYVSMNAKYBf11oBG35Wt",
#     "amount_btc": 2224155,
#     "amount_fiat": 135.99,
#     "confirmations": 0,
#     "currency": "EUR",
#     "note": 'Alpaca socks',
#     "payment_request_id": "PR-1533666275208",
#     "price_btc": 6114.23,
#     "price_timestamp": 1533666276,
#     "seller_id": "company1",
#     "status": "Created",
#     "txid": null
# }

# Upon a new payment request the script will start a transaction listener for the payment, once a transaction is detected the status will be updated
# There is also a HTTP GET trigger to request the status of a specified payment request

##########################################################################################################

print('Setting up PaymentProcessor')
print('----------------------------------------------\n')

# --------------------------------------------------------------------------------------------------------
# Clean up old triggers and actions first
# --------------------------------------------------------------------------------------------------------
clean_up_triggers(trigger_ids=['PaymentProcessorNewPayment', 'PaymentProcessorPaymentStatus', 'PaymentProcessorTransactionReceived'])

# --------------------------------------------------------------------------------------------------------
# Create Triggers
# --------------------------------------------------------------------------------------------------------
print('Creating Triggers...')
trigger_id = 'PaymentProcessorNewPayment'
trigger_type = 'HTTPPostRequest'
script = os.path.join('PaymentProcessor', 'PaymentProcessorNewPayment.py')

response = spellbook_call('save_trigger', trigger_id,
                          '-t=%s' % trigger_type,
                          '--multi',
                          '-sc=%s' % script)
assert response is None


trigger_id = 'PaymentProcessorPaymentStatus'
trigger_type = 'HTTPGetRequest'
script = os.path.join('PaymentProcessor', 'PaymentProcessorPaymentStatus.py')

response = spellbook_call('save_trigger', trigger_id,
                          '-t=%s' % trigger_type,
                          '--multi',
                          '-sc=%s' % script)
assert response is None

trigger_id = 'PaymentProcessorTransactionReceived'
trigger_type = 'HTTPPostRequest'
script = os.path.join('PaymentProcessor', 'PaymentProcessorTransactionReceived.py')

response = spellbook_call('save_trigger', trigger_id,
                          '-t=%s' % trigger_type,
                          '--multi',
                          '-sc=%s' % script)
assert response is None


# --------------------------------------------------------------------------------------------------------
print('\n\n')
print('HTTP POST endpoint created')
print('To create a new Payment request, send a HTTP POST request with the following fields: seller_id, amount_fiat, currency')
print('To this url:')

url = 'http://{host}:{port}/spellbook/triggers/PaymentProcessorNewPayment/post'.format(host=get_host(), port=get_port())
print(url)

# --------------------------------------------------------------------------------------------------------
print('\n\n')
print('HTTP GET endpoint created')
print('To get a payment status, send a HTTP GET request with the following fields: payment_request_id')
print('To this url:')

url = 'http://{host}:{port}/spellbook/triggers/PaymentProcessorPaymentStatus/get'.format(host=get_host(), port=get_port())
print(url)
