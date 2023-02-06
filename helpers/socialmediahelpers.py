#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import abstractmethod, ABCMeta

from helpers.loghelpers import LOG
from helpers.twitterhelpers import get_trending_topics as get_trending_topics_twitter, get_popular_tweet_ids, get_tweets_by_id
from helpers.mastodonhelpers import get_trending_topics as get_trending_topics_mastodon, get_popular_toot_ids, get_toots_by_id


class SocialNetwork(object):
    TWITTER = 'Twitter'
    MASTODON = 'Mastodon'
    NOSTR = 'Nostr'


class SocialMedia(object):
    __metaclass__ = ABCMeta

    def __init__(self, social_network: str = SocialNetwork.TWITTER):
        self.social_network = social_network

    @abstractmethod
    def get_trending_topics(self, woeid: int = 1) -> list:
        pass

    @abstractmethod
    def get_popular_statuses(self, topic: str, limit: int) -> list:
        pass


class Twitter(SocialMedia):
    def __init__(self):
        super().__init__(social_network=SocialNetwork.TWITTER)

    def get_trending_topics(self, woeid: int = 1) -> list:
        return get_trending_topics_twitter(woeid=woeid)

    def get_popular_statuses(self, topic: str, limit: int) -> dict:
        popular_tweet_ids = get_popular_tweet_ids(searchtext=topic, sort_by='retweet_count', limit=limit)
        LOG.info(f'top tweet ids: {popular_tweet_ids[:10]}')
        tweets = get_tweets_by_id(tweet_ids=popular_tweet_ids[:10])

        return tweets


class Mastodon(SocialMedia):
    def __init__(self):
        super().__init__(social_network=SocialNetwork.MASTODON)

    def get_trending_topics(self, woeid: int = 1) -> list:
        return get_trending_topics_mastodon()

    def get_popular_statuses(self, topic: str, limit: int) -> dict:
        popular_toot_ids = get_popular_toot_ids(topic=topic, limit=limit)
        LOG.info(f'top toot ids: {popular_toot_ids[:10]}')
        toots = get_toots_by_id(toot_ids=popular_toot_ids[:10])

        return toots
