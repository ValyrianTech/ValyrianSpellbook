#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock
import sys

# Mock tweepy before importing twitterhelpers
mock_tweepy = MagicMock()
sys.modules['tweepy'] = mock_tweepy
sys.modules['tweepy.tweet'] = MagicMock()
sys.modules['tweepy.direct_message_event'] = MagicMock()


class TestGetTwitterApi(unittest.TestCase):
    """Test cases for get_twitter_api function"""

    @patch('helpers.twitterhelpers.get_twitter_consumer_key', return_value='consumer_key')
    @patch('helpers.twitterhelpers.get_twitter_consumer_secret', return_value='consumer_secret')
    @patch('helpers.twitterhelpers.get_twitter_access_token', return_value='access_token')
    @patch('helpers.twitterhelpers.get_twitter_access_token_secret', return_value='access_token_secret')
    @patch('helpers.twitterhelpers.tweepy.OAuth1UserHandler')
    @patch('helpers.twitterhelpers.tweepy.API')
    @patch('builtins.print')
    def test_get_twitter_api_success(self, mock_print, mock_api, mock_auth, mock_secret, 
                                      mock_token, mock_consumer_secret, mock_consumer_key):
        """Test successful Twitter API authentication"""
        from helpers.twitterhelpers import get_twitter_api
        
        mock_api_instance = MagicMock()
        mock_api.return_value = mock_api_instance
        
        result = get_twitter_api()
        
        self.assertEqual(result, mock_api_instance)
        mock_api_instance.verify_credentials.assert_called_once()

    @patch('helpers.twitterhelpers.get_twitter_consumer_key', return_value='consumer_key')
    @patch('helpers.twitterhelpers.get_twitter_consumer_secret', return_value='consumer_secret')
    @patch('helpers.twitterhelpers.get_twitter_access_token', return_value='access_token')
    @patch('helpers.twitterhelpers.get_twitter_access_token_secret', return_value='access_token_secret')
    @patch('helpers.twitterhelpers.tweepy.OAuth1UserHandler')
    @patch('helpers.twitterhelpers.tweepy.API')
    @patch('builtins.print')
    def test_get_twitter_api_auth_failure(self, mock_print, mock_api, mock_auth, mock_secret,
                                           mock_token, mock_consumer_secret, mock_consumer_key):
        """Test Twitter API authentication failure"""
        from helpers.twitterhelpers import get_twitter_api
        
        mock_api_instance = MagicMock()
        mock_api_instance.verify_credentials.side_effect = Exception('Auth failed')
        mock_api.return_value = mock_api_instance
        
        result = get_twitter_api()
        
        self.assertIsNone(result)


class TestGetRecentTweets(unittest.TestCase):
    """Test cases for get_recent_tweets function"""

    def test_get_recent_tweets_invalid_sort_by(self):
        """Test get_recent_tweets with invalid sort_by parameter"""
        from helpers.twitterhelpers import get_recent_tweets
        
        with self.assertRaises(Exception) as context:
            get_recent_tweets('test', 'invalid_sort')
        
        self.assertIn('Invalid sort_by value', str(context.exception))

    @patch('helpers.twitterhelpers.get_tweets')
    def test_get_recent_tweets_valid_sort_by(self, mock_get_tweets):
        """Test get_recent_tweets with valid sort_by parameter"""
        from helpers.twitterhelpers import get_recent_tweets
        
        mock_tweets = [
            {'public_metrics': {'like_count': 10}},
            {'public_metrics': {'like_count': 50}},
            {'public_metrics': {'like_count': 25}}
        ]
        mock_get_tweets.return_value = mock_tweets
        
        result = get_recent_tweets('test', 'like_count', limit=3)
        
        # Should be sorted by like_count descending
        self.assertEqual(result[0]['public_metrics']['like_count'], 50)
        self.assertEqual(result[1]['public_metrics']['like_count'], 25)
        self.assertEqual(result[2]['public_metrics']['like_count'], 10)


