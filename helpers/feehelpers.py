#!/usr/bin/env python
"""Helper functions for retrieving recommended Bitcoin transaction fees."""
import math

import requests

from helpers.configurationhelpers import get_use_testnet
from helpers.http_helpers import DEFAULT_HTTP_TIMEOUT
from helpers.loghelpers import LOG

MIN_SAT_PER_BYTE = 1


def _per_byte(fee_per_kb):
    """Convert a per-kilobyte fee into a ceiled per-byte rate clamped to at least MIN_SAT_PER_BYTE."""
    rate = math.ceil(int(fee_per_kb) / 1024)
    return max(rate, MIN_SAT_PER_BYTE)


def get_medium_priority_fee():
    """Get the medium-priority fee per byte from BlockCypher."""
    data = get_recommended_fee_blockcypher()
    return _per_byte(data['medium_priority'])


def get_low_priority_fee():
    """Get the low-priority fee per byte from BlockCypher."""
    data = get_recommended_fee_blockcypher()
    return _per_byte(data['low_priority'])


def get_high_priority_fee():
    """Get the high-priority fee per byte from BlockCypher."""
    data = get_recommended_fee_blockcypher()
    return _per_byte(data['high_priority'])


def get_recommended_fee():
    """Get recommended fees from bitcoinfees.earn.com."""
    url = 'https://bitcoinfees.earn.com/api/v1/fees/recommended'

    try:
        LOG.info(f'GET {url}')
        r = requests.get(url=url, timeout=DEFAULT_HTTP_TIMEOUT)
        data = r.json()
    except (ValueError, KeyError, TypeError, OSError) as ex:
        raise ValueError(f'Unable get recommended fee from bitcoinfees.earn.com: {ex}')

    return {'high_priority': data['fastestFee']*1024,
            'low_priority': data['hourFee']*1024,
            'medium_priority': data['halfHourFee']*1024}


def get_recommended_fee_blockcypher():
    """Get recommended fees from BlockCypher API (testnet or mainnet)."""
    url = 'https://api.blockcypher.com/v1/btc/test3' if get_use_testnet() is True else 'https://api.blockcypher.com/v1/btc/main'

    try:
        LOG.info(f'GET {url}')
        r = requests.get(url=url, timeout=DEFAULT_HTTP_TIMEOUT)
        data = r.json()
    except (ValueError, KeyError, TypeError, OSError) as ex:
        raise ValueError(f'Unable get recommended fee from blockcypher.com: {ex}')

    return {'high_priority': data['high_fee_per_kb'],
            'low_priority': data['low_fee_per_kb'],
            'medium_priority': data['medium_fee_per_kb']}
