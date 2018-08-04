#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os

from action.actiontype import ActionType
from action.commandaction import CommandAction
from action.spawnprocessaction import SpawnProcessAction
from helpers.jsonhelpers import load_from_json_file
from action.revealsecretaction import RevealSecretAction
from action.sendmailaction import SendMailAction
from action.sendtransactionaction import SendTransactionAction
from action.webhookaction import WebhookAction

ACTIONS_DIR = 'json/public/actions'


def get_actions():
    """
    Get the list of action_ids

    :return: A list of action_ids
    """
    actions = glob.glob(os.path.join(ACTIONS_DIR, '*.json'))

    return [os.path.splitext(os.path.basename(action))[0] for action in actions]


def get_action_config(action_id):
    """
    Get the configuration of an action

    :param action_id: id of the action
    :return: a dict containing the configuration of the action
    """
    try:
        action_config = load_from_json_file(os.path.join(ACTIONS_DIR, '%s.json' % action_id))
    except IOError:
        # Action does not exist yet, return empty dict
        action_config = {}

    return action_config


def get_action(action_id, action_type=None):
    """
    Get the specified action, which is a subclass of Action
    The different action types are:
    - CommandAction
    - SpawnProcessAction
    - SendTransactionAction
    - RevealSecretAction
    - SendMailAction
    - WebhookAction

    If no config is known for the given action id then a CommandAction is returned

    :param action_id: The id of the action
    :param action_type: The type of action (optional)
    :return: A derived Action object (CommandAction, SendTransactionAction,
             RevealSecretAction, SendMailAction or WebhookAction)
    """
    action_config = get_action_config(action_id)

    if action_type is not None:
        action_config['action_type'] = action_type

    if action_config['action_type'] == ActionType.COMMAND:
        action = CommandAction(action_id)
    elif action_config['action_type'] == ActionType.SPAWNPROCESS:
        action = SpawnProcessAction(action_id)
    elif action_config['action_type'] == ActionType.SENDTRANSACTION:
        action = SendTransactionAction(action_id)
    elif action_config['action_type'] == ActionType.REVEALSECRET:
        action = RevealSecretAction(action_id)
    elif action_config['action_type'] == ActionType.SENDMAIL:
        action = SendMailAction(action_id)
    elif action_config['action_type'] == ActionType.WEBHOOK:
        action = WebhookAction(action_id)
    else:
        raise NotImplementedError('Unknown action type: %s' % action_config['action_type'])

    action.configure(**action_config)

    return action


def save_action(action_id, **action_config):
    """
    Save or update an action config

    :param action_id: The id of the action
    :param action_config: A dict containing the configuration for the action
    """
    if 'action_type' in action_config:
        action = get_action(action_id, action_type=action_config['action_type'])
    else:
        action = get_action(action_id)

    action.configure(**action_config)
    action.save()


def delete_action(action_id):
    """
    Delete an action

    :param action_id: The id of the action to delete
    """
    filename = os.path.join(ACTIONS_DIR, '%s.json' % action_id)
    if os.path.isfile(filename):
        os.remove(filename)
    else:
        return {'error': 'Unknown action id: %s' % action_id}


def run_action(action_id):
    """
    Run a specific action

    :param action_id: The id of the action to run
    """
    action = get_action(action_id)
    return action.run()


def get_reveal(action_id):
    """
    Get a revealed text and/or link from a RevealSecret Action.
    Will return None as long as the action has not been activated.
    Only after the action is activated will the secret text or link be revealed

    :param action_id: The id of the action
    """
    action = get_action(action_id)
    if action.allow_reveal is False:
        return None

    response = {'reveal_text': action.reveal_text, 'reveal_link': action.reveal_link}

    return response
