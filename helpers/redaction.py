#!/usr/bin/env python
"""Single source of truth for sensitive-key redaction.

This module defines the canonical set of sensitive configuration keys and the
helpers used to recognise and redact them. Both the REST API server
(``spellbookserver.py``) and ``helpers.actionhelpers`` import from here so that
the two cannot drift apart.
"""

SENSITIVE_KEYS = {'api_key', 'api_secret', 'secret', 'private_key', 'privkey', 'mnemonic', 'xpriv', 'password', 'passphrase', 'seed', 'API_Sign', 'API_Key'}

REDACTED_VALUE = '********'

NORMALIZED_SENSITIVE_KEYS = frozenset(key.lower() for key in SENSITIVE_KEYS)


def is_sensitive_key(name):
    """Return True if name is a sensitive key, matching case-insensitively.

    :param name: A mapping key to test (may be a non-str value)
    :return: True when name is a str and its lowercased form is in
             NORMALIZED_SENSITIVE_KEYS; False otherwise (including non-str/None)
    """
    return isinstance(name, str) and name.lower() in NORMALIZED_SENSITIVE_KEYS


def redact(mapping):
    """Return a copy of mapping with sensitive values redacted.

    Values are replaced with REDACTED_VALUE for any key where
    is_sensitive_key(key) is True; all other key/value pairs are preserved.

    :param mapping: A dict-like mapping to redact
    :return: A new dict with sensitive values redacted
    """
    return {
        key: REDACTED_VALUE if is_sensitive_key(key) else value
        for key, value in mapping.items()
    }
