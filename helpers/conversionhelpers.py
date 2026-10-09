#!/usr/bin/env python
"""Helper functions for converting between Bitcoin units."""

from decimal import Decimal, InvalidOperation, ROUND_DOWN


def btc2satoshis(btc):
    """Convert a BTC amount (string, int, or float) to an integer number of satoshis."""
    if not isinstance(btc, (str, int, float)):
        raise TypeError(f'Invalid type for btc: {type(btc)}')

    if isinstance(btc, str) and btc.count('.') > 1:
        raise ValueError('String containing BTC value can only contain a single "."')

    try:
        value = Decimal(str(btc))
    except InvalidOperation as e:
        raise TypeError(f'Invalid type for btc: {type(btc)}') from e

    satoshis = (value * 100_000_000).to_integral_value(rounding=ROUND_DOWN)
    return int(satoshis)
