#!/usr/bin/env python
# -*- coding: utf-8 -*-

from trigger import Trigger
from triggertype import TriggerType
from data.data import balance


class BalanceTrigger(Trigger):
    def __init__(self, trigger_id):
        super(BalanceTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.BALANCE

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
