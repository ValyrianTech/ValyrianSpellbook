#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import requests
import time
from datetime import datetime

from helpers.loghelpers import LOG
from action.actiontype import ActionType
from helpers.actionhelpers import get_action
from helpers.triggerhelpers import get_trigger
from trigger.triggertype import TriggerType
from helpers.configurationhelpers import get_host, get_port, get_use_testnet
from helpers.hotwallethelpers import get_address_from_wallet
from paymentprocessorscript import PaymentProcessorScript, PaymentRequest, ACCOUNT, LISTENER_TIMEOUT, REQUEST_TIMEOUT


class PaymentProcessorNewPayment(PaymentProcessorScript):
    def __init__(self, *args, **kwargs):
        super(PaymentProcessorNewPayment, self).__init__(*args, **kwargs)

    def run(self):
        LOG.info('Running Spellbook Script: %s' % os.path.splitext(os.path.basename(__file__))[0])

        if self.json is not None:
            if 'seller_id' not in self.json:
                LOG.error('Payment request json does not contain the seller id')
                return

            if 'amount_fiat' not in self.json:
                LOG.error('Payment request json does not contain the fiat amount!')
                return

            if 'currency' not in self.json:
                LOG.error('Payment request json does not contain the fiat currency!')
                return
            elif self.json['currency'] not in ['EUR', 'USD']:
                LOG.error('Payment processor currently only supports EUR or USD as currency!')
                return

            # Create a new payment request
            payment_request = PaymentRequest()
            payment_request.seller_id = self.json['seller_id']
            payment_request.amount_fiat = self.json['amount_fiat']
            payment_request.currency = self.json['currency']
            payment_request.note = self.json['note'] if 'note' in self.json else None

            # Use the number of times the trigger has been triggered as the index in the hot wallet account
            payment_request.address = get_address_from_wallet(account=ACCOUNT, index=self.triggered)

            # Get the current BTC price from bitcoinaverage
            url = 'https://apiv2.bitcoinaverage.com/indices/global/ticker/BTC{currency}'.format(currency=payment_request.currency)
            LOG.info('Retrieving BTC%s price from bitcoinaverage.com' % payment_request.currency)
            LOG.info('GET %s' % url)
            try:
                r = requests.get(url=url)
                price_data = r.json()
            except Exception as ex:
                LOG.error('Unable to retrieve BTC price from bitcoinaverage.com: %s' % ex)
                self.http_response = {'error': 'Unable to convert %s amount to BTC amount' % payment_request.currency}
                return

            payment_request.price_btc = price_data['last']
            payment_request.price_timestamp = price_data['timestamp']

            if payment_request.price_btc == 0:
                LOG.error('BTC price can not be 0!')
                self.http_response = {'error': 'Unable to convert %s amount to BTC amount' % payment_request.currency}
                return

            payment_request.amount_btc = int(payment_request.amount_fiat/payment_request.price_btc * 1e8)

            LOG.info('Created new payment request: %s' % payment_request.payment_request_id)
            LOG.info('Fiat Amount: %s %s' % (payment_request.amount_fiat, payment_request.currency))
            LOG.info('BTC Amount: %s (price %s %s/BTC @ %s)' % (payment_request.amount_btc, payment_request.price_btc, payment_request.currency, datetime.fromtimestamp(payment_request.price_timestamp).strftime('%Y-%m-%d %H:%M:%S')))
            LOG.info('Note: %s' % payment_request.note)
            LOG.info('Address: %s' % payment_request.address)

            payment_request.save()

            # Set the HTTP response with the payment request details
            self.http_response = payment_request.json_encodable()

            # Create a trigger to monitor the balance of the address (This is a fallback in case the listener doesn't pick up the transaction)
            # The script will then check the number of confirmations of the transaction if one is received
            trigger = get_trigger(trigger_id=payment_request.payment_request_id, trigger_type=TriggerType.BALANCE)
            trigger.address = payment_request.address
            trigger.amount = payment_request.amount_btc

            trigger.script = 'PaymentProcessor\\PaymentProcessorPaymentStatus.py'
            trigger.data = {'payment_request_id': payment_request.payment_request_id}
            trigger.self_destruct = int(time.time()) + REQUEST_TIMEOUT
            trigger.status = 'Active'
            trigger.multi = True
            trigger.save()

            # Spawn up a separate process to listen for the payment transaction
            url = 'http://%s:%s/spellbook/triggers/PaymentProcessorTransactionReceived/post' % (get_host(), get_port())
            command = r'helpers\notify_transaction.py %s %s #txid#' % (url, payment_request.payment_request_id)

            # Construct the command for the listener so that it listens for any receiving transactions on the address and executes the notify_transaction program when
            # a transaction is detected and stop the listener if no tx happens within the timeout period.
            run_command = r'listeners\transaction_listener.py --address=%s --timeout=%s --exit --receive --command="%s"' % (payment_request.address, LISTENER_TIMEOUT, command)

            # If we are configured for testnet we must also add the --testnet flag to the listener
            if get_use_testnet():
                run_command += ' --testnet'

            action = get_action(action_id='start_listener', action_type=ActionType.SPAWNPROCESS)
            action.run_command = run_command

            # Run the action immediately instead of saving it, so we are not creating new actions with each request
            action.run()

    def cleanup(self):
        pass
