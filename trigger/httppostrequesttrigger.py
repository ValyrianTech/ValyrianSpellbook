#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Trigger that activates on HTTP POST requests."""

from .trigger import Trigger
from .triggertype import TriggerType


class HTTPPostRequestTrigger(Trigger):
    """Trigger that activates on HTTP POST requests."""
    def __init__(self, trigger_id):
        """  init  ."""
        super(HTTPPostRequestTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.HTTPPOSTREQUEST
        self.json = None

    def conditions_fulfilled(self):
        """Conditions fulfilled."""
        # HTTP request triggers can only be triggered when a http request is received, so always return False
        return False

    def configure(self, **config):
        """Configure."""
        super(HTTPPostRequestTrigger, self).configure(**config)

    def json_encodable(self):
        """Json encodable."""
        ret = super(HTTPPostRequestTrigger, self).json_encodable()
        return ret

    def get_script_variables(self):
        """Get script variables."""
        ret = super(HTTPPostRequestTrigger, self).json_encodable()
        ret.update({'json': self.json})
        return ret

    def set_json_data(self, data):
        """Set json data."""
        self.json = data
