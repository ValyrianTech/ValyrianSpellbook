#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import logging
from datetime import datetime

from trigger import Trigger
from triggertype import TriggerType


class RecurringTrigger(Trigger):
    def __init__(self, trigger_id):
        super(RecurringTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.RECURRING
        self.next_activation = None

    def conditions_fulfilled(self):
        if self.interval is None or self.begin_time is None or self.end_time is None:
            return False

        if self.end_time <= int(time.time()):
            logging.getLogger('Spellbook').info('Recurring trigger %s has reached its end time' % self.id)
            self.triggered = True
            self.save()
            return False

        return self.next_activation <= int(time.time()) <= self.end_time

    def activate(self):
        super(RecurringTrigger, self).activate()

        if self.triggered is True and self.next_activation + self.interval <= self.end_time:
            self.next_activation += self.interval
            logging.getLogger('Spellbook').info('Setting next activation of recurring trigger %s to %s' % (self.id, datetime.fromtimestamp(self.next_activation)))
            self.triggered = False
            self.save()


