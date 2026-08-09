#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Trigger that is activated manually by the user."""

from .trigger import Trigger
from .triggertype import TriggerType


class ManualTrigger(Trigger):
    """Trigger that is activated manually by the user."""
    def __init__(self, trigger_id):
        super(ManualTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.MANUAL

    def conditions_fulfilled(self):
        """Conditions fulfilled."""
        # Manual triggers can only be triggered manually, so always return False
        return False
