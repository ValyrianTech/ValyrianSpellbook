#!/usr/bin/env python
# -*- coding: utf-8 -*-

from helpers.loghelpers import LOG
from .action import Action
from .actiontype import ActionType
from helpers.twitterhelpers import like_tweet


class LikeTweetAction(Action):
    def __init__(self, action_id):
        super(LikeTweetAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.LIKE_TWEET
        self.tweet_id = None

    def run(self):
        """
        Run the action

        :return: True upon success, False upon failure
        """
        if self.tweet_id is None:
            return False

        LOG.info('Liking tweet: %s' % self.tweet_id)

        try:
            like_tweet(tweet_id=self.tweet_id)
        except Exception as ex:
            LOG.error(f'Unable to like tweet {self.tweet_id}: {ex}')
            return False

        return True

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['tweet_id']    : The id of the tweet to like
        """
        super(LikeTweetAction, self).configure(**config)
        if 'tweet_id' in config:
            self.tweet_id = config['tweet_id']

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super(LikeTweetAction, self).json_encodable()
        ret.update({'tweet_id': self.tweet_id})
        return ret
