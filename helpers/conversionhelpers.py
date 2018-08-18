#!/usr/bin/env python
# -*- coding: utf-8 -*-


def btc2satoshis(btc):
    if isinstance(btc, (str, unicode)):
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

    elif isinstance(btc, (int, long)):
        return int(btc*1e8)
    elif isinstance(btc, float):
        return int(btc*1e8)
    else:
        raise Exception('Invalid type for btc: %s' % type(btc))
