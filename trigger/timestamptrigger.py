#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from trigger import Trigger
from triggertype import TriggerType


class TimestampTrigger(Trigger):
    def __init__(self, trigger_id):
        super(TimestampTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.TIMESTAMP

    def conditions_fulfilled(self):
        if self.timestamp is None:
            return False

        return self.timestamp <= time.time()
