#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from abc import abstractmethod, ABCMeta
from datetime import datetime

from jsonhelpers import save_to_json_file
from validators.validators import valid_action_type, valid_address, valid_percentage, valid_xpub, valid_amount, valid_op_return, valid_block_height
from validators.validators import valid_transaction_type
from hot_wallet_helpers import get_hot_wallet
from BIP44.BIP44 import get_xpub_key, get_address_from_xpub
from transactiontype import TransactionType
from configurationhelpers import get_minimum_output_value


ACTIONS_DIR = 'json/public/actions'


class Action(object):
    __metaclass__ = ABCMeta

    def __init__(self, action_id):
        self.id = action_id
        self.action_type = None
        self.created = None
        self.run_command = None
        self.mail_recipients = None
        self.mail_subject = None
        self.mail_body_template = None
        self.webhook = None
        self.reveal_text = None
        self.reveal_link = None
        self.allow_reveal = False
        self.fee_address = None
        self.fee_percentage = 0
        self.fee_minimum_amount = 1000
        self.wallet_type = None
        self.sending_address = None
        self.bip44_account = None
        self.bip44_index = None
        self.receiving_address = None
        self.receiving_xpub = None
        self.amount = 0
        self.minimum_amount = None
        self.op_return_data = None
        self.change_address = None
        self.registration_address = None
        self.registration_block_height = None
        self.registration_xpub = None
        self.distribution = None
        self.transaction_type = TransactionType.SEND2MANY
        self.minimum_output_value = get_minimum_output_value()

    def configure(self, **config):
        self.created = datetime.fromtimestamp(config['created']) if 'created' in config else datetime.now()

        if 'action_type' in config and valid_action_type(config['action_type']):
            self.action_type = config['action_type']

        if 'run_command' in config:
            self.run_command = config['run_command']

        if 'mail_recipients' in config:
            self.mail_recipients = config['mail_recipients']

        if 'mail_subject' in config:
            self.mail_subject = config['mail_subject']

        if 'mail_body_template' in config:
            self.mail_body_template = config['mail_body_template']

        if 'webhook' in config:
            self.webhook = config['webhook']

        if 'reveal_text' in config:
            self.reveal_text = config['reveal_text']

        if 'reveal_link' in config:
            self.reveal_link = config['reveal_link']

        if 'allow_reveal' in config:
            self.allow_reveal = config['allow_reveal']

        if 'fee_address' in config and valid_address(config['fee_address']):
            self.fee_address = config['fee_address']

        if 'fee_percentage' in config and valid_percentage(config['fee_percentage']):
            self.fee_percentage = config['fee_percentage']

        if 'wallet_type' in config and config['wallet_type'] in ['Single', 'BIP44']:
            self.wallet_type = config['wallet_type']

        if 'sending_address' in config and valid_address(config['sending_address']):
            self.sending_address = config['sending_address']

        if 'bip44_account' in config:
            self.bip44_account = config['bip44_account']

        if 'bip44_index' in config:
            self.bip44_index = config['bip44_index']

        if 'receiving_address' in config and valid_address(config['receiving_address']):
            self.receiving_address = config['receiving_address']

        if 'receiving_xpub' in config and valid_xpub(config['receiving_xpub']):
            self.receiving_xpub = config['receiving_xpub']

        if 'amount' in config and valid_amount(config['amount']):
            self.amount = config['amount']

        if 'minimum_amount' in config and valid_amount(config['minimum_amount']):
            self.minimum_amount = config['minimum_amount']

        if 'op_return_data' in config and valid_op_return(config['op_return_data']):
            self.op_return_data = config['op_return_data']

        if 'change_address' in config and valid_address(config['change_address']):
            self.receiving_address = config['change_address']

        if 'transaction_type' in config and valid_transaction_type(config['transaction_type']):
            self.transaction_type = config['transaction_type']

        if 'minimum_output_value' in config and valid_amount(config['minimum_output_value']):
            self.minimum_output_value = config['minimum_output_value']

        if 'registration_address' in config and valid_address(config['registration_address']):
            self.registration_address = config['registration_address']

        if 'registration_block_height' in config and valid_block_height(config['registration_block_height']):
            self.registration_block_height = config['registration_block_height']

        if 'registration_xpub' in config and valid_xpub(config['registration_xpub']):
            self.registration_xpub = config['registration_xpub']

        # fill in the address in case of a BIP44 hot wallet
        if self.wallet_type == 'BIP44':
            hot_wallet = get_hot_wallet()
            xpub_key = get_xpub_key(mnemonic=' '.join(hot_wallet['mnemonic']), passphrase=hot_wallet['passphrase'], account=self.bip44_account)

            # Explicitly delete the local variable hot wallet from memory as soon as possible for security reasons
            del hot_wallet

            self.sending_address = get_address_from_xpub(xpub=xpub_key, i=self.bip44_index)

    def save(self):
        save_to_json_file(os.path.join(ACTIONS_DIR, '%s.json' % self.id), self.json_encodable())

    def json_encodable(self):
        return {'id': self.id,
                'action_type': self.action_type,
                'created': int(time.mktime(self.created.timetuple())),
                'run_command': self.run_command,
                'mail_recipients': self.mail_recipients,
                'mail_subject': self.mail_subject,
                'mail_body_template': self.mail_body_template,
                'webhook': self.webhook,
                'reveal_text': self.reveal_text,
                'reveal_link': self.reveal_link,
                'allow_reveal': self.allow_reveal,
                'fee_address': self.fee_address,
                'fee_percentage': self.fee_percentage,
                'wallet_type': self.wallet_type,
                'sending_address': self.sending_address,
                'bip44_account': self.bip44_account,
                'bip44_index': self.bip44_index,
                'receiving_address': self.receiving_address,
                'receiving_xpub': self.receiving_xpub,
                'amount': self.amount,
                'minimum_amount': self.minimum_amount,
                'op_return_data': self.op_return_data,
                'change_address': self.change_address,
                'transaction_type': self.transaction_type,
                'minimum_output_value': self.minimum_output_value,
                'registration_address': self.registration_address,
                'registration_block_height': self.registration_block_height,
                'registration_xpub': self.registration_xpub}

    @abstractmethod
    def run(self):
        """
        Run the action

        :return: True upon success, False upon failure
        """
        pass
