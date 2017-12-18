#!/usr/bin/env python
# -*- coding: utf-8 -*-


class TriggerType(object):
    MANUAL = 'Manual'  # Triggers on a http request
    BALANCE = 'Balance'  # Triggers when an address has a final balance greater than or equal to a certain amount
    RECEIVED = 'Received'  # Triggers when an address has a total received balance greater than or equal to a certain amount
    SENT = 'Sent'  # Triggers when an address has a total sent balance greater than or equal to a certain amount
    BLOCK_HEIGHT = 'Block_height'  # Triggers when a certain block height is reached
