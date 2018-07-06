#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from datetime import datetime

from helpers.loghelpers import LOG
from trigger import Trigger
from triggertype import TriggerType
from validators.validators import valid_amount, valid_timestamp


class RecurringTrigger(Trigger):
    def __init__(self, trigger_id):
        super(RecurringTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.RECURRING
        self.next_activation = None
        self.begin_time = None
        self.end_time = None
        self.interval = None

    def conditions_fulfilled(self):
        if self.interval is None or self.begin_time is None or self.end_time is None:
            return False

        # Todo allow for recurring triggers without an end_time
        if self.end_time <= int(time.time()):
            LOG.info('Recurring trigger %s has reached its end time' % self.id)
            self.status = 'Succeeded'
            self.save()
            return False

        return self.next_activation <= int(time.time()) <= self.end_time

    def activate(self):
        super(RecurringTrigger, self).activate()

        if self.next_activation + self.interval <= self.end_time:
            self.next_activation += self.interval
            LOG.info('Setting next activation of recurring trigger %s to %s' % (self.id, datetime.fromtimestamp(self.next_activation)))
            self.save()

    def configure(self, **config):
        super(RecurringTrigger, self).configure(**config)

        if 'interval' in config and valid_amount(config['interval']):
            self.interval = config['interval']

        if 'begin_time' in config and valid_timestamp(config['begin_time']):
            self.begin_time = config['begin_time']

        if 'end_time' in config and valid_timestamp(config['end_time']):
            self.end_time = config['end_time']

        if 'next_activation' in config and valid_timestamp(config['next_activation']):
            self.next_activation = config['next_activation']
        elif self.begin_time is not None:
            self.next_activation = self.begin_time
            LOG.info('Setting first activation of recurring trigger %s to %s' % (self.id, datetime.fromtimestamp(self.next_activation)))

        self.multi = True

    def json_encodable(self):
        ret = super(RecurringTrigger, self).json_encodable()

        ret.update({
            'begin_time': self.begin_time,
            'end_time': self.end_time,
            'interval': self.interval,
            'next_activation': self.next_activation})
        return ret
