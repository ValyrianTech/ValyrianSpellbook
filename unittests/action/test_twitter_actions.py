#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock

from action.create_tweet_action import CreateTweetAction
from action.delete_tweet_action import DeleteTweetAction
from action.like_tweet_action import LikeTweetAction
from action.unlike_tweet_action import UnlikeTweetAction
from action.retweet_action import RetweetAction
from action.unretweet_action import UnretweetAction
from action.follow_on_twitter_action import FollowOnTwitterAction
from action.unfollow_on_twitter_action import UnfollowOnTwitterAction
from action.send_dm_twitter_action import SendDMTwitterAction
from action.actiontype import ActionType


class TestCreateTweetAction(object):
    """Tests for CreateTweetAction"""

    def test_createtweetaction_init(self):
        action = CreateTweetAction('test_tweet_action')
        assert action.id == 'test_tweet_action'
        assert action.action_type == ActionType.CREATE_TWEET
        assert action.text is None
        assert action.in_reply_to_tweet_id is None
        assert action.user_auth == True

    def test_createtweetaction_configure(self):
        action = CreateTweetAction('test_tweet_action')
        action.configure(
            text='Hello world',
            in_reply_to_tweet_id='123456',
            reply_settings='mentionedUsers',
            exclude_reply_user_ids=['user1', 'user2'],
            quote_tweet_id='789',
            poll_options=['Yes', 'No'],
            poll_duration_minutes=60,
            media_tagged_user_ids=['media_user1'],
            media_ids=['media1'],
            place_id='place123',
            for_super_followers_only=True,
            direct_message_deep_link='https://dm.link',
            user_auth=False
        )
        assert action.text == 'Hello world'
        assert action.in_reply_to_tweet_id == '123456'
        assert action.reply_settings == 'mentionedUsers'
        assert action.exclude_reply_user_ids == ['user1', 'user2']
        assert action.quote_tweet_id == '789'
        assert action.poll_options == ['Yes', 'No']
        assert action.poll_duration_minutes == 60
        assert action.media_tagged_user_ids == ['media_user1']
        assert action.media_ids == ['media1']
        assert action.place_id == 'place123'
        assert action.for_super_followers_only == True
        assert action.direct_message_deep_link == 'https://dm.link'
        assert action.user_auth == False

    def test_createtweetaction_json_encodable(self):
        action = CreateTweetAction('test_tweet_action')
        action.configure(text='Test tweet', created=1609459200)
        result = action.json_encodable()
        assert result['id'] == 'test_tweet_action'
        assert result['action_type'] == ActionType.CREATE_TWEET
        assert result['text'] == 'Test tweet'

    @mock.patch('action.create_tweet_action.create_tweet')
    def test_createtweetaction_run_success(self, mock_create_tweet):
        action = CreateTweetAction('test_tweet_action')
        action.configure(text='Hello world')
        result = action.run()
        assert result == True
        mock_create_tweet.assert_called_once()

    @mock.patch('action.create_tweet_action.create_tweet')
    def test_createtweetaction_run_exception(self, mock_create_tweet):
        mock_create_tweet.side_effect = Exception('Twitter API error')
        action = CreateTweetAction('test_tweet_action')
        action.configure(text='Hello world')
        result = action.run()
        assert result == False


