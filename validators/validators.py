#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Validation functions for Bitcoin addresses, transactions, and various input types."""

import re
import os
from helpers.bech32 import bech32_decode
from helpers.loghelpers import LOG

ALL_CHARACTERS_REGEX = "^[a-zA-Z0-9àáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ð ,.'-]+$"
YOUTUBE_REGEX = r"^(http(s?):\/\/)?(www\.)?youtu(be)?\.([a-z])+\/(watch(.*?)(\?|\&)v=)?(.*?)(&(.)*)?$"
YOUTUBE_ID_REGEX = "^[a-zA-Z0-9_-]{11}$"
URL_REGEX = r"((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-_]*)?\??(?:[\-\+=&;%@\.\w_]*)#?(?:[\.\!\/\\\w]*))?)"
MAINNET_ADDRESS_REGEX = "^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$"
TESTNET_ADDRESS_REGEX = "^[nm2][a-km-zA-HJ-NP-Z1-9]{25,34}$"
TXID_REGEX = "^[a-f0-9]{64}$"
BLOCKPROFILE_REGEX = "^[0-9]*@[0-9]+:[a-zA-Z0-9]+=[a-zA-Z0-9 ]+$"
EMAIL_REGEX = r"[^@]+@[^@]+\.[^@]+"
LOWERCASE_TESTNET_BECH32_ADDRESS_REGEX = '^tb1[ac-hj-np-z02-9]{11,71}$'
LOWERCASE_MAINNET_BECH32_ADDRESS_REGEX = '^bc1[ac-hj-np-z02-9]{11,71}$'
UPPERCASE_TESTNET_BECH32_ADDRESS_REGEX = '^TB1[AC-HJ-NP-Z02-9]{11,71}$'
UPPERCASE_MAINNET_BECH32_ADDRESS_REGEX = '^BC1[AC-HJ-NP-Z02-9]{11,71}$'


def valid_address(address):
    """Check if the given address is a valid Bitcoin address (legacy or Bech32)."""
    if not isinstance(address, str):
        return False

    from helpers.configurationhelpers import get_use_testnet
    testnet = get_use_testnet()
    if testnet is True:
        return re.match(TESTNET_ADDRESS_REGEX, address) is not None or valid_bech32_address(address)
    else:
        return re.match(MAINNET_ADDRESS_REGEX, address) is not None or valid_bech32_address(address)


def valid_txid(txid):
    """Check if the given string is a valid transaction ID (64-char hex)."""
    return isinstance(txid, str) and re.match(TXID_REGEX, txid) is not None


def valid_xpub(xpub):
    """Check if the given string is a valid extended public key (xpub or tpub)."""
    from helpers.configurationhelpers import get_use_testnet
    testnet = get_use_testnet()
    if testnet is True:
        return isinstance(xpub, str) and xpub[:4] == "tpub"
    else:
        return isinstance(xpub, str) and xpub[:4] == "xpub"


def valid_description(description):
    """Check if the given description is a valid string of at most 250 characters."""
    return isinstance(description, str) and len(description) <= 250


def valid_op_return(message):
    """Check if the given message is a valid OP_RETURN (non-empty, max 80 chars)."""
    return isinstance(message, str) and 0 < len(message) <= 80


def valid_blockprofile_message(message):
    """Check if the given message is a valid block profile message (from_index@to_index:name=value)."""
    valid = False
    all_valid = True
    if isinstance(message, str):
        for message_part in message.split("|"):
            if re.match(BLOCKPROFILE_REGEX, message_part) is not None:
                valid = True
            else:
                all_valid = False

    return valid and all_valid


def valid_text(text):
    """Check if the given value is a string."""
    return isinstance(text, str)


def valid_url(url):
    """Check if the given string is a valid URL."""
    return isinstance(url, str) and re.match(URL_REGEX, url) is not None


def valid_creator(creator):
    """Check if the given creator name contains only allowed characters."""
    return isinstance(creator, str) and re.match(ALL_CHARACTERS_REGEX, creator) is not None


def valid_email(email):
    """Check if the given string is a valid email address."""
    return isinstance(email, str) and re.match(EMAIL_REGEX, email) is not None


def valid_amount(amount):
    """Check if the given amount is a non-negative integer (not a float)."""
    return isinstance(amount, int) and not isinstance(amount, float) and amount >= 0


def valid_block_height(block_height):
    """Check if the given block height is a non-negative integer."""
    return isinstance(block_height, int) and block_height >= 0