class TestGetPopularTweetIds(unittest.TestCase):
    """Test cases for get_popular_tweet_ids function"""

    @patch('helpers.twitterhelpers.get_recent_tweets')
    def test_get_popular_tweet_ids_filters_sensitive(self, mock_recent):
        """Test that sensitive tweets are filtered out"""
        from helpers.twitterhelpers import get_popular_tweet_ids
        
        mock_recent.return_value = [
            {'possibly_sensitive': True, 'referenced_tweets': [{'type': 'retweeted', 'id': '123'}]},
            {'possibly_sensitive': False, 'referenced_tweets': [{'type': 'retweeted', 'id': '456'}]}
        ]
        
        result = get_popular_tweet_ids('test', 'like_count')
        
        self.assertNotIn('123', result)
        self.assertIn('456', result)

    @patch('helpers.twitterhelpers.get_recent_tweets')
    def test_get_popular_tweet_ids_no_duplicates(self, mock_recent):
        """Test that duplicate tweet IDs are not added"""
        from helpers.twitterhelpers import get_popular_tweet_ids
        
        mock_recent.return_value = [
            {'possibly_sensitive': False, 'referenced_tweets': [{'type': 'retweeted', 'id': '123'}]},
            {'possibly_sensitive': False, 'referenced_tweets': [{'type': 'retweeted', 'id': '123'}]}
        ]
        
        result = get_popular_tweet_ids('test', 'like_count')
        
        self.assertEqual(result.count('123'), 1)


class TestGetTweetsById(unittest.TestCase):
    """Test cases for get_tweets_by_id function"""

    @patch('helpers.twitterhelpers.client')
    def test_get_tweets_by_id_empty_list(self, mock_client):
        """Test get_tweets_by_id with empty list"""
        from helpers.twitterhelpers import get_tweets_by_id
        
        result = get_tweets_by_id([])
        
        self.assertEqual(result, {})
        mock_client.get_tweets.assert_not_called()

    @patch('helpers.twitterhelpers.client')
    def test_get_tweets_by_id_with_ids(self, mock_client):
        """Test get_tweets_by_id with tweet IDs"""
        from helpers.twitterhelpers import get_tweets_by_id
        
        mock_client.get_tweets.return_value = {'data': [{'id': '123'}]}
        
        result = get_tweets_by_id(['123', '456'])
        
        mock_client.get_tweets.assert_called_once()


class TestGetUsers(unittest.TestCase):
    """Test cases for get_users function"""

    @patch('helpers.twitterhelpers.get_twitter_bearer_token', return_value='bearer_token')
    @patch('helpers.twitterhelpers.tweepy.Client')
    def test_get_users_valid_ids(self, mock_client_class, mock_bearer):
        """Test get_users with valid IDs"""
        from helpers.twitterhelpers import get_users
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [{'id': '123', 'name': 'Test User'}]
        mock_client.get_users.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        result = get_users(['123'])
        
        self.assertEqual(result, [{'id': '123', 'name': 'Test User'}])

    @patch('helpers.twitterhelpers.get_twitter_bearer_token', return_value='bearer_token')
    @patch('helpers.twitterhelpers.tweepy.Client')
    def test_get_users_empty_list(self, mock_client_class, mock_bearer):
        """Test get_users with empty list"""
        from helpers.twitterhelpers import get_users
        
        result = get_users([])
        
        self.assertEqual(result, [])

    @patch('helpers.twitterhelpers.get_twitter_bearer_token', return_value='bearer_token')
    @patch('helpers.twitterhelpers.tweepy.Client')
    def test_get_users_too_many_ids(self, mock_client_class, mock_bearer):
        """Test get_users with more than 100 IDs"""
        from helpers.twitterhelpers import get_users
        
        # Create list of 101 IDs
        ids = [str(i) for i in range(101)]
        
        result = get_users(ids)
        
        self.assertEqual(result, [])


class TestGetUser(unittest.TestCase):
    """Test cases for get_user function"""

    @patch('helpers.twitterhelpers.client')
    def test_get_user_no_params(self, mock_client):
        """Test get_user with no parameters raises exception"""
        from helpers.twitterhelpers import get_user
        
        with self.assertRaises(Exception) as context:
            get_user()
        
        self.assertIn('Must supply either user_id or user_name', str(context.exception))

    @patch('helpers.twitterhelpers.client')
    def test_get_user_with_user_id(self, mock_client):
        """Test get_user with user_id"""
        from helpers.twitterhelpers import get_user
        
        mock_client.get_user.return_value = {'data': {'id': '123'}}
        
        result = get_user(user_id='123')
        
        mock_client.get_user.assert_called_once()

    @patch('helpers.twitterhelpers.client')
    def test_get_user_with_username(self, mock_client):
        """Test get_user with username"""
        from helpers.twitterhelpers import get_user
        
        mock_client.get_user.return_value = {'data': {'username': 'testuser'}}
        
        result = get_user(user_name='testuser')
        
        mock_client.get_user.assert_called_once()