class TestDeleteTweetAction(object):
    """Tests for DeleteTweetAction"""

    def test_deletetweetaction_init(self):
        action = DeleteTweetAction('test_delete_tweet')
        assert action.id == 'test_delete_tweet'
        assert action.action_type == ActionType.DELETE_TWEET
        assert action.tweet_id is None

    def test_deletetweetaction_configure(self):
        action = DeleteTweetAction('test_delete_tweet')
        action.configure(tweet_id='123456')
        assert action.tweet_id == '123456'

    def test_deletetweetaction_json_encodable(self):
        action = DeleteTweetAction('test_delete_tweet')
        action.configure(tweet_id='123456', created=1609459200)
        result = action.json_encodable()
        assert result['tweet_id'] == '123456'

    def test_deletetweetaction_run_no_tweet_id(self):
        action = DeleteTweetAction('test_delete_tweet')
        result = action.run()
        assert result == False

    @mock.patch('action.delete_tweet_action.delete_tweet')
    def test_deletetweetaction_run_success(self, mock_delete_tweet):
        action = DeleteTweetAction('test_delete_tweet')
        action.configure(tweet_id='123456')
        result = action.run()
        assert result == True
        mock_delete_tweet.assert_called_once_with(tweet_id='123456')

    @mock.patch('action.delete_tweet_action.delete_tweet')
    def test_deletetweetaction_run_exception(self, mock_delete_tweet):
        mock_delete_tweet.side_effect = Exception('API error')
        action = DeleteTweetAction('test_delete_tweet')
        action.configure(tweet_id='123456')
        result = action.run()
        assert result == False


class TestLikeTweetAction(object):
    """Tests for LikeTweetAction"""

    def test_liketweetaction_init(self):
        action = LikeTweetAction('test_like_tweet')
        assert action.id == 'test_like_tweet'
        assert action.action_type == ActionType.LIKE_TWEET
        assert action.tweet_id is None

    def test_liketweetaction_configure(self):
        action = LikeTweetAction('test_like_tweet')
        action.configure(tweet_id='123456')
        assert action.tweet_id == '123456'

    def test_liketweetaction_json_encodable(self):
        action = LikeTweetAction('test_like_tweet')
        action.configure(tweet_id='123456', created=1609459200)
        result = action.json_encodable()
        assert result['tweet_id'] == '123456'

    def test_liketweetaction_run_no_tweet_id(self):
        action = LikeTweetAction('test_like_tweet')
        result = action.run()
        assert result == False

    @mock.patch('action.like_tweet_action.like_tweet')
    def test_liketweetaction_run_success(self, mock_like_tweet):
        action = LikeTweetAction('test_like_tweet')
        action.configure(tweet_id='123456')
        result = action.run()
        assert result == True
        mock_like_tweet.assert_called_once_with(tweet_id='123456')

    @mock.patch('action.like_tweet_action.like_tweet')
    def test_liketweetaction_run_exception(self, mock_like_tweet):
        mock_like_tweet.side_effect = Exception('API error')
        action = LikeTweetAction('test_like_tweet')
        action.configure(tweet_id='123456')
        result = action.run()
        assert result == False


class TestUnlikeTweetAction(object):
    """Tests for UnlikeTweetAction"""

    def test_unliketweetaction_init(self):
        action = UnlikeTweetAction('test_unlike_tweet')
        assert action.id == 'test_unlike_tweet'
        assert action.action_type == ActionType.UNLIKE_TWEET
        assert action.tweet_id is None

    def test_unliketweetaction_configure(self):
        action = UnlikeTweetAction('test_unlike_tweet')
        action.configure(tweet_id='123456')
        assert action.tweet_id == '123456'

    def test_unliketweetaction_json_encodable(self):
        action = UnlikeTweetAction('test_unlike_tweet')
        action.configure(tweet_id='123456', created=1609459200)
        result = action.json_encodable()
        assert result['tweet_id'] == '123456'

    def test_unliketweetaction_run_no_tweet_id(self):
        action = UnlikeTweetAction('test_unlike_tweet')
        result = action.run()
        assert result == False

    @mock.patch('action.unlike_tweet_action.unlike_tweet')
    def test_unliketweetaction_run_success(self, mock_unlike_tweet):
        action = UnlikeTweetAction('test_unlike_tweet')
        action.configure(tweet_id='123456')
        result = action.run()
        assert result == True
        mock_unlike_tweet.assert_called_once_with(tweet_id='123456')

    @mock.patch('action.unlike_tweet_action.unlike_tweet')
    def test_unliketweetaction_run_exception(self, mock_unlike_tweet):
        mock_unlike_tweet.side_effect = Exception('API error')
        action = UnlikeTweetAction('test_unlike_tweet')
        action.configure(tweet_id='123456')
        result = action.run()
        assert result == False


