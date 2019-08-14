#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
from helpers.bech32 import bech32_decode
from helpers.loghelpers import LOG

from helpers.py2specials import *
from helpers.py3specials import *

ALL_CHARACTERS_REGEX = "^[a-zA-Z0-9àáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ð ,.'-]+$"
YOUTUBE_REGEX = "^(http(s?):\/\/)?(www\.)?youtu(be)?\.([a-z])+\/(watch(.*?)(\?|\&)v=)?(.*?)(&(.)*)?$"
YOUTUBE_ID_REGEX = "^[a-zA-Z0-9_-]{11}$"
URL_REGEX = "((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-_]*)?\??(?:[\-\+=&;%@\.\w_]*)#?(?:[\.\!\/\\\w]*))?)"
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
    if not isinstance(address, string_types):
        return False

    from helpers.configurationhelpers import get_use_testnet
    testnet = get_use_testnet()
    if testnet is True:
        return re.match(TESTNET_ADDRESS_REGEX, address) is not None or valid_bech32_address(address)
    else:
        return re.match(MAINNET_ADDRESS_REGEX, address) is not None or valid_bech32_address(address)


def valid_txid(txid):
    return isinstance(txid, string_types) and re.match(TXID_REGEX, txid) is not None


def valid_xpub(xpub):
    from helpers.configurationhelpers import get_use_testnet
    testnet = get_use_testnet()
    if testnet is True:
        return isinstance(xpub, string_types) and xpub[:4] == "tpub"
    else:
        return isinstance(xpub, string_types) and xpub[:4] == "xpub"


def valid_description(description):
    return isinstance(description, string_types) and len(description) <= 250


def valid_op_return(message):
    return isinstance(message, string_types) and 0 < len(message) <= 80


def valid_blockprofile_message(message):
    valid = False
    all_valid = True
    if isinstance(message, string_types):
        for message_part in message.split("|"):
            if re.match(BLOCKPROFILE_REGEX, message_part) is not None:
                valid = True
            else:
                all_valid = False

    return valid and all_valid


def valid_text(text):
    return isinstance(text, string_types)


def valid_url(url):
    return isinstance(url, string_types) and re.match(URL_REGEX, url) is not None


def valid_creator(creator):
    return isinstance(creator, string_types) and re.match(ALL_CHARACTERS_REGEX, creator) is not None


def valid_email(email):
    return isinstance(email, string_types) and re.match(EMAIL_REGEX, email) is not None


def valid_amount(amount):
    return isinstance(amount, int_types) and amount >= 0


def valid_block_height(block_height):
    return isinstance(block_height, int) and block_height >= 0


def valid_percentage(percentage):
    return isinstance(percentage, (int, float)) and 0.0 <= percentage <= 100.0


def valid_youtube(youtube):
    return isinstance(youtube, string_types) and re.match(YOUTUBE_REGEX, youtube) is not None


def valid_youtube_id(youtube):
    return isinstance(youtube, string_types) and re.match(YOUTUBE_ID_REGEX, youtube) is not None


def valid_status(status):
    return True if status in ['Pending', 'Active', 'Disabled', 'Succeeded', 'Failed'] else False


def valid_visibility(visibility):
    return True if visibility in ['Public', 'Private'] else False


def valid_private_key(private_key):  # Todo better validation
    return isinstance(private_key, string_types) and len(private_key) > 0


def valid_distribution(distribution):
    if not isinstance(distribution, dict) or len(distribution) == 0:
        return False

    return all([valid_address(key) and valid_amount(value) for key, value in distribution.items()])


def valid_outputs(outputs):
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
    return trigger_type in ['Manual', 'Balance', 'Received', 'Sent', 'Block_height', 'Timestamp', 'Recurring', 'TriggerStatus', 'DeadMansSwitch', 'SignedMessage']


def valid_action_type(action_type):
    return action_type in ['Command', 'SendTransaction', 'RevealSecret', 'SendMail', 'Webhook']


def valid_transaction_type(transaction_type):
    return transaction_type in ['Send2Single', 'Send2Many', 'Send2SIL', 'Send2LBL', 'Send2LRL', 'Send2LSL', 'Send2LAL']


def valid_actions(actions):
    return isinstance(actions, list) and all([isinstance(action_id, string_types) for action_id in actions])


def valid_timestamp(timestamp):
    return isinstance(timestamp, int) and timestamp > 0


def valid_phase(phase):
    return phase in range(6)


def valid_script(script):
    if not isinstance(script, string_types):
        return False

    if not script.endswith('.py'):
        LOG.error('Script %s is invalid: does not end with .py extension' % script)
        return False

    if os.path.isfile(os.path.join('spellbookscripts', script)):
        return True
    elif os.path.isfile(os.path.join('apps', script)):
        return True
    else:
        LOG.error('Script %s is invalid: file not found in spellbookscripts or apps directory' % script)
        return False


def valid_bech32_address(address):
    if not isinstance(address, string_types):
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
