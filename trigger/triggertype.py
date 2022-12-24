#!/usr/bin/env python
# -*- coding: utf-8 -*-


class TriggerType(object):
    MANUAL = 'Manual'  # Triggers on a http request
    BALANCE = 'Balance'  # Triggers when an address has a final balance greater than or equal to a certain amount
    RECEIVED = 'Received'  # Triggers when an address has a total received balance greater than or equal to a certain amount
    SENT = 'Sent'  # Triggers when an address has a total sent balance greater than or equal to a certain amount
    BLOCK_HEIGHT = 'Block_height'  # Triggers when a certain block height is reached
    TX_CONFIRMATION = 'Tx_confirmation'  # Triggers when a certain transaction reaches a certain amount of confirmations
    TIMESTAMP = 'Timestamp'  # Triggers when the time greater than or equal to a certain timestamp
    RECURRING = 'Recurring'  # Triggers each x seconds between a start time and end time
    TRIGGERSTATUS = 'TriggerStatus'  # Triggers when another trigger has activated and results in a status 'Succeeded' or 'Failed'
    DEADMANSSWITCH = 'DeadMansSwitch'  # Triggers after it has been activated and a period of time has elapsed without being reset
    SIGNEDMESSAGE = 'SignedMessage'  # Triggers when a verified signed message is received
    HTTPGETREQUEST = 'HTTPGetRequest'  # Triggers when a HTTP GET request is made
    HTTPPOSTREQUEST = 'HTTPPostRequest'  # Triggers when a HTTP POST request is made
    HTTPDELETEREQUEST = 'HTTPDeleteRequest'  # Triggers when a HTTP DELETE request is made
    HTTPOPTIONSREQUEST = 'HTTPOptionsRequest' # Triggers when a HTTP OPTIONS request is made
    # todo add utxotrigger
