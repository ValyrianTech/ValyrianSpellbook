#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .trigger import Trigger
from .triggertype import TriggerType
from data.data import balance
from validators.validators import valid_address, valid_amount


class SentTrigger(Trigger):
    def __init__(self, trigger_id):
        super(SentTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.SENT
        self.address = None
        self.amount = None

    def conditions_fulfilled(self):
        if self.address is None or self.amount is None:
            return False

        data = balance(self.address)
        if isinstance(data, dict) and 'balance' in data and 'sent' in data['balance']:
            total_sent = data['balance']['sent']
        else:
            # Something went wrong during retrieval of balance
            return False

        return True if self.amount <= total_sent else False

    def configure(self, **config):
        super(SentTrigger, self).configure(**config)
        if 'address' in config and valid_address(config['address']):
            self.address = config['address']

        if 'amount' in config and valid_amount(config['amount']):
            self.amount = config['amount']

    def json_encodable(self):
        ret = super(SentTrigger, self).json_encodable()

        ret.update({
            'address': self.address,
            'amount': self.amount})
        return ret
