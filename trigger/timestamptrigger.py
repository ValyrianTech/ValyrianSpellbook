#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Trigger that activates at a specific timestamp."""

import time

from .trigger import Trigger
from .triggertype import TriggerType
from validators.validators import valid_timestamp


class TimestampTrigger(Trigger):
    """Trigger that activates at a specific timestamp."""
    def __init__(self, trigger_id):
        """  init  ."""
        super(TimestampTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.TIMESTAMP
        self.timestamp = None

    def configure(self, **config):
        """Configure."""
        super(TimestampTrigger, self).configure(**config)
        if 'timestamp' in config and valid_timestamp(config['timestamp']):
            self.timestamp = config['timestamp']

    def conditions_fulfilled(self):
        """Conditions fulfilled."""
        if self.timestamp is None:
            return False

        return self.timestamp <= time.time()

    def json_encodable(self):
        """Json encodable."""
        ret = super(TimestampTrigger, self).json_encodable()
        ret.update({'timestamp': self.timestamp})
        return ret
