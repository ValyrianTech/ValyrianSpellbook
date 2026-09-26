#!/usr/bin/env python
"""Trigger that activates at a specific timestamp."""

import time

from validators.validators import valid_timestamp

from .trigger import Trigger
from .triggertype import TriggerType


class TimestampTrigger(Trigger):
    """Trigger that activates at a specific timestamp."""
    def __init__(self, trigger_id):
        super().__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.TIMESTAMP
        self.timestamp = None

    def configure(self, **config):
        """Configure."""
        super().configure(**config)
        if 'timestamp' in config and valid_timestamp(config['timestamp']):
            self.timestamp = config['timestamp']

    def conditions_fulfilled(self):
        """Conditions fulfilled."""
        if self.timestamp is None:
            return False

        return self.timestamp <= time.time()

    def json_encodable(self):
        """Json encodable."""
        ret = super().json_encodable()
        ret.update({'timestamp': self.timestamp})
        return ret
