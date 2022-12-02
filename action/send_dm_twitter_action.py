#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Union

from helpers.loghelpers import LOG
from .action import Action
from .actiontype import ActionType
from helpers.twitterhelpers import create_direct_message


class SendDMTwitterAction(Action):
    def __init__(self, action_id):
        super(SendDMTwitterAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.SEND_DM_TWITTER

        self.dm_conversation_id: Union[str, None] = None
        self.participant_id: Union[int, str, None] = None
        self.media_id: Union[int, str, None] = None
        self.text: Union[str, None] = None
        self.user_auth: bool = True

    def run(self):
        """
        Run the action

        :return: True upon success, False upon failure
        """
        LOG.info('Creating DM on twitter')
        LOG.info(f'dm_conversation_id: {self.dm_conversation_id}')
        LOG.info(f'participant_id: {self.participant_id}')
        LOG.info(f'media_id: {self.media_id}')
        LOG.info(f'text: {self.text}')
        LOG.info(f'user_auth: {self.user_auth}')

        try:
            create_direct_message(dm_conversation_id=self.dm_conversation_id,
                                  participant_id=self.participant_id,
                                  media_id=self.media_id,
                                  text=self.text,
                                  user_auth=self.user_auth)

        except Exception as ex:
            LOG.error(f'Unable to create direct message on twitter: {ex}')
            return False

        return True

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                    - config['dm_conversation_id']: The dm_conversation_id of the conversation to add the Direct Message to. Supports both 1-1 and group conversations.
                    - config['participant_id']: The User ID of the account this one-to-one Direct Message is to be sent to.
                    - config['media_id']: A single Media ID being attached to the Direct Message. This field is required if text is not present. For this launch, only 1 attachment is supported.
                    - config['text']: Text of the Direct Message being created. This field is required if media_id is not present. Text messages support up to 10,000 characters.
                    - config['user_auth']: Whether or not to use OAuth 1.0a User Context to authenticate
        """
        super(SendDMTwitterAction, self).configure(**config)
        if 'dm_conversation_id' in config:
            self.dm_conversation_id = config['dm_conversation_id']

        if 'participant_id' in config:
            self.participant_id = config['participant_id']

        if 'media_id' in config:
            self.media_id = config['media_id']

        if 'text' in config:
            self.text = config['text']

        if 'user_auth' in config:
            self.user_auth = config['user_auth']

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super(SendDMTwitterAction, self).json_encodable()
        ret.update({'dm_conversation_id': self.dm_conversation_id,
                    'participant_id': self.participant_id,
                    'media_id': self.media_id,
                    'text': self.text,
                    'user_auth': self.user_auth})
        return ret
