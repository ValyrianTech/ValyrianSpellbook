#!/usr/bin/env python

"""Trigger that activates when funds are sent from an address."""

from data.data import balance
from validators.validators import valid_address, valid_amount

from .trigger import Trigger
from .triggertype import TriggerType


class SentTrigger(Trigger):
    """Trigger that activates when funds are sent from an address."""
    def __init__(self, trigger_id):
        super().__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.SENT
        self.address = None
        self.amount = None

    def conditions_fulfilled(self):
        """Conditions fulfilled."""
        if self.address is None or self.amount is None:
            return False

        data = balance(self.address)
        if isinstance(data, dict) and 'balance' in data and 'sent' in data['balance']:
            total_sent = data['balance']['sent']
        else:
            # Something went wrong during retrieval of balance
            return False

        return self.amount <= total_sent

    def configure(self, **config):
        """Configure."""
        super().configure(**config)
        if 'address' in config and valid_address(config['address']):
            self.address = config['address']

        if 'amount' in config and valid_amount(config['amount']):
            self.amount = config['amount']

    def json_encodable(self):
        """Json encodable."""
        ret = super().json_encodable()

        ret.update({
            'address': self.address,
            'amount': self.amount})
        return ret
