#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock


class TestSocialNetwork(unittest.TestCase):
    """Test cases for SocialNetwork class"""

    def test_social_network_constants(self):
        """Test SocialNetwork constants"""
        from helpers.socialmediahelpers import SocialNetwork
        
        self.assertEqual(SocialNetwork.TWITTER, 'Twitter')
        self.assertEqual(SocialNetwork.MASTODON, 'Mastodon')
        self.assertEqual(SocialNetwork.NOSTR, 'Nostr')


class TestTwitterClass(unittest.TestCase):
    """Test cases for Twitter class"""

    def test_twitter_init(self):
        """Test Twitter initialization"""
        from helpers.socialmediahelpers import Twitter, SocialNetwork
        
        twitter = Twitter()
        
        self.assertEqual(twitter.social_network, SocialNetwork.TWITTER)

    @patch('helpers.socialmediahelpers.get_trending_topics_twitter')
    def test_twitter_get_trending_topics(self, mock_get_trending):
        """Test Twitter get_trending_topics"""
        from helpers.socialmediahelpers import Twitter
        
        mock_get_trending.return_value = [('topic1', 100, 'query1', 'url1')]
        
        twitter = Twitter()
        result = twitter.get_trending_topics(woeid=1)
        
        mock_get_trending.assert_called_once_with(woeid=1)
        self.assertEqual(result, [('topic1', 100, 'query1', 'url1')])

    @patch('helpers.socialmediahelpers.get_tweets_by_id')
    @patch('helpers.socialmediahelpers.get_popular_tweet_ids')
    @patch('helpers.socialmediahelpers.LOG')
    def test_twitter_get_popular_statuses(self, mock_log, mock_get_ids, mock_get_tweets):
        """Test Twitter get_popular_statuses"""
        from helpers.socialmediahelpers import Twitter
        
        mock_get_ids.return_value = ['id1', 'id2', 'id3']
        mock_get_tweets.return_value = {'data': [{'id': 'id1'}]}
        
        twitter = Twitter()
        result = twitter.get_popular_statuses('test', limit=10)
        
        mock_get_ids.assert_called_once_with(searchtext='test', sort_by='retweet_count', limit=10)
        self.assertEqual(result, {'data': [{'id': 'id1'}]})


class TestMastodonClass(unittest.TestCase):
    """Test cases for Mastodon class"""

    def test_mastodon_init(self):
        """Test Mastodon initialization"""
        from helpers.socialmediahelpers import Mastodon, SocialNetwork
        
        mastodon = Mastodon()
        
        self.assertEqual(mastodon.social_network, SocialNetwork.MASTODON)

    @patch('helpers.socialmediahelpers.get_trending_topics_mastodon')
    def test_mastodon_get_trending_topics(self, mock_get_trending):
        """Test Mastodon get_trending_topics"""
        from helpers.socialmediahelpers import Mastodon
        
        mock_get_trending.return_value = [('topic1', 100, 'query1', 'url1')]
        
        mastodon = Mastodon()
        result = mastodon.get_trending_topics()
        
        mock_get_trending.assert_called_once()
        self.assertEqual(result, [('topic1', 100, 'query1', 'url1')])

    @patch('helpers.socialmediahelpers.get_toots_by_id')
    @patch('helpers.socialmediahelpers.get_popular_toot_ids')
    @patch('helpers.socialmediahelpers.LOG')
    def test_mastodon_get_popular_statuses(self, mock_log, mock_get_ids, mock_get_toots):
        """Test Mastodon get_popular_statuses"""
        from helpers.socialmediahelpers import Mastodon
        
        mock_get_ids.return_value = ['id1', 'id2', 'id3']
        mock_get_toots.return_value = {'data': [{'id': 'id1'}]}
        
        mastodon = Mastodon()
        result = mastodon.get_popular_statuses('test', limit=10)
        
        mock_get_ids.assert_called_once_with(topic='test', limit=10)
        self.assertEqual(result, {'data': [{'id': 'id1'}]})


if __name__ == '__main__':
    unittest.main()
