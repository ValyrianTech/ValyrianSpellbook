#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Union, List

from helpers.loghelpers import LOG
from .action import Action
from .actiontype import ActionType
from helpers.twitterhelpers import create_tweet


class CreateTweetAction(Action):
    def __init__(self, action_id):
        super(CreateTweetAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.CREATE_TWEET

        self.text: Union[str, None] = None
        self.in_reply_to_tweet_id: Union[int, str, None] = None
        self.reply_settings: Union[str, None] = None
        self.exclude_reply_user_ids: Union[List[Union[int, str]], None] = None
        self.quote_tweet_id: Union[int, str, None] = None
        self.poll_options: Union[List[str], None] = None
        self.poll_duration_minutes: Union[int, None] = None
        self.media_tagged_user_ids: Union[List[Union[int, str]], None] = None
        self.media_ids: Union[List[Union[int, str]], None] = None
        self.place_id: Union[str, None] = None
        self.for_super_followers_only: Union[bool, None] = None
        self.direct_message_deep_link: Union[str, None] = None
        self.user_auth: bool = True

    def run(self):
        """
        Run the action

        :return: True upon success, False upon failure
        """
        LOG.info('Creating tweet')
        LOG.info(f'text: {self.text}')
        LOG.info(f'in_reply_to_tweet_id: {self.in_reply_to_tweet_id}')
        LOG.info(f'reply_settings: {self.reply_settings}')
        LOG.info(f'exclude_reply_user_ids: {self.exclude_reply_user_ids}')
        LOG.info(f'quote_tweet_id: {self.quote_tweet_id}')
        LOG.info(f'poll_options: {self.poll_options}')
        LOG.info(f'poll_duration_minutes: {self.poll_duration_minutes}')
        LOG.info(f'media_tagged_user_ids: {self.media_tagged_user_ids}')
        LOG.info(f'media_ids: {self.media_ids}')
        LOG.info(f'place_id: {self.place_id}')
        LOG.info(f'for_super_followers_only: {self.for_super_followers_only}')
        LOG.info(f'direct_message_deep_link: {self.direct_message_deep_link}')
        LOG.info(f'user_auth: {self.user_auth}')

        try:
            create_tweet(text=self.text,
                         in_reply_to_tweet_id=self.in_reply_to_tweet_id,
                         reply_settings=self.reply_settings,
                         exclude_reply_user_ids=self.exclude_reply_user_ids,
                         quote_tweet_id=self.quote_tweet_id,
                         poll_options=self.poll_options,
                         poll_duration_minutes=self.poll_duration_minutes,
                         media_tagged_user_ids=self.media_tagged_user_ids,
                         media_ids=self.media_ids,
                         place_id=self.place_id,
                         for_super_followers_only=self.for_super_followers_only,
                         direct_message_deep_link=self.direct_message_deep_link,
                         user_auth=self.user_auth)

        except Exception as ex:
            LOG.error(f'Unable to create tweet: {ex}')
            return False

        return True

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                        - config['text']: Text of the Tweet being created. This field is required if media.media_ids is not present.
                        - config['in_reply_to_tweet_id']: Tweet ID of the Tweet being replied to. Please note that in_reply_to_tweet_id needs to be in the request if exclude_reply_user_ids is present.
                        - config['reply_settings']: Settings to indicate who can reply to the Tweet. Limited to “mentionedUsers” and “following”. If the field isn’t specified, it will default to everyone.
                        - config['exclude_reply_user_ids']:  A list of User IDs to be excluded from the reply Tweet thus removing a user from a thread.
                        - config['quote_tweet_id']: Link to the Tweet being quoted.
                        - config['poll_options']: A list of poll options for a Tweet with a poll.
                        - config['poll_duration_minutes']: Duration of the poll in minutes for a Tweet with a poll. This is only required if the request includes poll.options.
                        - config['media_tagged_user_ids']: A list of User IDs being tagged in the Tweet with Media. If the user you’re tagging doesn’t have photo-tagging enabled, their names won’t show up in the list of tagged users even though the Tweet is successfully created.
                        - config['media_ids']: A list of Media IDs being attached to the Tweet. This is only required if the request includes the tagged_user_ids.
                        - config['place_id']: Place ID being attached to the Tweet for geo location.
                        - config['for_super_followers_only']: Allows you to Tweet exclusively for Super Followers.
                        - config['direct_message_deep_link']: Tweets a link directly to a Direct Message conversation with an account.
                        - config['user_auth']: Whether or not to use OAuth 1.0a User Context to authenticate
        """
        super(CreateTweetAction, self).configure(**config)
        if 'text' in config:
            self.text = config['text']

        if 'in_reply_to_tweet_id' in config:
            self.in_reply_to_tweet_id = config['in_reply_to_tweet_id']

        if 'reply_settings' in config:
            self.reply_settings = config['reply_settings']

        if 'exclude_reply_user_ids' in config:
            self.exclude_reply_user_ids = config['exclude_reply_user_ids']

        if 'quote_tweet_id' in config:
            self.quote_tweet_id = config['quote_tweet_id']

        if 'poll_options' in config:
            self.poll_options = config['poll_options']

        if 'poll_duration_minutes' in config:
            self.poll_duration_minutes = config['poll_duration_minutes']

        if 'media_tagged_user_ids' in config:
            self.media_tagged_user_ids = config['media_tagged_user_ids']

        if 'media_ids' in config:
            self.media_ids = config['media_ids']

        if 'place_id' in config:
            self.place_id = config['place_id']

        if 'for_super_followers_only' in config:
            self.for_super_followers_only = config['for_super_followers_only']

        if 'direct_message_deep_link' in config:
            self.direct_message_deep_link = config['direct_message_deep_link']

        if 'user_auth' in config:
            self.user_auth = config['user_auth']

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super(CreateTweetAction, self).json_encodable()
        ret.update({'text': self.text,
                    'in_reply_to_tweet_id': self.in_reply_to_tweet_id,
                    'reply_settings': self.reply_settings,
                    'exclude_reply_user_ids': self.exclude_reply_user_ids,
                    'quote_tweet_id': self.quote_tweet_id,
                    'poll_options': self.poll_options,
                    'poll_duration_minutes': self.poll_duration_minutes,
                    'media_tagged_user_ids': self.media_tagged_user_ids,
                    'media_ids': self.media_ids,
                    'place_id': self.place_id,
                    'for_super_followers_only': self.for_super_followers_only,
                    'direct_message_deep_link': self.direct_message_deep_link,
                    'user_auth': self.user_auth})
        return ret
