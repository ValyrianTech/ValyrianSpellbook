#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import os
import platform
import time
from abc import abstractmethod, ABCMeta
from datetime import datetime

from helpers.actionhelpers import get_actions, get_action
from helpers.jsonhelpers import save_to_json_file
from helpers.loghelpers import LOG
from spellbookscripts.spellbookscript import SpellbookScript
from validators.validators import valid_actions, valid_trigger_type, valid_amount, valid_script
from validators.validators import valid_description, valid_creator, valid_email, valid_youtube_id
from validators.validators import valid_status, valid_visibility, valid_timestamp

TRIGGERS_DIR = 'json/public/triggers'


class Trigger(object):
    __metaclass__ = ABCMeta

    def __init__(self, trigger_id):
        self.id = trigger_id
        self.trigger_type = None
        self.script = None
        self.data = None
        self.triggered = 0
        self.multi = False
        self.description = None
        self.creator_name = None
        self.creator_email = None
        self.youtube = None
        self.status = None
        self.visibility = None
        self.created = None
        self.actions = []
        self.self_destruct = None
        self.destruct_actions = False  # When self-destructing, also destruct the attached actions?

    def configure(self, **config):
        self.created = datetime.fromtimestamp(config['created']) if 'created' in config else datetime.now()

        if 'trigger_type' in config and valid_trigger_type(config['trigger_type']):
            self.trigger_type = config['trigger_type']

        if 'script' in config and valid_script(config['script']):
            self.script = config['script']

        if 'data' in config and isinstance(config['data'], dict):
            self.data = config['data']

        if 'multi' in config and config['multi'] in [True, False]:
            self.multi = config['multi']

        if 'status' in config and valid_status(config['status']):
            self.status = config['status']

        if 'reset' in config and config['reset'] is True:
            self.triggered = 0
            self.status = 'Active'

        elif 'triggered' in config and valid_amount(config['triggered']):
            self.triggered = config['triggered']

        if 'description' in config and valid_description(config['description']):
            self.description = config['description']

        if 'creator_name' in config and valid_creator(config['creator_name']):
            self.creator_name = config['creator_name']

        if 'creator_email' in config and valid_email(config['creator_email']):
            self.creator_email = config['creator_email']

        if 'youtube' in config and valid_youtube_id(config['youtube']):
            self.youtube = config['youtube']

        if 'visibility' in config and valid_visibility(config['visibility']):
            self.visibility = config['visibility']

        if 'actions' in config and valid_actions(config['actions']):
            self.actions = config['actions']
            configured_actions = get_actions()
            for action_id in self.actions:
                if action_id not in configured_actions:
                    LOG.warning('Trigger %s contains unknown action: %s' % (self.id, action_id))

        if 'self_destruct' in config and valid_timestamp(config['self_destruct']):
            self.self_destruct = config['self_destruct']

        if 'destruct_actions' in config and config['destruct_actions'] in [True, False]:
            self.destruct_actions = config['destruct_actions']

    @abstractmethod
    def conditions_fulfilled(self):
        """
        Abstract method to check if the conditions of the trigger have been fulfilled.

        :return: True or False
        """
        pass

    def activate(self):
        """
        Activate all actions on this trigger, if all actions are successful the 'triggered' status will be True
        If an action fails, the remaining actions will not be executed and the 'triggered' status remains False so another attempt can be made the next time the trigger is checked

        Important: actions of type SendTransaction should always be the last action in the list and there should only be maximum 1 SendTransaction

        :return:
        """
        LOG.info('Activating trigger %s' % self.id)
        script = self.load_script()

        if script is not None:
            script.run()
            if len(script.new_actions) >= 1:
                LOG.info('Adding actions %s to trigger %s' % (script.new_actions, self.id))
                self.actions.extend(script.new_actions)
                LOG.info('Trigger will run actions: %s' % self.actions)

        configured_actions = get_actions()
        for action_id in self.actions:
            if action_id not in configured_actions:
                LOG.error('Unknown action id: %s' % action_id)
                return

        for i, action_id in enumerate(self.actions):
            LOG.info('Running action %s: %s' % (i+1, action_id))

            action = get_action(action_id)
            success = action.run()

            if not success:
                self.triggered += 1
                self.status = 'Failed' if self.multi is False else 'Active'
                self.save()
                return

        # All actions were successful
        self.triggered += 1

        self.status = 'Succeeded' if self.multi is False else 'Active'
        self.save()

        if script is not None:
            script.cleanup()
            return script.http_response

    def get_script_variables(self):
        return self.json_encodable()

    def save(self):
        save_to_json_file(os.path.join(TRIGGERS_DIR, '%s.json' % self.id), self.json_encodable())

    def json_encodable(self):
        return {'trigger_id': self.id,
                'trigger_type': self.trigger_type,
                'script': self.script,
                'data': self.data,
                'triggered': self.triggered,
                'multi': self.multi,
                'description': self.description,
                'creator_name': self.creator_name,
                'creator_email': self.creator_email,
                'youtube': self.youtube,
                'status': self.status,
                'visibility': self.visibility,
                'created': int(time.mktime(self.created.timetuple())),
                'actions': self.actions,
                'self_destruct': self.self_destruct,
                'destruct_actions': self.destruct_actions}

    def load_script(self):
        if self.script is not None:
            if not valid_script(self.script):
                return

            script_name = self.script[:-3]  # script name without the .py extension
            script_path = None
            script_module_name = None

            # Search for the script in the allowed root directories
            for root_dir in ['spellbookscripts', 'apps']:
                if os.path.isfile(os.path.join(root_dir, self.script)):
                    script_path = os.path.join(root_dir, self.script)
                    if platform.system() == 'Windows':
                        script_module_name = '%s.%s' % (root_dir, script_name.replace('\\', '.'))
                    elif platform.system() == 'Linux':
                        script_module_name = '%s.%s' % (root_dir, script_name.replace('/', '.'))
                    else:
                        raise NotImplementedError('Unsupported platform: only windows and linux are supported')

            if script_path is None:
                LOG.error('Can not find spellbook script' % self.script)
                return

            LOG.info('Loading Spellbook Script %s' % script_path)
            try:
                script_module = importlib.import_module(script_module_name)
            except Exception as ex:
                LOG.error('Failed to load Spellbook Script %s: %s' % (script_path, ex))
                return

            script_class_name = os.path.basename(script_path)[:-3]
            spellbook_script = getattr(script_module, script_class_name)
            kwargs = self.get_script_variables()
            script = spellbook_script(**kwargs)

            if not isinstance(script, SpellbookScript):
                LOG.error(
                    'Script %s is not a valid Spellbook Script, instead it is a %s' % (self.script, type(script)))
                return

            return script
