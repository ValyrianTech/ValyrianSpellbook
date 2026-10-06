#!/usr/bin/env python
"""Validation functions for Bitcoin addresses, transactions, and various input types."""

import ipaddress
import os
import re
import socket
from urllib.parse import urlparse

from helpers.bech32 import bech32_decode
from helpers.loghelpers import LOG
from helpers.pathhelpers import safe_path

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


def resolve_and_validate_webhook_url(url):
    """Resolve a webhook URL's hostname and return its validated public IP (SSRF-safe).

    The URL must be a valid http/https URL whose hostname resolves exclusively to
    public IP addresses. Returns the first resolved public IP string on success, or
    None if the URL is invalid, uses a non-http(s) scheme, cannot be resolved, or
    resolves (in whole or in part) to a non-public address.

    Note: userinfo/credentials embedded in a webhook URL are preserved by the
    IP-pinning adapter; the resolved IP replaces only the host component of the
    netloc.
    """
    if not valid_url(url):
        return None

    try:
        parsed = urlparse(url)
    except (ValueError, TypeError):
        LOG.error(f'Webhook URL {url} is invalid: could not be parsed')
        return None

    hostname = parsed.hostname
    if not hostname:
        LOG.error(f'Webhook URL {url} is invalid: no hostname')
        return None

    scheme = parsed.scheme.lower()
    if scheme not in ('http', 'https'):
        LOG.error(f'Webhook URL {url} is invalid: unsupported scheme {scheme}')
        return None

    try:
        addresses = socket.getaddrinfo(hostname, None)
    except (socket.gaierror, OSError, UnicodeError) as ex:
        LOG.error(f'Webhook URL {url} is invalid: could not resolve hostname {hostname}: {ex}')
        return None

    resolved_ip = None
    for address in addresses:
        ip_string = address[4][0].split('%')[0]
        ip = ipaddress.ip_address(ip_string)
        if (not ip.is_global or ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
            LOG.error(f'Webhook URL {url} is invalid: hostname {hostname} resolves to non-public address {ip_string}')
            return None
        if resolved_ip is None:
            resolved_ip = ip_string

    return resolved_ip


def valid_webhook_url(url):
    """Check if the given URL is a valid, publicly-resolvable webhook URL (SSRF-safe)."""
    return resolve_and_validate_webhook_url(url) is not None


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
    return status in ['Pending', 'Active', 'Disabled', 'Succeeded', 'Failed']


def valid_visibility(visibility):
    """Check if the given visibility is either 'Public' or 'Private'."""
    return visibility in ['Public', 'Private']


def valid_private_key(private_key):  # Todo better validation
    """Check if the given private key is a non-empty string."""
    return isinstance(private_key, str) and len(private_key) > 0


def valid_distribution(distribution):
    """Check if the given distribution dict maps valid addresses to valid amounts."""
    if not isinstance(distribution, dict) or len(distribution) == 0:
        return False

    return all(valid_address(key) and valid_amount(value) for key, value in distribution.items())


def valid_outputs(outputs):
    """Check if the given outputs list contains valid (address, amount) pairs."""
    valid = False

    if isinstance(outputs, list) and len(outputs) >= 1:
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
    return isinstance(actions, list) and all(isinstance(action_id, str) for action_id in actions)


def valid_timestamp(timestamp):
    """Check if the given timestamp is a positive integer."""
    return isinstance(timestamp, int) and timestamp > 0


def valid_phase(phase):
    """Check if the given phase is in the valid range (0-5)."""
    return phase in range(6)


def _resolve_script_path(script):
    """Resolve a script name to a (path, reason) pair within the allowed roots.

    Returns ``(absolute_real_path, None)`` when the script resolves to an existing
    file inside ``spellbookscripts/`` or ``apps/``. On failure it returns
    ``(None, reason)`` where ``reason`` is one of ``'invalid_type'`` (not a
    string), ``'invalid_extension'`` (not ending in ``.py``),
    ``'resolved_outside_roots'`` (resolves to an existing file outside the
    allowed roots, i.e. a path-traversal attempt) or ``'not_found'`` (no such
    file in the allowed roots).
    """
    if not isinstance(script, str):
        return None, 'invalid_type'

    if not script.endswith('.py'):
        return None, 'invalid_extension'

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    resolved_outside = False
    for root_dir in ('spellbookscripts', 'apps'):
        allowed_root = os.path.join(project_root, root_dir)
        try:
            candidate = safe_path(allowed_root, script)
        except ValueError:
            resolved_outside = True
            continue
        if os.path.isfile(candidate):
            return candidate, None

    if resolved_outside:
        return None, 'resolved_outside_roots'

    return None, 'not_found'


def find_script_path(script):
    """Return the absolute, real path of a script confined to the allowed roots.

    Returns None if script is not a string ending in .py, or if the resolved path
    does not live inside spellbookscripts/ or apps/ (defends against '..' segments,
    absolute paths and symlinks that escape the allowed roots).
    """
    path, _ = _resolve_script_path(script)
    return path


def valid_script(script):
    """Check if the given script name is a valid .py file in spellbookscripts or apps."""
    if not isinstance(script, str) or not script.endswith('.py'):
        LOG.error(f'Script {script} is invalid: must be a string ending in .py')
        return False

    path, reason = _resolve_script_path(script)
    if path is None:
        if reason == 'resolved_outside_roots':
            LOG.error(f'Script {script} is invalid: not found in or resolved outside spellbookscripts/apps')
        else:
            LOG.error(f'Script {script} is invalid: file not found in spellbookscripts or apps directory')
        return False

    return True


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