class TestTwitterActions(unittest.TestCase):
    """Test cases for Twitter action functions"""

    @patch('helpers.twitterhelpers.client')
    def test_follow_user(self, mock_client):
        """Test follow_user function"""
        from helpers.twitterhelpers import follow_user
        
        mock_client.follow_user.return_value = {'following': True, 'pending_follow': False}
        
        result = follow_user('123')
        
        mock_client.follow_user.assert_called_once_with(target_user_id='123', user_auth=True)

    @patch('helpers.twitterhelpers.client')
    def test_unfollow_user(self, mock_client):
        """Test unfollow_user function"""
        from helpers.twitterhelpers import unfollow_user
        
        mock_client.unfollow_user.return_value = {'following': False}
        
        result = unfollow_user('123')
        
        mock_client.unfollow_user.assert_called_once_with(target_user_id='123', user_auth=True)

    @patch('helpers.twitterhelpers.client')
    def test_like_tweet(self, mock_client):
        """Test like_tweet function"""
        from helpers.twitterhelpers import like_tweet
        
        mock_client.like.return_value = {'liked': True}
        
        result = like_tweet('123')
        
        mock_client.like.assert_called_once_with(tweet_id='123', user_auth=True)

    @patch('helpers.twitterhelpers.client')
    def test_unlike_tweet(self, mock_client):
        """Test unlike_tweet function"""
        from helpers.twitterhelpers import unlike_tweet
        
        mock_client.unlike.return_value = {'liked': False}
        
        result = unlike_tweet('123')
        
        mock_client.unlike.assert_called_once_with(tweet_id='123', user_auth=True)

    @patch('helpers.twitterhelpers.client')
    def test_delete_tweet(self, mock_client):
        """Test delete_tweet function"""
        from helpers.twitterhelpers import delete_tweet
        
        mock_client.delete_tweet.return_value = {'deleted': True}
        
        result = delete_tweet('123')
        
        mock_client.delete_tweet.assert_called_once_with(id='123', user_auth=True)

    @patch('helpers.twitterhelpers.client')
    def test_retweet(self, mock_client):
        """Test retweet function"""
        from helpers.twitterhelpers import retweet
        
        mock_client.retweet.return_value = {'retweeted': True}
        
        result = retweet('123')
        
        mock_client.retweet.assert_called_once_with(tweet_id='123', user_auth=True)

    @patch('helpers.twitterhelpers.client')
    def test_unretweet(self, mock_client):
        """Test unretweet function"""
        from helpers.twitterhelpers import unretweet
        
        mock_client.unretweet.return_value = {'retweeted': False}
        
        result = unretweet('123')
        
        mock_client.unretweet.assert_called_once_with(source_tweet_id='123', user_auth=True)


class TestCreateTweet(unittest.TestCase):
    """Test cases for create_tweet function"""

    @patch('helpers.twitterhelpers.client')
    def test_create_tweet_text_only(self, mock_client):
        """Test create_tweet with text only"""
        from helpers.twitterhelpers import create_tweet
        
        mock_client.create_tweet.return_value = {'id': '123', 'text': 'Hello'}
        
        result = create_tweet(text='Hello')
        
        mock_client.create_tweet.assert_called_once()

    @patch('helpers.twitterhelpers.client')
    def test_create_tweet_with_reply(self, mock_client):
        """Test create_tweet as reply"""
        from helpers.twitterhelpers import create_tweet
        
        mock_client.create_tweet.return_value = {'id': '456', 'text': 'Reply'}
        
        result = create_tweet(text='Reply', in_reply_to_tweet_id='123')
        
        call_kwargs = mock_client.create_tweet.call_args[1]
        self.assertEqual(call_kwargs['in_reply_to_tweet_id'], '123')

    @patch('helpers.twitterhelpers.client')
    def test_create_tweet_with_poll(self, mock_client):
        """Test create_tweet with poll"""
        from helpers.twitterhelpers import create_tweet
        
        mock_client.create_tweet.return_value = {'id': '789'}
        
        result = create_tweet(
            text='Poll question',
            poll_options=['Option 1', 'Option 2'],
            poll_duration_minutes=60
        )
        
        call_kwargs = mock_client.create_tweet.call_args[1]
        self.assertEqual(call_kwargs['poll_options'], ['Option 1', 'Option 2'])
        self.assertEqual(call_kwargs['poll_duration_minutes'], 60)


