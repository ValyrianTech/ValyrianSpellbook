#!/usr/bin/env python
# -*- coding: utf-8 -*-

from data.data import get_explorer_api


def get_optimal_fee():
    blocktrail = get_explorer_api('blocktrail.com')
    data = blocktrail.get_recommended_fee()
    return int(data['optimal']/1024)


def get_low_priority_fee():
    blocktrail = get_explorer_api('blocktrail.com')
    data = blocktrail.get_recommended_fee()
    return int(data['low_priority']/1024)


def get_high_priority_fee():
    blocktrail = get_explorer_api('blocktrail.com')
    data = blocktrail.get_recommended_fee()
    return int(data['high_priority']/1024)