class TestRetweetAction(object):
    """Tests for RetweetAction"""

    def test_retweetaction_init(self):
        action = RetweetAction('test_retweet')
        assert action.id == 'test_retweet'
        assert action.action_type == ActionType.RETWEET
        assert action.tweet_id is None

    def test_retweetaction_configure(self):
        action = RetweetAction('test_retweet')
        action.configure(tweet_id='123456')
        assert action.tweet_id == '123456'

    def test_retweetaction_json_encodable(self):
        action = RetweetAction('test_retweet')
        action.configure(tweet_id='123456', created=1609459200)
        result = action.json_encodable()
        assert result['tweet_id'] == '123456'

    def test_retweetaction_run_no_tweet_id(self):
        action = RetweetAction('test_retweet')
        result = action.run()
        assert result == False

    @mock.patch('action.retweet_action.retweet')
    def test_retweetaction_run_success(self, mock_retweet):
        action = RetweetAction('test_retweet')
        action.configure(tweet_id='123456')
        result = action.run()
        assert result == True
        mock_retweet.assert_called_once_with(tweet_id='123456')

    @mock.patch('action.retweet_action.retweet')
    def test_retweetaction_run_exception(self, mock_retweet):
        mock_retweet.side_effect = Exception('API error')
        action = RetweetAction('test_retweet')
        action.configure(tweet_id='123456')
        result = action.run()
        assert result == False


class TestUnretweetAction(object):
    """Tests for UnretweetAction"""

    def test_unretweetaction_init(self):
        action = UnretweetAction('test_unretweet')
        assert action.id == 'test_unretweet'
        assert action.action_type == ActionType.UNRETWEET
        assert action.tweet_id is None

    def test_unretweetaction_configure(self):
        action = UnretweetAction('test_unretweet')
        action.configure(tweet_id='123456')
        assert action.tweet_id == '123456'

    def test_unretweetaction_json_encodable(self):
        action = UnretweetAction('test_unretweet')
        action.configure(tweet_id='123456', created=1609459200)
        result = action.json_encodable()
        assert result['tweet_id'] == '123456'

    def test_unretweetaction_run_no_tweet_id(self):
        action = UnretweetAction('test_unretweet')
        result = action.run()
        assert result == False

    @mock.patch('action.unretweet_action.retweet')
    def test_unretweetaction_run_success(self, mock_retweet):
        action = UnretweetAction('test_unretweet')
        action.configure(tweet_id='123456')
        result = action.run()
        assert result == True
        mock_retweet.assert_called_once_with(tweet_id='123456')

    @mock.patch('action.unretweet_action.retweet')
    def test_unretweetaction_run_exception(self, mock_retweet):
        mock_retweet.side_effect = Exception('API error')
        action = UnretweetAction('test_unretweet')
        action.configure(tweet_id='123456')
        result = action.run()
        assert result == False


class TestFollowOnTwitterAction(object):
    """Tests for FollowOnTwitterAction"""

    def test_followontwitteraction_init(self):
        action = FollowOnTwitterAction('test_follow')
        assert action.id == 'test_follow'
        assert action.action_type == ActionType.FOLLOW_ON_TWITTER
        assert action.user_id is None

    def test_followontwitteraction_configure(self):
        action = FollowOnTwitterAction('test_follow')
        action.configure(user_id='user123')
        assert action.user_id == 'user123'

    def test_followontwitteraction_json_encodable(self):
        action = FollowOnTwitterAction('test_follow')
        action.configure(user_id='user123', created=1609459200)
        result = action.json_encodable()
        assert result['user_id'] == 'user123'

    def test_followontwitteraction_run_no_user_id(self):
        action = FollowOnTwitterAction('test_follow')
        result = action.run()
        assert result == False

    @mock.patch('action.follow_on_twitter_action.follow_user')
    def test_followontwitteraction_run_success(self, mock_follow):
        action = FollowOnTwitterAction('test_follow')
        action.configure(user_id='user123')
        result = action.run()
        assert result == True
        mock_follow.assert_called_once_with(target_user_id='user123')

    @mock.patch('action.follow_on_twitter_action.follow_user')
    def test_followontwitteraction_run_exception(self, mock_follow):
        mock_follow.side_effect = Exception('API error')
        action = FollowOnTwitterAction('test_follow')
        action.configure(user_id='user123')
        result = action.run()
        assert result == False


