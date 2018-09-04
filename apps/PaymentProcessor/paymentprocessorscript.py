#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time

from helpers.loghelpers import LOG
from spellbookscripts.spellbookscript import SpellbookScript
from helpers.jsonhelpers import save_to_json_file, load_from_json_file
from helpers.configurationhelpers import get_app_data_dir


PAYMENT_PROCESSOR_DIR = os.path.join(get_app_data_dir(), 'PaymentProcessor')
if not os.path.isdir(PAYMENT_PROCESSOR_DIR):
    os.makedirs(PAYMENT_PROCESSOR_DIR)

##########################################################################################################
# PaymentProcessor parameters
##########################################################################################################

# Set the account in the hot wallet to use for the payments
ACCOUNT = 0

# Set a timeout for listening if a transaction is broadcasted to the network
# If a transaction is broadcasted after this timeout, you can still use the PaymentStatus HTTP GET request to update the status
LISTENER_TIMEOUT = 60*15  # Listen for 15 minutes

# Set a timeout for the payment request, if no payment has been received, the address will no longer be monitored
REQUEST_TIMEOUT = 60*60*24*7  # Payment requests are removed after 1 week

# Set an email address to notify when a transaction is received and when the payment is fully confirmed
NOTIFICATION_EMAIL = 'someone@example.com'

##########################################################################################################


class PaymentProcessorScript(SpellbookScript):
    def __init__(self, *args, **kwargs):
        super(PaymentProcessorScript, self).__init__(*args, **kwargs)

    def run(self):
        pass

    def cleanup(self):
        pass


class PaymentRequest(object):
    def __init__(self, payment_request_id=None):
        self.payment_request_id = payment_request_id if payment_request_id is not None else 'PR-%s' % int(time.time() * 1000)  # just a id based on the timestamp

        self.seller_id = None
        self.amount_fiat = 0
        self.currency = None
        self.price_btc = 0
        self.price_timestamp = None

        self.amount_btc = 0
        self.note = None
        self.status = 'Created'

        self.txid = None
        self.confirmations = 0

        self.address = None

        if payment_request_id is not None:
            self.load(payment_request_id=self.payment_request_id)

    def load(self, payment_request_id):
        try:
            data = load_from_json_file(filename=os.path.join(PAYMENT_PROCESSOR_DIR, '%s.json' % payment_request_id))
        except IOError as ex:
            LOG.error('Payment_request_id not found: %s' % ex)
            raise Exception('Unknown payment request id: %s' % payment_request_id)

        self.payment_request_id = payment_request_id
        self.seller_id = data['seller_id']
        self.amount_fiat = data['amount_fiat']
        self.currency = data['currency']
        self.price_btc = data['price_btc']
        self.price_timestamp = data['price_timestamp']
        self.amount_btc = data['amount_btc']
        self.note = data['note']

        self.status = data['status']
        self.address = data['address']
        self.txid = data['txid']
        self.confirmations = data['confirmations']

    def save(self):
        save_to_json_file(filename=os.path.join(PAYMENT_PROCESSOR_DIR, '%s.json' % self.payment_request_id), data=self.json_encodable())

    def json_encodable(self):
        return {'payment_request_id': self.payment_request_id,
                'seller_id': self.seller_id,
                'amount_fiat': self.amount_fiat,
                'currency': self.currency,
                'price_btc': self.price_btc,
                'price_timestamp': self.price_timestamp,
                'amount_btc': self.amount_btc,
                'note': self.note,
                'status': self.status,
                'address': self.address,
                'txid': self.txid,
                'confirmations': self.confirmations}
