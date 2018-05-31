#!/usr/bin/env python
# -*- coding: utf-8 -*-

from trigger import Trigger
from triggertype import TriggerType


class HTTPDeleteRequestTrigger(Trigger):
    def __init__(self, trigger_id):
        super(HTTPDeleteRequestTrigger, self).__init__(trigger_id=trigger_id)
        self.trigger_type = TriggerType.HTTPDELETEREQUEST
        self.json = None

    def conditions_fulfilled(self):
        # HTTP request triggers can only be triggered when a http request is received, so always return False
        return False

    def configure(self, **config):
        super(HTTPDeleteRequestTrigger, self).configure(**config)

    def json_encodable(self):
        ret = super(HTTPDeleteRequestTrigger, self).json_encodable()
        return ret

    def get_script_variables(self):
        ret = super(HTTPDeleteRequestTrigger, self).json_encodable()
        ret.update({'json': self.json})
        return ret

    def set_json_data(self, data):
        self.json = data
