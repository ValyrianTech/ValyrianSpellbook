#!/usr/bin/env python

"""Trigger that activates at a specific block height."""

from data.data import latest_block
from validators.validators import valid_amount, valid_block_height

from .trigger import Trigger
from .triggertype import TriggerType


class BlockHeightTrigger(Trigger):
    """Trigger that activates at a specific block height."""
    def __init__(self, trigger_id):
        super().__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.BLOCK_HEIGHT
        self.block_height = None
        self.confirmations = 0

    def conditions_fulfilled(self):
        """Conditions fulfilled."""
        if self.block_height is None:
            return False

        data = latest_block()
        if isinstance(data, dict) and 'block' in data and 'height' in data['block']:
            latest_block_height = data['block']['height']
        else:
            # Something went wrong during retrieval of latest block height
            return False

        return True if self.block_height + self.confirmations <= latest_block_height else False

    def configure(self, **config):
        """Configure."""
        super().configure(**config)
        if 'block_height' in config and valid_block_height(config['block_height']):
            self.block_height = config['block_height']

        if 'confirmations' in config and valid_amount(config['confirmations']):
            self.confirmations = config['confirmations']

    def json_encodable(self):
        """Json encodable."""
        ret = super().json_encodable()

        ret.update({
            'block_height': self.block_height,
            'confirmations': self.confirmations})
        return ret
