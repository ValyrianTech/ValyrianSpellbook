#!/usr/bin/env python
"""Trigger that activates on a recurring schedule."""

import time
from datetime import datetime, timezone

from helpers.loghelpers import LOG
from validators.validators import valid_amount, valid_timestamp

from .trigger import Trigger
from .triggertype import TriggerType


class RecurringTrigger(Trigger):
    """Trigger that activates on a recurring schedule."""
    def __init__(self, trigger_id):
        super().__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.RECURRING
        self.next_activation = None
        self.begin_time = None
        self.end_time = None
        self.interval = None

    def conditions_fulfilled(self):
        """Conditions fulfilled."""
        if self.interval is None or self.begin_time is None:
            return False

        if self.end_time is None:
            return self.next_activation <= int(time.time())

        elif self.end_time <= int(time.time()):
            LOG.info(f'Recurring trigger {self.id} has reached its end time')
            self.status = 'Succeeded'
            self.save()
            return False

        return self.next_activation <= int(time.time()) <= self.end_time

    def activate(self):
        """Activate."""
        super().activate()

        if self.end_time is None or self.next_activation + self.interval <= self.end_time:
            self.next_activation += self.interval  # Todo what if trigger was activated after interval has passed??
            LOG.info(f'Setting next activation of recurring trigger {self.id} to {datetime.fromtimestamp(self.next_activation, tz=timezone.utc)}')
            self.save()

    def configure(self, **config):
        """Configure."""
        super().configure(**config)

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
            LOG.info(f'Setting first activation of recurring trigger {self.id} to {datetime.fromtimestamp(self.next_activation, tz=timezone.utc)}')

        self.multi = True

    def json_encodable(self):
        """Json encodable."""
        ret = super().json_encodable()

        ret.update({
            'begin_time': self.begin_time,
            'end_time': self.end_time,
            'interval': self.interval,
            'next_activation': self.next_activation})
        return ret
