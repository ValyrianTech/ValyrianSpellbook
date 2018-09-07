#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

from helpers.loghelpers import LOG
from helpers.configurationhelpers import get_use_testnet


def get_medium_priority_fee():
    data = get_recommended_fee_blockcypher()
    return int(data['medium_priority']/1024)


def get_low_priority_fee():
    data = get_recommended_fee_blockcypher()
    return int(data['low_priority']/1024)


def get_high_priority_fee():
    data = get_recommended_fee_blockcypher()
    return int(data['high_priority']/1024)


def get_recommended_fee():
    url = 'https://bitcoinfees.earn.com/api/v1/fees/recommended'

    try:
        LOG.info('GET %s' % url)
        r = requests.get(url=url)
        data = r.json()
    except Exception as ex:
        raise Exception('Unable get recommended fee from bitcoinfees.earn.com: %s' % ex)

    return {'high_priority': data['fastestFee']*1024,
            'low_priority': data['hourFee']*1024,
            'medium_priority': data['halfHourFee']*1024}


def get_recommended_fee_blockcypher():
    url = 'https://api.blockcypher.com/v1/btc/test3' if get_use_testnet() is True else 'https://api.blockcypher.com/v1/btc/main'

    try:
        LOG.info('GET %s' % url)
        r = requests.get(url=url)
        data = r.json()
    except Exception as ex:
        raise Exception('Unable get recommended fee from blockcypher.com: %s' % ex)

    return {'high_priority': data['high_fee_per_kb'],
            'low_priority': data['low_fee_per_kb'],
            'medium_priority': data['medium_fee_per_kb']}
