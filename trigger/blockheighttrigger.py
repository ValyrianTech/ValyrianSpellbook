#!/usr/bin/env python
# -*- coding: utf-8 -*-

from trigger import Trigger
from triggertype import TriggerType
from data.data import latest_block


class BlockHeightTrigger(Trigger):
    def __init__(self, trigger_id):
        super(BlockHeightTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.BLOCK_HEIGHT

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

