#!/usr/bin/env python

"""Action that follows a user on Twitter."""

from helpers.loghelpers import LOG
from helpers.twitterhelpers import follow_user

from .action import Action
from .actiontype import ActionType


class FollowOnTwitterAction(Action):
    """Action that follows a user on Twitter."""
    def __init__(self, action_id):
        super().__init__(action_id=action_id)
        self.action_type = ActionType.FOLLOW_ON_TWITTER
        self.user_id = None

    def run(self):
        """
        Run the action

        :return: True upon success, False upon failure
        """
        if self.user_id is None:
            LOG.error('Unable to follow on twitter: No user_id')
            return False

        LOG.info(f'Following user {self.user_id} on twitter')

        try:
            follow_user(target_user_id=self.user_id)
        except (ValueError, KeyError, TypeError, OSError) as ex:
            LOG.error(f'Unable to follow user {self.user_id}: {ex}')
            return False

        return True

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['user_id']    : The id of the user to follow
        """
        super().configure(**config)
        if 'user_id' in config:
            self.user_id = config['user_id']

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super().json_encodable()
        ret.update({'user_id': self.user_id})
        return ret
