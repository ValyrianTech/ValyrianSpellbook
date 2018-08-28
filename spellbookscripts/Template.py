#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from helpers.loghelpers import LOG
from spellbookscript import SpellbookScript
from helpers.triggerhelpers import get_trigger
from trigger.triggertype import TriggerType
from helpers.actionhelpers import get_action
from action.actiontype import ActionType


class Template(SpellbookScript):
    """
    Important:  the class name must be exactly the same as the script name without the .py extension
    The class must also be derived from 'SpellbookScript'

    spellbookscripts must either be stored in the 'spellbookscripts' directory or the 'apps' directory
    subdirectories are allowed, just remember when saving a trigger with a script, you must include the subdirectories in the script name
    """
    def __init__(self, *args, **kwargs):
        super(Template, self).__init__(*args, **kwargs)

        # If you need to initialize a few things, it is recommended to to this here after the super call

    def run(self):
        # Here you can write your code that will be executed when the trigger is activated. This happens before any actions are done.
        LOG.info('Running Spellbook Script: %s' % os.path.splitext(os.path.basename(__file__))[0])

        # A number of member variables are initialized by the spellbook:
        LOG.info('id: %s' % self.trigger_id)
        LOG.info('trigger_type: %s' % self.trigger_type)
        LOG.info('script: %s' % self.script)
        LOG.info('triggered: %s' % self.triggered)  # number of times the trigger has activated
        LOG.info('multi: %s' % self.multi)
        LOG.info('description: %s' % self.description)
        LOG.info('creator_name: %s' % self.creator_name)
        LOG.info('creator_email: %s' % self.creator_email)
        LOG.info('youtube: %s' % self.youtube)
        LOG.info('status: %s' % self.status)
        LOG.info('visibility: %s' % self.visibility)
        LOG.info('created: %s' % self.created)  # timestamp when the trigger was created
        LOG.info('actions: %s' % self.actions)  # a list of action_ids

        # For signed messages:
        LOG.info('address: %s' % self.address)
        LOG.info('signature: %s' % self.signature)
        LOG.info('message: %s' % self.message)

        LOG.info('json: %s' % self.json)  # json data from the http request
        LOG.info('data: %s' % self.data)  # the 'data' value of the trigger

        if self.json is not None:
            if 'address' not in self.json:
                LOG.info('Request data does not contain key: address')
                return

        # You can specify the response for the http request like this:
        self.http_response = {'status': 'success'}

        # You can add or modify actions like this:
        my_action = get_action(action_id='my_action_id', action_type=ActionType.SPAWNPROCESS)
        my_action.run_command = 'echo hello world!'
        my_action.save()

        # If you want the action to run when this script is finished, you must attach the action to the trigger
        self.attach_action(action_id='my_action_id')

        # You can add or modify triggers like this:
        my_trigger = get_trigger(trigger_id='my_trigger_id', trigger_type=TriggerType.MANUAL)  # if the trigger doesn't exist it will be created
        my_trigger.script = 'path\\to\\script.py'
        my_trigger.multi = True
        my_trigger.status = 'Active'
        my_trigger.actions = ['my_action_id']
        my_trigger.save()

    def cleanup(self):
        # Here you can write any code that will be executed after all actions are done.
        LOG.info('Cleaning up...')
