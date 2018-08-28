#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from datetime import datetime

from helpers.loghelpers import LOG
from helpers.actionhelpers import get_action
from action.actiontype import ActionType
from paymentprocessorscript import PaymentProcessorScript, PaymentRequest, NOTIFICATION_EMAIL
from data.data import transaction


class PaymentProcessorTransactionReceived(PaymentProcessorScript):
    def __init__(self, *args, **kwargs):
        super(PaymentProcessorTransactionReceived, self).__init__(*args, **kwargs)

    def run(self):
        LOG.info('Running Spellbook Script: %s' % os.path.splitext(os.path.basename(__file__))[0])

        if self.json is not None:
            if 'payment_request_id' not in self.json:
                LOG.error('Payment request json does not contain the payment_request_id!')
                return

            if 'txid' not in self.json:
                LOG.error('Payment request json does not contain the txid!')
                return
            payment_request_id = self.json['payment_request_id']

            try:
                payment_request = PaymentRequest(payment_request_id=payment_request_id)
            except Exception as ex:
                self.http_response = {'error': str(ex)}
                return

            # Note: because this is just an example app, we will ignore the possibility of transaction malleability
            txid = self.json['txid']
            LOG.info('Payment request %s received a transaction: %s' % (payment_request_id, txid))

            tx_data = transaction(txid=txid)
            if 'transaction' not in tx_data:
                LOG.error('Unable to retrieve transaction %s' % txid)
                return

            tx = tx_data['transaction']

            transaction_received = False

            # Note: we are assuming there is only a single output to the payment address
            for tx_output in tx['outputs']:
                if tx_output['address'] == payment_request.address and tx_output['value'] == payment_request.amount_btc:
                    LOG.info('Transaction contains valid payment!')
                    transaction_received = True
                    payment_request.txid = txid
                    payment_request.status = 'Transaction received'
                elif tx_output['address'] == payment_request.address and tx_output['value'] < payment_request.amount_btc:
                    LOG.info('Transaction has less than the requested amount!')
                    payment_request.status = 'Insufficient amount received'
                elif tx_output['address'] == payment_request.address and tx_output['value'] > payment_request.amount_btc:
                    LOG.info('Transaction has more than the requested amount!')
                    transaction_received = True
                    payment_request.txid = txid
                    payment_request.status = 'Excess amount received'

            if transaction_received is False:
                LOG.info('Transaction does not contain a valid payment!')
                return

            payment_request.confirmations = tx['confirmations']
            if payment_request.confirmations >= 6:
                payment_request.status = 'Confirmed'

            payment_request.save()

            # Send an email to notify we received the transaction
            action = get_action(action_id='tx_received_email', action_type=ActionType.SENDMAIL)
            action.mail_subject = 'Transaction received for payment %s' % payment_request.payment_request_id
            action.mail_recipients = NOTIFICATION_EMAIL
            action.mail_body_template = os.path.join('PaymentProcessor', 'templates', 'TransactionReceived.txt')  # The spellbook will search for the template in the 'email_templates' and in the 'apps' directory, subdirectories are allowed, just need to specify the full path as shown here
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

    def cleanup(self):
        pass



