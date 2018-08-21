#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

from data.data import get_explorer_api
from helpers.loghelpers import LOG


def get_optimal_fee():
    blocktrail = get_explorer_api('blocktrail.com')
    data = blocktrail.get_recommended_fee() if blocktrail is not None else get_recommended_fee()
    return int(data['optimal']/1024)


def get_low_priority_fee():
    blocktrail = get_explorer_api('blocktrail.com')
    data = blocktrail.get_recommended_fee() if blocktrail is not None else get_recommended_fee()
    return int(data['low_priority']/1024)


def get_high_priority_fee():
    blocktrail = get_explorer_api('blocktrail.com')
    data = blocktrail.get_recommended_fee() if blocktrail is not None else get_recommended_fee()
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
            'optimal': data['halfHourFee']*1024}
