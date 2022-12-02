#!/usr/bin/env python
# -*- coding: utf-8 -*-

from helpers.loghelpers import LOG
from .action import Action
from .actiontype import ActionType
from helpers.twitterhelpers import delete_tweet


class DeleteTweetAction(Action):
    def __init__(self, action_id):
        super(DeleteTweetAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.DELETE_TWEET
        self.tweet_id = None

    def run(self):
        """
        Run the action

        :return: True upon success, False upon failure
        """
        if self.tweet_id is None:
            return False

        LOG.info('Deleting tweet: %s' % self.tweet_id)

        try:
            delete_tweet(tweet_id=self.tweet_id)
        except Exception as ex:
            LOG.error(f'Unable to delete tweet {self.tweet_id}: {ex}')
            return False

        return True

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['tweet_id']    : The id of the tweet to like
        """
        super(DeleteTweetAction, self).configure(**config)
        if 'tweet_id' in config:
            self.tweet_id = config['tweet_id']

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super(DeleteTweetAction, self).json_encodable()
        ret.update({'tweet_id': self.tweet_id})
        return ret
