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
    LAUNCHEVOLVER = 'LaunchEvolver'

    # Twitter
    LIKE_TWEET = 'Like tweet'
    UNLIKE_TWEET = 'Unlike tweet'
    RETWEET = 'Retweet'
    UNRETWEET = 'Unretweet'
    CREATE_TWEET = 'Create tweet'
    DELETE_TWEET = 'Delete tweet'
    SEND_DM_TWITTER = 'Send direct message on twitter'
    FOLLOW_ON_TWITTER = 'Follow on twitter'
    UNFOLLOW_ON_TWITTER = 'Unfollow on twitter'
