#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from trigger import Trigger
from triggertype import TriggerType
from validators.validators import valid_timestamp


class TimestampTrigger(Trigger):
    def __init__(self, trigger_id):
        super(TimestampTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.TIMESTAMP
        self.timestamp = None

    def configure(self, **config):
        super(TimestampTrigger, self).configure(**config)
        if 'timestamp' in config and valid_timestamp(config['timestamp']):
            self.timestamp = config['timestamp']

    def conditions_fulfilled(self):
        if self.timestamp is None:
            return False

        return self.timestamp <= time.time()

    def json_encodable(self):
        ret = super(TimestampTrigger, self).json_encodable()
        ret.update({'timestamp': self.timestamp})
        return ret
