#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob

from jsonhelpers import load_from_json_file
from triggertype import TriggerType
from manualtrigger import ManualTrigger
from balancetrigger import BalanceTrigger
from receivedtrigger import ReceivedTrigger
from senttrigger import SentTrigger
from blockheighttrigger import BlockHeightTrigger

TRIGGERS_DIR = 'json/public/triggers'


def get_triggers():
    """
    Get the list of triggers_ids

    :return: A list of trigger_ids
    """
    triggers = glob.glob(os.path.join(TRIGGERS_DIR, '*.json'))

    return [os.path.splitext(os.path.basename(trigger))[0] for trigger in triggers]


def get_trigger_config(trigger_id):
    """
    Get the configuration of a trigger

    :param trigger_id: id of the trigger
    :return: a dict containing the configuration of the trigger
    """
    try:
        trigger_config = load_from_json_file(os.path.join(TRIGGERS_DIR, '%s.json' % trigger_id))
    except IOError:
        # Trigger does not exist yet, return empty dict
        trigger_config = {}

    return trigger_config


def get_trigger(trigger_id):
    trigger_config = get_trigger_config(trigger_id)
    trigger = ManualTrigger(trigger_id)
    if 'trigger_type' in trigger_config:
        if trigger_config['trigger_type'] == TriggerType.BALANCE:
            trigger = BalanceTrigger(trigger_id)
        elif trigger_config['trigger_type'] == TriggerType.RECEIVED:
            trigger = ReceivedTrigger(trigger_id)
        elif trigger_config['trigger_type'] == TriggerType.SENT:
            trigger = SentTrigger(trigger_id)
        elif trigger_config['trigger_type'] == TriggerType.BLOCK_HEIGHT:
            trigger = BlockHeightTrigger(trigger_id)
        elif trigger_config['trigger_type'] == TriggerType.MANUAL:
            trigger = ManualTrigger(trigger_id)
        else:
            raise NotImplementedError('Unknown trigger type: %s' % trigger_config['trigger_type'])

    trigger.configure(**trigger_config)

    return trigger


def save_trigger(trigger_id, **trigger_config):
    """
    Save or update a trigger config in the triggers.json file

    :param trigger_id: The id of the trigger
    :param trigger_config: A dict containing the configuration for the trigger
    """
    trigger = get_trigger(trigger_id)
    trigger.configure(**trigger_config)
    trigger.save()


def delete_trigger(trigger_id):
    """
    Delete a trigger

    :param trigger_id: The id of the trigger to delete
    """
    filename = os.path.join(TRIGGERS_DIR, '%s.json' % trigger_id)
    if os.path.isfile(filename):
        os.remove(filename)
    else:
        return {'error': 'Unknown trigger id: %s' % trigger_id}


def activate_trigger(trigger_id):
    """
    Activate a Manual trigger

    :param trigger_id: The id of the trigger
    """
    if not os.path.isfile(os.path.join(TRIGGERS_DIR, '%s.json' % trigger_id)):
        return {'error': 'Unknown trigger id: %s' % trigger_id}

    trigger = get_trigger(trigger_id)
    if trigger.trigger_type == TriggerType.MANUAL:
        trigger.activate()
    else:
        return {'error': 'Only triggers of type Manual can be activated manually'}
