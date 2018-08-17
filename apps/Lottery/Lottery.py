#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from data.data import block_by_height
from helpers.BIP44 import set_testnet
from helpers.actionhelpers import get_actions, get_action
from helpers.triggerhelpers import get_trigger
from helpers.configurationhelpers import get_use_testnet
from helpers.hotwallethelpers import get_address_from_wallet
from helpers.loghelpers import LOG
from randomaddress.randomaddress import random_address_from_sil
from spellbookscripts.spellbookscript import SpellbookScript

set_testnet(get_use_testnet())


class Lottery(SpellbookScript):

    def run(self):
        LOG.info('Running Spellbook Script: %s' % os.path.splitext(os.path.basename(__file__))[0])

        trigger = get_trigger(trigger_id=self.trigger_id)
        LOG.info('Lottery winner is determined at block height %s' % trigger.block_height)

        # Double check the block at the specified height has been mined already (even though the trigger should not activate before the specified blockheight + number of confirmations)
        block_data = block_by_height(height=trigger.block_height)
        if 'block' in block_data:
            block_hash = block_data['block']['hash']
        else:
            LOG.error('Unable to get the block hash of block %s to determine the winner of the lottery' % trigger.block_height)
            return

        LOG.info('Picking the winner with block %s (%s)' % (trigger.block_height, block_hash))

        action_id = 'Lottery-payout'
        if action_id not in get_actions():
            LOG.error('Can not modify action %s: action not found' % action_id)
            return

        action = get_action(action_id=action_id)

        lottery_address = get_address_from_wallet(account=action.bip44_account, index=action.bip44_index)
        LOG.info('Getting SIL from lottery address %s' % lottery_address)

        random_address_data = random_address_from_sil(address=lottery_address, sil_block_height=trigger.block_height, rng_block_height=trigger.block_height)
        LOG.info('random_address_data: %s' % random_address_data)
        if 'chosen_address' not in random_address_data:
            LOG.error('Failed to get winning address')
            return

        winning_address = random_address_data['chosen_address']
        LOG.info('Winning address: %s' % winning_address)
        LOG.info('Distribution: %s' % random_address_data['distribution'])

        LOG.info('Configuring action Lottery-payout')
        action.receiving_address = winning_address

        # Also set the amount to send in the payout, just in case someone sends a transaction to the lottery after the winner has been picked
        # Todo this (how to get the balance at a specific time?)

        action.save()
        LOG.info('Action Lottery-payout is configured')

        self.attach_action('Lottery-payout')

    def cleanup(self):
        # Clear the actions so the payout doesn't happen multiple times
        trigger = get_trigger(trigger_id=self.trigger_id)
        trigger.actions = []
        trigger.save()
        LOG.info('Actions have been cleared from trigger %s' % self.trigger_id)

















