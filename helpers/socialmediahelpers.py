#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Abstract social media interface with Twitter and Mastodon implementations."""
from abc import abstractmethod, ABCMeta

from helpers.loghelpers import LOG
from helpers.twitterhelpers import get_trending_topics as get_trending_topics_twitter, get_popular_tweet_ids, get_tweets_by_id
from helpers.mastodonhelpers import get_trending_topics as get_trending_topics_mastodon, get_popular_toot_ids, get_toots_by_id


class SocialNetwork(object):
    """Constants for supported social network names."""

    TWITTER = 'Twitter'
    MASTODON = 'Mastodon'
    NOSTR = 'Nostr'


class SocialMedia(object):
    """
    Abstract base class for social media platform interactions.

    Initializes with the name of the social network.
    """

    __metaclass__ = ABCMeta

    def __init__(self, social_network: str = SocialNetwork.TWITTER):
        self.social_network = social_network

    @abstractmethod
    def get_trending_topics(self, woeid: int = 1) -> list:
        """Retrieve trending topics for the given location (woeid)."""
        pass

    @abstractmethod
    def get_popular_statuses(self, topic: str, limit: int) -> dict:
        """Retrieve popular statuses for the given topic."""
        pass


class Twitter(SocialMedia):
    """
    Twitter implementation of the SocialMedia abstract class.

    Initializes the Twitter social media adapter.
    """

    def __init__(self):
        super().__init__(social_network=SocialNetwork.TWITTER)

    def get_trending_topics(self, woeid: int = 1) -> list:
        """Retrieve trending topics from Twitter for the given woeid."""
        return get_trending_topics_twitter(woeid=woeid)

    def get_popular_statuses(self, topic: str, limit: int) -> dict:
        """Retrieve popular tweets for the given topic sorted by retweet count."""
        popular_tweet_ids = get_popular_tweet_ids(searchtext=topic, sort_by='retweet_count', limit=limit)
        LOG.info(f'top tweet ids: {popular_tweet_ids[:10]}')
        tweets = get_tweets_by_id(tweet_ids=popular_tweet_ids[:10])

        return tweets


class Mastodon(SocialMedia):
    """
    Mastodon implementation of the SocialMedia abstract class.

    Initializes the Mastodon social media adapter.
    """

    def __init__(self):
        super().__init__(social_network=SocialNetwork.MASTODON)

    def get_trending_topics(self, woeid: int = 1) -> list:
        """Retrieve trending topics from Mastodon."""
        return get_trending_topics_mastodon()

    def get_popular_statuses(self, topic: str, limit: int) -> dict:
        """Retrieve popular toots for the given topic."""
        popular_toot_ids = get_popular_toot_ids(topic=topic, limit=limit)
        LOG.info(f'top toot ids: {popular_toot_ids[:10]}')
        toots = get_toots_by_id(toot_ids=popular_toot_ids[:10])

        return toots
