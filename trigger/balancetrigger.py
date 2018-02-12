#!/usr/bin/env python
# -*- coding: utf-8 -*-

from trigger import Trigger
from triggertype import TriggerType
from data.data import balance
from validators.validators import valid_address, valid_amount


class BalanceTrigger(Trigger):
    def __init__(self, trigger_id):
        super(BalanceTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.BALANCE
        self.address = None
        self.amount = None

    def conditions_fulfilled(self):
        if self.address is None or self.amount is None:
            return False

        data = balance(self.address)
        if isinstance(data, dict) and 'balance' in data and 'final' in data['balance']:
            final_balance = data['balance']['final']
        else:
            # Something went wrong during retrieval of balance
            return False

        return True if self.amount <= final_balance else False

    def configure(self, **config):
        super(BalanceTrigger, self).configure(**config)
        if 'address' in config and valid_address(config['address']):
            self.address = config['address']

        if 'amount' in config and valid_amount(config['amount']):
            self.amount = config['amount']

    def json_encodable(self):
        ret = super(BalanceTrigger, self).json_encodable()

        ret.update({
            'address': self.address,
            'amount': self.amount})
        return ret
