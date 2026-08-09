#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Trigger that activates when funds are received at an address."""

from .trigger import Trigger
from .triggertype import TriggerType
from data.data import balance
from validators.validators import valid_address, valid_amount


class ReceivedTrigger(Trigger):
    """Trigger that activates when funds are received at an address."""
    def __init__(self, trigger_id):
        """  init  ."""
        super(ReceivedTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.RECEIVED
        self.address = None
        self.amount = None

    def conditions_fulfilled(self):
        """Conditions fulfilled."""
        if self.address is None or self.amount is None:
            return False

        data = balance(self.address)
        if isinstance(data, dict) and 'balance' in data and 'received' in data['balance']:
            total_received = data['balance']['received']
        else:
            # Something went wrong during retrieval of balance
            return False

        return True if self.amount <= total_received else False

    def configure(self, **config):
        """Configure."""
        super(ReceivedTrigger, self).configure(**config)
        if 'address' in config and valid_address(config['address']):
            self.address = config['address']

        if 'amount' in config and valid_amount(config['amount']):
            self.amount = config['amount']

    def json_encodable(self):
        """Json encodable."""
        ret = super(ReceivedTrigger, self).json_encodable()

        ret.update({
            'address': self.address,
            'amount': self.amount})
        return ret
