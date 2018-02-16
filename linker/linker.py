#!/usr/bin/env python
# -*- coding: utf-8 -*-

from data.data import balance
from helpers.BIP44 import get_addresses_from_xpub
from inputs.inputs import get_sil
from validators.validators import valid_address, valid_xpub


def get_lal(address, xpub, block_height=0):
    if not valid_address(address):
        return {'error': 'Invalid address: %s' % address}

    if not valid_xpub(xpub):
        return {'error': 'Invalid xpub: %s' % xpub}

    sil_data = get_sil(address, block_height)

    if 'SIL' in sil_data:
        sil = sil_data['SIL']
        linked_addresses = get_addresses_from_xpub(xpub, len(sil))

        lal = []
        for i in range(0, len(sil)):
            lal.append([sil[i][0], linked_addresses[i]])

        return {'LAL': lal}
    else:
        return {'error': 'Received invalid SIL data: %s' % sil_data}


def get_lbl(address, xpub, block_height=0):
    lal_data = get_lal(address, xpub, block_height)

    if 'error' in lal_data:
        return lal_data['error']

    lal = lal_data['LAL']

    lbl = []
    for i in range(0, len(lal)):
        address = lal[i][0]
        linked_balance = balance(lal[i][1])
        if 'balance' in linked_balance and 'final' in linked_balance['balance']:
            lbl.append([address, linked_balance['balance']['final']])
        else:
            return {'error': 'Failed to retrieve balance of %s' % lal[i][1]}

    total = float(sum([row[1] for row in lbl]))
    for row in lbl:
        row.append(row[1] / total if total > 0 else 0)

    return {'LBL': lbl}


def get_lrl(address, xpub, block_height=0):
    lal_data = get_lal(address, xpub, block_height)

    if 'error' in lal_data:
        return lal_data['error']

    lal = lal_data['LAL']

    lrl = []
    for i in range(0, len(lal)):
        address = lal[i][0]
        linked_balance = balance(lal[i][1])
        if 'balance' in linked_balance and 'received' in linked_balance['balance']:
            lrl.append([address, linked_balance['balance']['received']])
        else:
            return {'error': 'Failed to retrieve balance of %s' % lal[i][1]}

    total = float(sum([row[1] for row in lrl]))
    for row in lrl:
        row.append(row[1] / total if total > 0 else 0)

    return {'LRL': lrl}


def get_lsl(address, xpub, block_height=0):
    lal_data = get_lal(address, xpub, block_height)

    if 'error' in lal_data:
        return lal_data['error']

    lal = lal_data['LAL']

    lsl = []
    for i in range(0, len(lal)):
        address = lal[i][0]
        linked_balance = balance(lal[i][1])
        if 'balance' in linked_balance and 'sent' in linked_balance['balance']:
            lsl.append([address, linked_balance['balance']['sent']])
        else:
            return {'error': 'Failed to retrieve balance of %s' % lal[i][1]}

    total = float(sum([row[1] for row in lsl]))
    for row in lsl:
        row.append(row[1] / total if total > 0 else 0)

    return {'LSL': lsl}
