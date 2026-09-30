#!/usr/bin/env python
"""Helper functions for creating, configuring, checking, and activating triggers."""

import glob
import os
import time

from helpers.actionhelpers import delete_action
from helpers.hotwallethelpers import (
    find_address_in_wallet,
    find_single_address_in_wallet,
    get_private_key_from_wallet,
)
from helpers.jsonhelpers import load_from_json_file
from helpers.loghelpers import LOG
from helpers.messagehelpers import sign_and_verify, verify_message
from trigger.balancetrigger import BalanceTrigger
from trigger.blockheighttrigger import BlockHeightTrigger
from trigger.deadmansswitchtrigger import DeadMansSwitchTrigger
from trigger.httpdeleterequesttrigger import HTTPDeleteRequestTrigger
from trigger.httpgetrequesttrigger import HTTPGetRequestTrigger
from trigger.httppostrequesttrigger import HTTPPostRequestTrigger
from trigger.manualtrigger import ManualTrigger
from trigger.receivedtrigger import ReceivedTrigger
from trigger.recurringtrigger import RecurringTrigger
from trigger.senttrigger import SentTrigger
from trigger.signedmessagetrigger import SignedMessageTrigger
from trigger.timestamptrigger import TimestampTrigger
from trigger.triggerstatustrigger import TriggerStatusTrigger
from trigger.triggertype import TriggerType
from trigger.txconfirmationtrigger import TxConfirmationTrigger
from validators.validators import valid_address

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
        trigger_config = load_from_json_file(os.path.join(TRIGGERS_DIR, f'{trigger_id}.json'))
    except OSError:
        # Trigger does not exist yet, return empty dict
        trigger_config = {}

    return trigger_config


def get_trigger(trigger_id, trigger_type=None):
    """
    Get the specified trigger, which is a subclass of Trigger
    The different trigger types are:
    - ManualTrigger (default)
    - BalanceTrigger
    - ReceivedTrigger
    - SentTrigger
    - BlockHeightTrigger
    - TxConfirmationTrigger
    - TimestampTrigger
    - RecurringTrigger
    - TriggerStatusTrigger

    If no config is known for the given trigger id then a ManualTrigger is returned

    :param trigger_id: The id of the trigger
    :param trigger_type: The type of the trigger (optional)
    :return: A child class of Trigger
    """
    trigger_config = get_trigger_config(trigger_id)

    if trigger_type is not None:
        trigger_config['trigger_type'] = trigger_type

    if trigger_config['trigger_type'] == TriggerType.BALANCE:
        trigger = BalanceTrigger(trigger_id)
    elif trigger_config['trigger_type'] == TriggerType.RECEIVED:
        trigger = ReceivedTrigger(trigger_id)
    elif trigger_config['trigger_type'] == TriggerType.SENT:
        trigger = SentTrigger(trigger_id)
    elif trigger_config['trigger_type'] == TriggerType.BLOCK_HEIGHT:
        trigger = BlockHeightTrigger(trigger_id)
    elif trigger_config['trigger_type'] == TriggerType.TX_CONFIRMATION:
        trigger = TxConfirmationTrigger(trigger_id)
    elif trigger_config['trigger_type'] == TriggerType.TIMESTAMP:
        trigger = TimestampTrigger(trigger_id)
    elif trigger_config['trigger_type'] == TriggerType.RECURRING:
        trigger = RecurringTrigger(trigger_id)
    elif trigger_config['trigger_type'] == TriggerType.TRIGGERSTATUS:
        trigger = TriggerStatusTrigger(trigger_id)
    elif trigger_config['trigger_type'] == TriggerType.DEADMANSSWITCH:
        trigger = DeadMansSwitchTrigger(trigger_id)
    elif trigger_config['trigger_type'] == TriggerType.SIGNEDMESSAGE:
        trigger = SignedMessageTrigger(trigger_id)
    elif trigger_config['trigger_type'] == TriggerType.MANUAL:
        trigger = ManualTrigger(trigger_id)
    elif trigger_config['trigger_type'] == TriggerType.HTTPGETREQUEST:
        trigger = HTTPGetRequestTrigger(trigger_id)
    elif trigger_config['trigger_type'] == TriggerType.HTTPPOSTREQUEST:
        trigger = HTTPPostRequestTrigger(trigger_id)
    elif trigger_config['trigger_type'] == TriggerType.HTTPDELETEREQUEST:
        trigger = HTTPDeleteRequestTrigger(trigger_id)
    else:
        raise NotImplementedError('Unknown trigger type: {}'.format(trigger_config['trigger_type']))

    trigger.configure(**trigger_config)

    return trigger