class TestDirectMessages(unittest.TestCase):
    """Test cases for direct message functions"""

    @patch('helpers.twitterhelpers.client')
    def test_get_direct_message_events(self, mock_client):
        """Test get_direct_message_events function"""
        from helpers.twitterhelpers import get_direct_message_events
        
        mock_client.get_direct_message_events.return_value = [{'id': '123'}]
        
        result = get_direct_message_events()
        
        mock_client.get_direct_message_events.assert_called_once()

    @patch('helpers.twitterhelpers.client')
    def test_get_direct_message_events_with_conversation(self, mock_client):
        """Test get_direct_message_events with conversation ID"""
        from helpers.twitterhelpers import get_direct_message_events
        
        mock_client.get_direct_message_events.return_value = [{'id': '123'}]
        
        result = get_direct_message_events(dm_conversation_id='conv123')
        
        call_kwargs = mock_client.get_direct_message_events.call_args[1]
        self.assertEqual(call_kwargs['dm_conversation_id'], 'conv123')

    @patch('helpers.twitterhelpers.client')
    def test_create_direct_message(self, mock_client):
        """Test create_direct_message function"""
        from helpers.twitterhelpers import create_direct_message
        
        mock_client.create_direct_message.return_value = {'id': '123'}
        
        result = create_direct_message(participant_id='456', text='Hello')
        
        call_kwargs = mock_client.create_direct_message.call_args[1]
        self.assertEqual(call_kwargs['participant_id'], '456')
        self.assertEqual(call_kwargs['text'], 'Hello')


class TestTrendingTopics(unittest.TestCase):
    """Test cases for trending topic functions"""

    @patch('helpers.twitterhelpers.api')
    def test_get_country_woeids(self, mock_api):
        """Test get_country_woeids function"""
        from helpers.twitterhelpers import get_country_woeids
        
        mock_api.available_trends.return_value = [
            {'country': 'United States', 'woeid': 23424977, 'placeType': {'name': 'Country'}},
            {'country': 'United Kingdom', 'woeid': 23424975, 'placeType': {'name': 'Country'}},
            {'country': 'New York', 'woeid': 2459115, 'placeType': {'name': 'Town'}}
        ]
        
        result = get_country_woeids()
        
        self.assertIn('United States', result)
        self.assertIn('United Kingdom', result)
        self.assertNotIn('New York', result)  # Not a country

    @patch('helpers.twitterhelpers.get_country_woeids')
    def test_get_country_woeid_found(self, mock_woeids):
        """Test get_country_woeid when country is found"""
        from helpers.twitterhelpers import get_country_woeid
        
        mock_woeids.return_value = {'United States': 23424977}
        
        result = get_country_woeid('United States')
        
        self.assertEqual(result, 23424977)

    @patch('helpers.twitterhelpers.get_country_woeids')
    def test_get_country_woeid_not_found(self, mock_woeids):
        """Test get_country_woeid when country is not found"""
        from helpers.twitterhelpers import get_country_woeid
        
        mock_woeids.return_value = {'United States': 23424977}
        
        result = get_country_woeid('Nonexistent Country')
        
        self.assertEqual(result, 0)

    @patch('helpers.twitterhelpers.api')
    def test_get_trending_topics_with_woeid(self, mock_api):
        """Test get_trending_topics with specific woeid"""
        from helpers.twitterhelpers import get_trending_topics
        
        mock_api.get_place_trends.return_value = [{
            'trends': [
                {'name': '#Topic1', 'tweet_volume': 1000, 'query': 'topic1', 'url': 'http://...'},
                {'name': '#Topic2', 'tweet_volume': 500, 'query': 'topic2', 'url': 'http://...'},
                {'name': '#Topic3', 'tweet_volume': None, 'query': 'topic3', 'url': 'http://...'}
            ]
        }]
        
        result = get_trending_topics(woeid=1)
        
        # Should be sorted by tweet_volume descending
        self.assertEqual(result[0][0], '#Topic1')
        self.assertEqual(result[0][1], 1000)
        # None should be converted to 0
        self.assertEqual(result[2][1], 0)

    @patch('helpers.twitterhelpers.api')
    @patch('helpers.twitterhelpers.random.choice')
    def test_get_trending_topics_random_woeid(self, mock_choice, mock_api):
        """Test get_trending_topics with random woeid"""
        from helpers.twitterhelpers import get_trending_topics
        
        mock_api.available_trends.return_value = [{'woeid': 1}, {'woeid': 2}]
        mock_choice.return_value = 1
        mock_api.get_place_trends.return_value = [{
            'trends': [{'name': '#Test', 'tweet_volume': 100, 'query': 'test', 'url': 'http://...'}]
        }]
        
        result = get_trending_topics()
        
        mock_choice.assert_called_once()


class TestGetExtendedStatus(unittest.TestCase):
    """Test cases for get_extended_status function"""

    @patch('helpers.twitterhelpers.api')
    def test_get_extended_status(self, mock_api):
        """Test get_extended_status function"""
        from helpers.twitterhelpers import get_extended_status
        
        mock_status = MagicMock()
        mock_status.full_text = 'Extended tweet text'
        mock_api.get_status.return_value = mock_status
        
        result = get_extended_status('123')
        
        mock_api.get_status.assert_called_once_with(id='123', tweet_mode='extended')
        self.assertEqual(result, mock_status)


if __name__ == '__main__':
    unittest.main()
