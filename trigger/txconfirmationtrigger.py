#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .trigger import Trigger
from .triggertype import TriggerType
from data.data import transaction
from validators.validators import valid_amount, valid_txid


class TxConfirmationTrigger(Trigger):
    def __init__(self, trigger_id):
        super(TxConfirmationTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.TX_CONFIRMATION
        self.txid = None
        self.confirmations = 1

    def conditions_fulfilled(self):
        if self.txid is None:
            return False

        data = transaction(txid=self.txid)
        if isinstance(data, dict) and 'transaction' in data and 'confirmations' in data['transaction']:
            confirmations = data['transaction']['confirmations']
        else:
            # Something went wrong during retrieval of transaction
            return False

        return True if self.confirmations <= confirmations else False

    def configure(self, **config):
        super(TxConfirmationTrigger, self).configure(**config)
        if 'txid' in config and valid_txid(config['txid']):
            self.txid = config['txid']

        if 'confirmations' in config and valid_amount(config['confirmations']):
            self.confirmations = config['confirmations']

    def json_encodable(self):
        ret = super(TxConfirmationTrigger, self).json_encodable()

        ret.update({
            'txid': self.txid,
            'confirmations': self.confirmations})
        return ret