def save_trigger(trigger_id, **trigger_config):
    """
    Save or update a trigger config in the triggers.json file

    :param trigger_id: The id of the trigger
    :param trigger_config: A dict containing the configuration for the trigger
    """
    if 'trigger_type' in trigger_config:
        trigger = get_trigger(trigger_id, trigger_type=trigger_config['trigger_type'])
    else:
        trigger = get_trigger(trigger_id)

    trigger.configure(**trigger_config)
    trigger.save()


def delete_trigger(trigger_id):
    """
    Delete a trigger

    :param trigger_id: The id of the trigger to delete
    """
    filename = os.path.join(TRIGGERS_DIR, f'{trigger_id}.json')
    if os.path.isfile(filename):
        os.remove(filename)
    else:
        return {'error': f'Unknown trigger id: {trigger_id}'}


def activate_trigger(trigger_id):
    """
    Activate a Manual trigger or a DeadMansSwitch trigger

    :param trigger_id: The id of the trigger
    """
    if not os.path.isfile(os.path.join(TRIGGERS_DIR, f'{trigger_id}.json')):
        return {'error': f'Unknown trigger id: {trigger_id}'}

    trigger = get_trigger(trigger_id)
    if trigger.trigger_type == TriggerType.MANUAL:
        trigger.activate()
    elif trigger.trigger_type == TriggerType.DEADMANSSWITCH:
        trigger.arm()
    else:
        return {'error': 'Only triggers of type Manual or DeadmansSwitch can be activated manually'}


def check_triggers(trigger_id=None):
    """Check all active triggers and activate those whose conditions are fulfilled.

    Also handles self-destruct logic for triggers that have reached their expiry time.

    :param trigger_id: If given, only check the specified trigger (optional)
    """
    # Get a list of all trigger_ids that are configured
    triggers = get_triggers()

    # If a trigger_id is given, only check that specific trigger
    if trigger_id is not None and trigger_id in triggers:
        triggers = [trigger_id]
    elif trigger_id is not None and trigger_id not in triggers:
        return {'error': f'Unknown trigger id: {trigger_id}'}

    for tid in triggers:
        trigger = get_trigger(trigger_id=tid)
        if trigger.status == 'Active':
            LOG.info(f'Checking conditions of trigger {tid}')
            if trigger.conditions_fulfilled() is True:
                trigger.activate()

        if trigger.self_destruct is not None and trigger.self_destruct <= int(time.time()):
            LOG.info(f'Trigger {tid} has reached its self-destruct time')

            # Also destruct any attached actions if needed
            if trigger.destruct_actions is True:
                for action_id in trigger.actions:
                    LOG.info(f'Deleting action {action_id}')
                    delete_action(action_id=action_id)

            LOG.info(f'Deleting trigger {tid}')
            delete_trigger(trigger_id=tid)
            continue