class TestUnfollowOnTwitterAction(object):
    """Tests for UnfollowOnTwitterAction"""

    def test_unfollowontwitteraction_init(self):
        action = UnfollowOnTwitterAction('test_unfollow')
        assert action.id == 'test_unfollow'
        assert action.action_type == ActionType.UNFOLLOW_ON_TWITTER
        assert action.user_id is None

    def test_unfollowontwitteraction_configure(self):
        action = UnfollowOnTwitterAction('test_unfollow')
        action.configure(user_id='user123')
        assert action.user_id == 'user123'

    def test_unfollowontwitteraction_json_encodable(self):
        action = UnfollowOnTwitterAction('test_unfollow')
        action.configure(user_id='user123', created=1609459200)
        result = action.json_encodable()
        assert result['user_id'] == 'user123'

    def test_unfollowontwitteraction_run_no_user_id(self):
        action = UnfollowOnTwitterAction('test_unfollow')
        result = action.run()
        assert result == False

    @mock.patch('action.unfollow_on_twitter_action.unfollow_user')
    def test_unfollowontwitteraction_run_success(self, mock_unfollow):
        action = UnfollowOnTwitterAction('test_unfollow')
        action.configure(user_id='user123')
        result = action.run()
        assert result == True
        mock_unfollow.assert_called_once_with(target_user_id='user123')

    @mock.patch('action.unfollow_on_twitter_action.unfollow_user')
    def test_unfollowontwitteraction_run_exception(self, mock_unfollow):
        mock_unfollow.side_effect = Exception('API error')
        action = UnfollowOnTwitterAction('test_unfollow')
        action.configure(user_id='user123')
        result = action.run()
        assert result == False


class TestSendDMTwitterAction(object):
    """Tests for SendDMTwitterAction"""

    def test_senddmtwitteraction_init(self):
        action = SendDMTwitterAction('test_dm')
        assert action.id == 'test_dm'
        assert action.action_type == ActionType.SEND_DM_TWITTER
        assert action.dm_conversation_id is None
        assert action.participant_id is None
        assert action.media_id is None
        assert action.text is None
        assert action.user_auth == True

    def test_senddmtwitteraction_configure(self):
        action = SendDMTwitterAction('test_dm')
        action.configure(
            dm_conversation_id='conv123',
            participant_id='user123',
            media_id='media456',
            text='Hello!',
            user_auth=False
        )
        assert action.dm_conversation_id == 'conv123'
        assert action.participant_id == 'user123'
        assert action.media_id == 'media456'
        assert action.text == 'Hello!'
        assert action.user_auth == False

    def test_senddmtwitteraction_json_encodable(self):
        action = SendDMTwitterAction('test_dm')
        action.configure(participant_id='user123', text='Hello!', created=1609459200)
        result = action.json_encodable()
        assert result['participant_id'] == 'user123'
        assert result['text'] == 'Hello!'

    @mock.patch('action.send_dm_twitter_action.create_direct_message')
    def test_senddmtwitteraction_run_success(self, mock_create_dm):
        action = SendDMTwitterAction('test_dm')
        action.configure(participant_id='user123', text='Hello!')
        result = action.run()
        assert result == True
        mock_create_dm.assert_called_once()

    @mock.patch('action.send_dm_twitter_action.create_direct_message')
    def test_senddmtwitteraction_run_exception(self, mock_create_dm):
        mock_create_dm.side_effect = Exception('API error')
        action = SendDMTwitterAction('test_dm')
        action.configure(participant_id='user123', text='Hello!')
        result = action.run()
        assert result == False
