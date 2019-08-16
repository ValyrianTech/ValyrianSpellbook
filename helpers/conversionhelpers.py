#!/usr/bin/env python
# -*- coding: utf-8 -*-

from helpers.py2specials import *
from helpers.py3specials import *


def btc2satoshis(btc):
    if isinstance(btc, string_types):
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

    elif isinstance(btc, int_types):
        return int(btc*1e8)
    elif isinstance(btc, float):
        return int(btc*1e8)
    else:
        raise Exception('Invalid type for btc: %s' % type(btc))
