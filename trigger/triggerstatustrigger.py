#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Trigger that activates based on another trigger's status."""

from .trigger import Trigger
from .triggertype import TriggerType


class TriggerStatusTrigger(Trigger):
    """Trigger that activates based on another trigger's status."""
    def __init__(self, trigger_id):
        super(TriggerStatusTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.TRIGGERSTATUS
        self.previous_trigger = None
        self.previous_trigger_status = None

    def conditions_fulfilled(self):
        """Conditions fulfilled."""
        # Avoid circular import here
        from helpers.triggerhelpers import get_trigger

        if self.previous_trigger is None or self.previous_trigger_status is None:
            return False

        previous_trigger = get_trigger(self.previous_trigger)

        return previous_trigger.triggered > 0 and previous_trigger.status == self.previous_trigger_status

    def configure(self, **config):
        """Configure."""
        super(TriggerStatusTrigger, self).configure(**config)
        if 'previous_trigger' in config:
            self.previous_trigger = config['previous_trigger']

        if 'previous_trigger_status' in config and config['previous_trigger_status'] in ['Succeeded', 'Failed']:
            self.previous_trigger_status = config['previous_trigger_status']

    def json_encodable(self):
        """Json encodable."""
        ret = super(TriggerStatusTrigger, self).json_encodable()

        ret.update({
            'previous_trigger': self.previous_trigger,
            'previous_trigger_status': self.previous_trigger_status})
        return ret
