#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Trigger that activates on HTTP DELETE requests."""

from .trigger import Trigger
from .triggertype import TriggerType


class HTTPDeleteRequestTrigger(Trigger):
    """Trigger that activates on HTTP DELETE requests."""
    def __init__(self, trigger_id):
        super(HTTPDeleteRequestTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.HTTPDELETEREQUEST
        self.json = None

    def conditions_fulfilled(self):
        """Conditions fulfilled."""
        # HTTP request triggers can only be triggered when a http request is received, so always return False
        return False

    def configure(self, **config):
        """Configure."""
        super(HTTPDeleteRequestTrigger, self).configure(**config)

    def json_encodable(self):
        """Json encodable."""
        ret = super(HTTPDeleteRequestTrigger, self).json_encodable()
        return ret

    def get_script_variables(self):
        """Get script variables."""
        ret = super(HTTPDeleteRequestTrigger, self).json_encodable()
        ret.update({'json': self.json})
        return ret

    def set_json_data(self, data):
        """Set json data."""
        self.json = data
