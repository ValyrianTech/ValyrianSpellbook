#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helper functions for converting between Bitcoin units."""


def btc2satoshis(btc):
    """Convert a BTC amount (string, int, or float) to an integer number of satoshis."""
    if isinstance(btc, str):
        if '.' in btc:
            parts = btc.split('.')
            if len(parts) == 2:
                whole_btc = int(parts[0])
                satoshis = int(parts[1].ljust(8, '0'))  # add zeros up to 8 decimals
                return int(whole_btc*1e8 + satoshis)
            else:
                raise Exception('String containing BTC value can only contain a single "."')
        else:
            return int(int(btc)*1e8)

    elif isinstance(btc, (int, float)):
        return int(btc*1e8)
    else:
        raise Exception('Invalid type for btc: %s' % type(btc))
