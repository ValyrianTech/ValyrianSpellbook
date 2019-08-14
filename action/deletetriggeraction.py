#!/usr/bin/env python
# -*- coding: utf-8 -*-

from helpers.loghelpers import LOG
from .action import Action
from .actiontype import ActionType


class DeleteTriggerAction(Action):
    def __init__(self, action_id):
        super(DeleteTriggerAction, self).__init__(action_id=action_id)
        self.action_type = ActionType.DELETETRIGGER
        self.trigger_ids = []

    def run(self):
        """
        Run the action

        :return: True upon success, False upon failure
        """
        # avoid circular import
        from helpers.triggerhelpers import delete_trigger, get_triggers

        if self.trigger_ids is None or len(self.trigger_ids) == 0:
            LOG.error('Can not delete triggers: no trigger_ids set')
            return False

        LOG.info('Deleting triggers %s' % self.trigger_ids)
        configured_triggers = get_triggers()
        for trigger_id in self.trigger_ids:
            if trigger_id not in configured_triggers:
                LOG.error('Can not delete trigger: unknown trigger id: %s' % self.trigger_ids)
            else:
                delete_trigger(trigger_id=trigger_id)
                LOG.info('Trigger %s is deleted' % trigger_id)

        return True

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['trigger_ids']  : A list of trigger_ids to delete
        """
        super(DeleteTriggerAction, self).configure(**config)
        if 'trigger_ids' in config:
            self.trigger_ids = config['trigger_ids']

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super(DeleteTriggerAction, self).json_encodable()
        ret.update({'trigger_ids': self.trigger_ids})
        return ret
