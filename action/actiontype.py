#!/usr/bin/env python
# -*- coding: utf-8 -*-


class ActionType(object):
    COMMAND = 'Command'
    SPAWNPROCESS = 'SpawnProcess'
    REVEALSECRET = 'RevealSecret'
    SENDMAIL = 'SendMail'
    WEBHOOK = 'Webhook'
    SENDTRANSACTION = 'SendTransaction'
    DELETETRIGGER = 'DeleteTrigger'
    # Todo SendTweetAction