def verify_signed_message(trigger_id, **data):
    """Verify a signed message and activate the corresponding SignedMessage trigger.

    :param trigger_id: The id of the trigger
    :param data: Must contain 'address', 'message', and 'signature' keys
    :return: A dict with the activation result or an error message
    """
    if not all(key in data for key in ['address', 'message', 'signature']):
        return {'error': 'Request data does not contain all required keys: address, message and signature'}

    triggers = get_triggers()
    if trigger_id not in triggers:
        return {'error': f'Unknown trigger id: {trigger_id}'}

    trigger = get_trigger(trigger_id)
    if trigger.trigger_type != TriggerType.SIGNEDMESSAGE:
        return {'error': f'Trigger {trigger.trigger_type} is not a Signedmessage trigger'}

    if trigger.address is not None and trigger.address != data['address']:
        return {'error': f'Trigger {trigger.id} only listens to signed messages from address {trigger.address}'}

    if verify_message(address=data['address'], message=data['message'], signature=data['signature']) is True:
        if trigger.status == 'Active':
            LOG.info(f'Trigger {trigger_id} received a verified signed message')
            trigger.process_message(address=data['address'],
                                    message=data['message'],
                                    signature=data['signature'],
                                    data=data.get('data', None),
                                    ipfs_object=data.get('ipfs_object', None))
            return trigger.activate()
    else:
        LOG.warning(f'Trigger {trigger_id} received a bad signed message')
        LOG.warning('message: {}'.format(data['message']))
        LOG.warning('address: {}'.format(data['address']))
        LOG.warning('signature: {}'.format(data['signature']))
        return {'error': 'Signature is invalid!'}


def sign_message(**data):
    """Sign a message using a private key from the hot wallet.

    :param data: Must contain 'address' and 'message' keys
    :return: A dict with 'success', 'signature', 'address', and 'message' or an error
    """
    if not all(key in data for key in ['address', 'message']):
        return {'success': False, 'error': 'Request data does not contain all required keys: address, message'}

    address = data['address']
    message = data['message']

    if not valid_address(address=address):
        return {'success': False, 'error': f'Invalid address: {address}'}

    if len(message) > 255:
        return {'success': False, 'error': 'Message is too long, can not be longer than 255 characters.'}

    account, index = find_address_in_wallet(address=address)
    if account is None or index is None:
        private_key = find_single_address_in_wallet(address=address)

        if private_key is None:
            return {'success': False, 'error': f'Address {address} not found in hot wallet'}
    else:
        private_key = get_private_key_from_wallet(account=account, index=index)[address]

    try:
        signature = sign_and_verify(private_key=private_key, address=address, message=message)
    except (ValueError, KeyError, TypeError, OSError) as ex:
        return {'success': False, 'error': f'Unable to sign message: {ex}'}

    return {'success': True,
            'signature': signature,
            'address': address,
            'message': message}


def http_options_request(trigger_id, **data):
    """Handle an HTTP OPTIONS request for a trigger.

    :param trigger_id: The id of the trigger
    :param data: Optional data to pass to the trigger
    :return: A dict with the activation result or an error message
    """
    triggers = get_triggers()
    if trigger_id not in triggers:
        return {'error': f'Unknown trigger id: {trigger_id}'}

    trigger = get_trigger(trigger_id)
    if trigger.trigger_type != TriggerType.HTTPOPTIONSREQUEST:
        return {'error': f'Trigger {trigger_id} is not a HTTP OPTIONS request trigger but a {trigger.trigger_type} trigger'}

    if trigger.status == 'Active':
        LOG.info(f'Trigger {trigger_id} received a HTTP OPTIONS request')
        if len(data) > 0:
            trigger.set_json_data(data=data)
        return trigger.activate()


def http_get_request(trigger_id, **data):
    """Handle an HTTP GET request for a trigger.

    :param trigger_id: The id of the trigger
    :param data: Optional data to pass to the trigger
    :return: A dict with the activation result or an error message
    """
    triggers = get_triggers()
    if trigger_id not in triggers:
        return {'error': f'Unknown trigger id: {trigger_id}'}

    trigger = get_trigger(trigger_id)
    if trigger.trigger_type != TriggerType.HTTPGETREQUEST:
        return {'error': f'Trigger {trigger_id} is not a HTTP GET request trigger but a {trigger.trigger_type} trigger'}

    if trigger.status == 'Active':
        LOG.info(f'Trigger {trigger_id} received a HTTP GET request')
        if len(data) > 0:
            trigger.set_json_data(data=data)
        return trigger.activate()


