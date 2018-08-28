#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
from datetime import datetime

from helpers.loghelpers import LOG
from helpers.triggerhelpers import get_trigger
from trigger.triggertype import TriggerType
from helpers.actionhelpers import get_action
from action.actiontype import ActionType
from paymentprocessorscript import PaymentProcessorScript, PaymentRequest, NOTIFICATION_EMAIL
from data.data import transaction, balance, transactions


class PaymentProcessorPaymentStatus(PaymentProcessorScript):
    def __init__(self, *args, **kwargs):
        super(PaymentProcessorPaymentStatus, self).__init__(*args, **kwargs)

    def run(self):
        LOG.info('Running Spellbook Script: %s' % os.path.splitext(os.path.basename(__file__))[0])
        LOG.info('triggered: %s' % self.triggered)

        # If the trigger contains data, override the information in self.json
        if self.data is not None:
            if self.json is None:
                self.json = {}

            for key, value in self.data.items():
                self.json[key] = value

        if self.json is not None:

            if 'payment_request_id' not in self.json:
                LOG.error('Payment request json does not contain the payment request id!')
                return

            try:
                payment_request = PaymentRequest(payment_request_id=self.json['payment_request_id'])
            except Exception as ex:
                self.http_response = {'error': str(ex)}
                return

            if payment_request.txid is not None:
                tx_data = transaction(txid=payment_request.txid)
                tx = tx_data['transaction'] if 'transaction' in tx_data else {}
                payment_request.confirmations = tx['confirmations'] if 'confirmations' in tx else None

            else:
                # Fallback method in case the listener did not pick up the transaction (tx might have happened after listener timed out)
                balance_data = balance(address=payment_request.address)

                # If the final balance of the address is equal or more than the requested amount, assume the most recent transaction is the payment transaction
                # Note: there could be situations where multiple transactions are sent, those situations are not handled in this example app
                if 'balance' in balance_data and balance_data['balance']['final'] >= payment_request.amount_btc:
                    LOG.info('Current balance of %s: %s' % (payment_request.address, balance_data['balance']))
                    transactions_data = transactions(address=payment_request.address)
                    if 'transactions' in transactions_data:
                        tx = transactions_data['transactions'][-1]
                        payment_request.txid = tx['txid']
                        payment_request.confirmations = tx['confirmations']

            if payment_request.confirmations >= 6:
                payment_request.status = 'Confirmed'
            elif 1 <= payment_request.confirmations < 6:
                payment_request.status = '%s of 6 confirmations' % payment_request.confirmations

            payment_request.save()

            LOG.info('Retrieving status of payment request: %s' % payment_request.payment_request_id)
            LOG.info('Seller id: %s' % payment_request.seller_id)
            LOG.info('Fiat Amount: %s %s' % (payment_request.amount_fiat, payment_request.currency))
            LOG.info('BTC Amount: %s (price %s %s/BTC @ %s)' % (payment_request.amount_btc, payment_request.price_btc, payment_request.currency, datetime.fromtimestamp(payment_request.price_timestamp).strftime('%Y-%m-%d %H:%M:%S')))
            LOG.info('Note: %s' % payment_request.note)
            LOG.info('Address: %s' % payment_request.address)
            LOG.info('Status: %s' % payment_request.status)
            LOG.info('Txid: %s' % payment_request.txid)
            LOG.info('Confirmations: %s' % payment_request.confirmations)

            self.http_response = payment_request.json_encodable()

            if payment_request.status == 'Confirmed':
                # Send an email to notify the payment is confirmed
                action = get_action(action_id='tx_received_email', action_type=ActionType.SENDMAIL)
                action.mail_subject = 'Payment request %s is confirmed' % payment_request.payment_request_id
                action.mail_recipients = NOTIFICATION_EMAIL
                action.mail_body_template = os.path.join('PaymentProcessor', 'templates' 'PaymentConfirmed.txt')  # The spellbook will search for the template in the 'email_templates' and in the 'apps' directory, subdirectories are allowed, just need to specify the full path as shown here
                action.mail_variables = {'PAYMENT_REQUEST_ID': payment_request.payment_request_id,
                                         'SELLER_ID': payment_request.seller_id,
                                         'AMOUNT_FIAT': payment_request.amount_fiat,
                                         'CURRENCY': payment_request.currency,
                                         'NOTE': payment_request.note,
                                         'ADDRESS': payment_request.address,
                                         'AMOUNT_BTC': payment_request.amount_btc / 1e8,  # amount is in satoshis, display in BTC
                                         'PRICE_BTC': payment_request.price_btc,
                                         'PRICE_TIMESTAMP': datetime.fromtimestamp(payment_request.price_timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                                         'TXID': payment_request.txid}

                action.run()

                # Now that the payment is complete and confirmation email is sent, we can delete the trigger by setting
                # the self_destruct time to something in the past, this will delete the trigger next time check_triggers happens
                # We can not delete it right now because it is still in use by the spellbookserver
                trigger = get_trigger(trigger_id=payment_request.payment_request_id, trigger_type=TriggerType.BALANCE)
                trigger.self_destruct = int(time.time())-1
                trigger.save()

    def cleanup(self):
        pass
