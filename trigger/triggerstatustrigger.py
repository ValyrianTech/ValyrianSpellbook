#!/usr/bin/env python
# -*- coding: utf-8 -*-

from trigger import Trigger
from triggertype import TriggerType


class TriggerStatusTrigger(Trigger):
    def __init__(self, trigger_id):
        super(TriggerStatusTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.TRIGGERSTATUS

    def conditions_fulfilled(self):
        # Avoid circular import here
        from triggerhelpers import get_trigger

        if self.previous_trigger is None or self.previous_trigger_status is None:
            return False

        previous_trigger = get_trigger(self.previous_trigger)

        return previous_trigger.triggered is True and previous_trigger.status == self.previous_trigger_status