def http_post_request(trigger_id, **data):
    """Handle an HTTP POST request for a trigger.

    :param trigger_id: The id of the trigger
    :param data: Optional data to pass to the trigger
    :return: A dict with the activation result or an error message
    """
    triggers = get_triggers()
    if trigger_id not in triggers:
        return {'error': f'Unknown trigger id: {trigger_id}'}

    trigger = get_trigger(trigger_id)
    if trigger.trigger_type != TriggerType.HTTPPOSTREQUEST:
        return {'error': f'Trigger {trigger_id} is not a HTTP POST request trigger but a {trigger.trigger_type} trigger'}

    if trigger.status == 'Active':
        LOG.info(f'Trigger {trigger_id} received a HTTP POST request')
        if len(data) > 0:
            trigger.set_json_data(data=data)
        return trigger.activate()


def http_delete_request(trigger_id, **data):
    """Handle an HTTP DELETE request for a trigger.

    :param trigger_id: The id of the trigger
    :param data: Optional data to pass to the trigger
    :return: A dict with the activation result or an error message
    """
    triggers = get_triggers()
    if trigger_id not in triggers:
        return {'error': f'Unknown trigger id: {trigger_id}'}

    trigger = get_trigger(trigger_id)
    if trigger.trigger_type != TriggerType.HTTPDELETEREQUEST:
        return {'error': f'Trigger {trigger_id} is not a HTTP DELETE request trigger but a {trigger.trigger_type} trigger'}

    if trigger.status == 'Active':
        LOG.info(f'Trigger {trigger_id} received a HTTP DELETE request')
        if len(data) > 0:
            trigger.set_json_data(data=data)
        return trigger.activate()


def signed_message_request(trigger_id, **data):
    """Handle a SignedMessage request for a trigger.

    :param trigger_id: The id of the trigger
    :param data: Optional data including 'message', 'message_address', and 'message_signature'
    :return: A dict with the activation result or an error message
    """
    triggers = get_triggers()
    if trigger_id not in triggers:
        return {'error': f'Unknown trigger id: {trigger_id}'}

    trigger = get_trigger(trigger_id)
    if trigger.trigger_type != TriggerType.SIGNEDMESSAGE:
        return {'error': f'Trigger {trigger_id} is not a SignedMessage request trigger but a {trigger.trigger_type} trigger'}

    if trigger.status == 'Active':
        LOG.info(f'Trigger {trigger_id} received a SignedMessage request')

        if 'message' in data:
            trigger.message = data['message']
        if 'message_address' in data:
            trigger.message_address = data['message_address']
        if 'message_signature' in data:
            trigger.message_signature = data['message_signature']

        if len(data) > 0:
            trigger.set_json_data(data=data)

        return trigger.activate()

def file_download(trigger_id, **data):
    """Handle a file download request for an HTTP GET trigger.

    :param trigger_id: The id of the trigger
    :param data: Optional data to pass to the trigger
    :return: A dict with the activation result or an error message
    """
    triggers = get_triggers()
    if trigger_id not in triggers:
        return {'error': f'Unknown trigger id: {trigger_id}'}

    trigger = get_trigger(trigger_id)
    if trigger.trigger_type != TriggerType.HTTPGETREQUEST:
        return {'error': f'Trigger {trigger_id} is not a HTTP GET request trigger but a {trigger.trigger_type} trigger'}

    if trigger.status == 'Active':
        LOG.info(f'Trigger {trigger_id} received a HTTP GET request')
        if len(data) > 0:
            trigger.set_json_data(data=data)
        return trigger.activate()