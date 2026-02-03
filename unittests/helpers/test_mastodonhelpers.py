#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock


class TestMastodonHelpers(unittest.TestCase):
    """Test cases for helpers/mastodonhelpers.py"""

    @patch('helpers.mastodonhelpers.get_enable_mastodon', return_value=True)
    @patch('helpers.mastodonhelpers.get_mastodon_client_id', return_value='client_id')
    @patch('helpers.mastodonhelpers.get_mastodon_client_secret', return_value='client_secret')
    @patch('helpers.mastodonhelpers.get_mastodon_access_token', return_value='access_token')
    @patch('helpers.mastodonhelpers.get_mastodon_api_base_url', return_value='https://mastodon.social')
    @patch('helpers.mastodonhelpers.mastodon.Mastodon')
    def test_get_mastodon_api_enabled(self, mock_mastodon, mock_url, mock_token, mock_secret, mock_id, mock_enable):
        """Test get_mastodon_api when Mastodon is enabled"""
        from helpers.mastodonhelpers import get_mastodon_api
        
        mock_client = MagicMock()
        mock_mastodon.return_value = mock_client
        
        result = get_mastodon_api()
        
        mock_mastodon.assert_called_once_with(
            client_id='client_id',
            client_secret='client_secret',
            access_token='access_token',
            api_base_url='https://mastodon.social'
        )
        self.assertEqual(result, mock_client)

    @patch('helpers.mastodonhelpers.get_enable_mastodon', return_value=False)
    def test_get_mastodon_api_disabled(self, mock_enable):
        """Test get_mastodon_api when Mastodon is disabled"""
        from helpers.mastodonhelpers import get_mastodon_api
        
        result = get_mastodon_api()
        
        self.assertIsNone(result)


class TestMastodonTrendingTopics(unittest.TestCase):
    """Test cases for trending topics functions"""

    @patch('helpers.mastodonhelpers.api')
    def test_get_trending_topics(self, mock_api):
        """Test get_trending_topics returns sorted topics"""
        from helpers.mastodonhelpers import get_trending_topics
        
        mock_api.trending_tags.return_value = [
            {'name': 'topic1', 'history': [{'uses': '100'}], 'url': 'https://example.com/topic1'},
            {'name': 'topic2', 'history': [{'uses': '200'}], 'url': 'https://example.com/topic2'},
        ]
        
        result = get_trending_topics()
        
        self.assertEqual(len(result), 2)
        # Should be sorted by count descending
        self.assertEqual(result[0][0], 'topic2')
        self.assertEqual(result[0][1], 200)

    @patch('helpers.mastodonhelpers.api')
    def test_get_trending_topics_no_history(self, mock_api):
        """Test get_trending_topics handles missing history"""
        from helpers.mastodonhelpers import get_trending_topics
        
        mock_api.trending_tags.return_value = [
            {'name': 'topic1', 'history': None, 'url': 'https://example.com/topic1'},
        ]
        
        result = get_trending_topics()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], 0)


class TestMastodonToots(unittest.TestCase):
    """Test cases for toot functions"""

    @patch('helpers.mastodonhelpers.api')
    @patch('helpers.mastodonhelpers.LOG')
    def test_get_popular_toot_ids(self, mock_log, mock_api):
        """Test get_popular_toot_ids returns toot IDs"""
        from helpers.mastodonhelpers import get_popular_toot_ids
        
        mock_api.timeline_hashtag.return_value = [
            {'in_reply_to_id': '123'},
            {'in_reply_to_id': '456'},
            {'in_reply_to_id': None},  # Should be skipped
        ]
        mock_api.fetch_next.return_value = []
        
        result = get_popular_toot_ids('test', limit=10)
        
        self.assertEqual(result, ['123', '456'])

    @patch('helpers.mastodonhelpers.api')
    def test_get_toots_by_id(self, mock_api):
        """Test get_toots_by_id returns toots"""
        from helpers.mastodonhelpers import get_toots_by_id
        
        mock_api.status.side_effect = [
            {'id': '123', 'content': 'Toot 1'},
            {'id': '456', 'content': 'Toot 2'},
        ]
        
        result = get_toots_by_id(['123', '456'])
        
        self.assertEqual(len(result['data']), 2)

    @patch('helpers.mastodonhelpers.api')
    def test_post_toot(self, mock_api):
        """Test post_toot calls status_post"""
        from helpers.mastodonhelpers import post_toot
        
        post_toot("Test toot", visibility='public')
        
        mock_api.status_post.assert_called_once_with(
            "Test toot",
            media_ids=None,
            sensitive=False,
            spoiler_text=None,
            visibility='public'
        )


if __name__ == '__main__':
    unittest.main()
