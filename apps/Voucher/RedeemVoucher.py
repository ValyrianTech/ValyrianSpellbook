#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import requests

from action.actiontype import ActionType
from action.sendtransactionaction import TransactionType
from helpers.actionhelpers import get_action
from helpers.configurationhelpers import get_app_data_dir, get_use_testnet
from helpers.hotwallethelpers import get_address_from_wallet
from helpers.loghelpers import LOG
from spellbookscripts.spellbookscript import SpellbookScript
from validators.validators import valid_address, valid_bech32_address


LOG.info('loading script')

##########################################################################################################
# Voucher parameters
##########################################################################################################

# Set the account in the hot wallet to use for the Voucher service
WALLET_TYPE = 'BIP44'
BIP44_ACCOUNT = 0
ADDRESS_INDEX = 0

# Set the default fee type to use (Low, Medium, High)
FEE_TYPE = 'Medium'

# Set the notification email address
NOTIFICATION_EMAIL = 'info@valyrian.tech'

# Set the directory to use for data storage
VOUCHER_DIR = os.path.join(get_app_data_dir(), 'Voucher')
if not os.path.isdir(VOUCHER_DIR):
    os.makedirs(VOUCHER_DIR)
    LOG.info('Created Voucher dir')

# Set the amount in dollar to for each voucher
VOUCHER_AMOUNT_USD = 5.00

##########################################################################################################


class RedeemVoucher(SpellbookScript):

    def run(self, *args, **kwargs):
        LOG.info('Running Spellbook Script: %s' % os.path.splitext(os.path.basename(__file__))[0])

        if 'voucher' not in self.json:
            return self.exit_with_error(message='key "voucher" not found in http POST request')

        voucher = self.json['voucher']

        if 'address' not in self.json:
            return self.exit_with_error('key "address" not found in http POST request')

        if valid_address(address=self.json['address']) or valid_bech32_address(address=self.json['address']):
            address = self.json['address']
        else:
            return self.exit_with_error(message='Address %s is not valid!' % self.json['address'])

        # Get the current BTC price from bitcoinaverage
        url = 'https://apiv2.bitcoinaverage.com/indices/global/ticker/BTC{currency}'.format(currency='USD')
        LOG.info('Retrieving BTCUSD price from bitcoinaverage.com')
        LOG.info('GET %s' % url)
        try:
            r = requests.get(url=url)
            price_data = r.json()
        except Exception as ex:
            LOG.error('Unable to retrieve BTC price from bitcoinaverage.com: %s' % ex)
            self.http_response = {'error': 'Unable to convert USD amount to BTC amount'}
            return

        btc_price = price_data['last']
        amount_btc = round(number=VOUCHER_AMOUNT_USD/btc_price, ndigits=8)
        amount_sat = int(amount_btc * 1e8)

        active_vouchers_file = os.path.join(VOUCHER_DIR, 'active_vouchers.txt')

        # Create an empty file if it doesn't exist yet
        if not os.path.exists(active_vouchers_file):
            with open(active_vouchers_file, 'w') as output_file:
                output_file.write('')

        active_vouchers = []
        with open(active_vouchers_file, 'r') as input_file:
            for active_voucher in input_file.readlines():
                active_vouchers.append(active_voucher.strip())

        if voucher in active_vouchers:
            LOG.info('Valid voucher received, sending transaction now')
            txid = self.send_redeem_transaction(address=address, amount=amount_sat)

        else:
            return self.exit_with_error(message='Invalid voucher received: %s' % voucher)

        if txid is not None:
            with open(active_vouchers_file, 'w') as output_file:
                for active_voucher in active_vouchers:
                    if active_voucher != voucher:
                        output_file.write('%s\n' % active_voucher)

            self.send_notification_email(voucher=voucher, amount_usd=VOUCHER_AMOUNT_USD, amount_sat=amount_sat, btc_price=btc_price, txid=txid)
        else:
            self.send_alert_email(voucher=voucher, address=address, txid=txid)
            return self.exit_with_error(message='Unable to send redeem transaction')

        self.http_response = {'txid': txid,
                              'address': address,
                              'amount_usd': VOUCHER_AMOUNT_USD,
                              'amount_sat': amount_sat}

    def cleanup(self):
        pass

    @staticmethod
    def send_redeem_transaction(address, amount):
        # Create a new action to send a custom transaction with the OP_RETURN data
        action_id = 'RedeemVoucherAction'
        action = get_action(action_id=action_id, action_type=ActionType.SENDTRANSACTION)
        action.transaction_type = TransactionType.SEND2SINGLE
        action.wallet_type = WALLET_TYPE
        action.bip44_account = BIP44_ACCOUNT
        action.bip44_index = ADDRESS_INDEX
        action.sending_address = get_address_from_wallet(account=action.bip44_account, index=action.bip44_index)
        action.receiving_address = address
        action.amount = amount
        success = action.run()

        return action.txid if success is True else None

    @staticmethod
    def send_alert_email(voucher, address, txid):
        # Send an email to alert me something has gone wrong
        action = get_action(action_id='alert_email', action_type=ActionType.SENDMAIL)
        action.mail_subject = 'ALERT: Redeem voucher failed'
        action.mail_recipients = NOTIFICATION_EMAIL
        action.mail_body_template = os.path.join('Voucher', 'templates', 'Alert.txt')  # The spellbook will search for the template in the 'email_templates' and in the 'apps' directory, subdirectories are allowed, just need to specify the full path as shown here
        action.mail_variables = {'VOUCHER': voucher,
                                 'ADDRESS': address,
                                 'TXID': txid}

        return action.run()

    @staticmethod
    def send_notification_email(voucher, amount_usd, amount_sat, btc_price, txid):
        blockcypher_url = 'https://live.blockcypher.com/btc/tx/' if get_use_testnet() is False else 'https://live.blockcypher.com/btc-testnet/tx/'
        blockcypher_url += txid

        # Send an email to notify that a voucher has been redeemed
        action = get_action(action_id='alert_email', action_type=ActionType.SENDMAIL)
        action.mail_subject = 'A voucher has been redeemed'
        action.mail_recipients = NOTIFICATION_EMAIL
        action.mail_body_template = os.path.join('Voucher', 'templates', 'Notification.txt')  # The spellbook will search for the template in the 'email_templates' and in the 'apps' directory, subdirectories are allowed, just need to specify the full path as shown here
        action.mail_variables = {'VOUCHER': voucher,
                                 'AMOUNT_USD': amount_usd,
                                 'AMOUNT_SAT': amount_sat,
                                 'BTC_PRICE': btc_price,
                                 'TXID': blockcypher_url}

        return action.run()