def valid_percentage(percentage):
    """Check if the given percentage is a number between 0 and 100."""
    return isinstance(percentage, (int, float)) and 0.0 <= percentage <= 100.0


def valid_youtube(youtube):
    """Check if the given string is a valid YouTube URL."""
    return isinstance(youtube, str) and re.match(YOUTUBE_REGEX, youtube) is not None


def valid_youtube_id(youtube):
    """Check if the given string is a valid YouTube video ID (11 chars)."""
    return isinstance(youtube, str) and re.match(YOUTUBE_ID_REGEX, youtube) is not None


def valid_status(status):
    """Check if the given status is one of the allowed trigger status values."""
    return True if status in ['Pending', 'Active', 'Disabled', 'Succeeded', 'Failed'] else False


def valid_visibility(visibility):
    """Check if the given visibility is either 'Public' or 'Private'."""
    return True if visibility in ['Public', 'Private'] else False


def valid_private_key(private_key):  # Todo better validation
    """Check if the given private key is a non-empty string."""
    return isinstance(private_key, str) and len(private_key) > 0


def valid_distribution(distribution):
    """Check if the given distribution dict maps valid addresses to valid amounts."""
    if not isinstance(distribution, dict) or len(distribution) == 0:
        return False

    return all([valid_address(key) and valid_amount(value) for key, value in distribution.items()])


def valid_outputs(outputs):
    """Check if the given outputs list contains valid (address, amount) pairs."""
    valid = False

    if isinstance(outputs, list):
        if len(outputs) >= 1:
            for recipient in outputs:
                if isinstance(recipient, (tuple, list)):
                    if len(recipient) == 2:
                        if valid_address(recipient[0]) and isinstance(recipient[1], int) and recipient[1] > 0:
                            valid = True
                        else:
                            valid = False
                            break
                    else:
                        valid = False
                        break
    return valid


def valid_trigger_type(trigger_type):
    """Check if the given trigger type is one of the allowed values."""
    return trigger_type in ['Manual', 'Balance', 'Received', 'Sent', 'Block_height', 'Timestamp', 'Recurring', 'TriggerStatus', 'DeadMansSwitch', 'SignedMessage']


def valid_action_type(action_type):
    """Check if the given action type is one of the allowed values."""
    return action_type in ['Command', 'SendTransaction', 'RevealSecret', 'SendMail', 'Webhook']


def valid_transaction_type(transaction_type):
    """Check if the given transaction type is one of the allowed values."""
    return transaction_type in ['Send2Single', 'Send2Many', 'Send2SIL', 'Send2LBL', 'Send2LRL', 'Send2LSL', 'Send2LAL']


def valid_actions(actions):
    """Check if the given actions is a list of strings."""
    return isinstance(actions, list) and all([isinstance(action_id, str) for action_id in actions])


def valid_timestamp(timestamp):
    """Check if the given timestamp is a positive integer."""
    return isinstance(timestamp, int) and timestamp > 0


def valid_phase(phase):
    """Check if the given phase is in the valid range (0-5)."""
    return phase in range(6)


def valid_script(script):
    """Check if the given script name is a valid .py file in spellbookscripts or apps."""
    if not isinstance(script, str):
        return False

    if not script.endswith('.py'):
        LOG.error('Script %s is invalid: does not end with .py extension' % script)
        return False

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.isfile(os.path.join(project_root, 'spellbookscripts', script)):
        return True
    elif os.path.isfile(os.path.join(project_root, 'apps', script)):
        return True
    else:
        LOG.error('Script %s is invalid: file not found in spellbookscripts or apps directory' % script)
        return False


def valid_bech32_address(address):
    """Check if the given string is a valid Bech32 Bitcoin address (mainnet or testnet)."""
    if not isinstance(address, str):
        return False

    hrp, data = bech32_decode(address)
    if (hrp, data) == (None, None):
        return False

    from helpers.configurationhelpers import get_use_testnet
    testnet = get_use_testnet()
    if testnet is True:
        return re.match(LOWERCASE_TESTNET_BECH32_ADDRESS_REGEX, address) is not None or re.match(UPPERCASE_TESTNET_BECH32_ADDRESS_REGEX, address) is not None
    else:
        return re.match(LOWERCASE_MAINNET_BECH32_ADDRESS_REGEX, address) is not None or re.match(UPPERCASE_MAINNET_BECH32_ADDRESS_REGEX, address) is not None
