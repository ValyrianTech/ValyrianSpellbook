#!/usr/bin/env python
# -*- coding: utf-8 -*-

from trigger import Trigger
from triggertype import TriggerType
from data.data import latest_block
from validators.validators import valid_block_height, valid_amount


class BlockHeightTrigger(Trigger):
    def __init__(self, trigger_id):
        super(BlockHeightTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.BLOCK_HEIGHT
        self.block_height = None
        self.confirmations = 0

    def conditions_fulfilled(self):
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
        super(BlockHeightTrigger, self).configure(**config)
        if 'block_height' in config and valid_block_height(config['block_height']):
            self.block_height = config['block_height']

        if 'confirmations' in config and valid_amount(config['confirmations']):
            self.confirmations = config['confirmations']

    def json_encodable(self):
        ret = super(BlockHeightTrigger, self).json_encodable()

        ret.update({
            'block_height': self.block_height,
            'confirmations': self.confirmations})
        return ret
