#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import logging

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
    """
    Get the specified trigger, which is a subclass of Trigger
    The different trigger types are:
    - ManualTrigger (default)
    - BalanceTrigger
    - ReceivedTrigger
    - SentTrigger
    - BlockHeightTrigger

    If no config is known for the given trigger id then a ManualTrigger is returned

    :param trigger_id: The id of the trigger
    :return: A derived Trigger object (ManualTrigger, BalanceTrigger, ReceivedTrigger, SentTrigger or BlockHeightTrigger)
    """
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


def check_triggers(trigger_id=None):
    # Get a list of all trigger_ids that are configured
    triggers = get_triggers()

    # If a trigger_id is given, only check that specific trigger
    if trigger_id is not None and trigger_id in triggers:
        triggers = [trigger_id]
    elif trigger_id is not None and trigger_id not in triggers:
        return {'error': 'Unknown trigger id: %s' % trigger_id}

    for trigger_id in triggers:
        trigger = get_trigger(trigger_id=trigger_id)
        if trigger.triggered is False:
            logging.getLogger('Spellbook').info('Checking conditions of trigger %s' % trigger_id)
            if trigger.conditions_fulfilled() is True:
                trigger.activate()
