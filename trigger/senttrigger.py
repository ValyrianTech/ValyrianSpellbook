#!/usr/bin/env python
# -*- coding: utf-8 -*-

from trigger import Trigger
from triggertype import TriggerType
from data.data import balance


class SentTrigger(Trigger):
    def __init__(self, trigger_id):
        super(SentTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.SENT

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
