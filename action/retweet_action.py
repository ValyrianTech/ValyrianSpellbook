#!/usr/bin/env python

"""Action that retweets a tweet on Twitter."""

from helpers.loghelpers import LOG
from helpers.twitterhelpers import retweet

from .action import Action
from .actionresult import ActionResult
from .actiontype import ActionType


class RetweetAction(Action):
    """Action that retweets a tweet on Twitter."""
    def __init__(self, action_id):
        super().__init__(action_id=action_id)
        self.action_type = ActionType.RETWEET
        self.tweet_id = None

    def run(self):
        """
        Run the action

        :return: An ActionResult indicating success or failure
        """
        if self.tweet_id is None:
            return ActionResult(success=False)

        LOG.info(f'Retweeting tweet: {self.tweet_id}')

        try:
            retweet(tweet_id=self.tweet_id)
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to retweet tweet {self.tweet_id}: {ex}')
            return ActionResult(success=False)

        return ActionResult(success=True)

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['tweet_id']    : The id of the tweet to retweet
        """
        super().configure(**config)
        if 'tweet_id' in config:
            self.tweet_id = config['tweet_id']

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super().json_encodable()
        ret.update({'tweet_id': self.tweet_id})
        return ret
