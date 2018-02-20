#!/usr/bin/env python
# -*- coding: utf-8 -*-

from validators.validators import valid_address, valid_xpub
from data.data import block_by_height, latest_block
from inputs.inputs import get_sil, get_sul
from linker.linker import get_lbl, get_lrl, get_lsl


def random_number_from_blockhash(block_height=0):
    """
    Get a random number between 0 and 1.
    The block_hash of a block at a given height is used to generate the random number in the following way:
    The hash is converted to an integer and then the integer is added to '0.' in reverse order

    :param block_height: The block height of the block_hash to use as a random number (default=0 (latest block))
    :return: A random number between 0 and 1
    """
    block_data = block_by_height(block_height) if block_height != 0 else latest_block()

    if 'block' in block_data and 'hash' in block_data['block']:
        block_hash = block_data['block']['hash']

        # Convert the block_hash to an integer
        hash_as_integer = int(block_hash, 16)

        # Add the digits in reversed order to '0.'
        random_number_as_string = '0.'
        for digit in reversed(str(hash_as_integer)):
            random_number_as_string += digit

        # Convert the full string to a float
        return float(random_number_as_string)


def random_address_from_sil(address, sil_block_height=0, rng_block_height=0):
    if not valid_address(address):
        return {'error': 'Invalid address: %s' % address}

    return RandomAddress(address=address,
                         sil_block_height=sil_block_height).get(source='SIL',
                                                                rng_block_height=rng_block_height)


def random_address_from_sul(address, sil_block_height=0, rng_block_height=0):
    if not valid_address(address):
        return {'error': 'Invalid address: %s' % address}

    return RandomAddress(address=address,
                         sil_block_height=sil_block_height).get(source='SUL',
                                                                rng_block_height=rng_block_height)


def random_address_from_lbl(address, xpub, sil_block_height=0, rng_block_height=0):
    if not valid_address(address):
        return {'error': 'Invalid address: %s' % address}

    if not valid_xpub(xpub):
        return {'error': 'Invalid xpub: %s' % xpub}

    return RandomAddress(address=address,
                         xpub=xpub,
                         sil_block_height=sil_block_height).get(source='LBL',
                                                                rng_block_height=rng_block_height)


def random_address_from_lrl(address, xpub, sil_block_height=0, rng_block_height=0):
    if not valid_address(address):
        return {'error': 'Invalid address: %s' % address}

    if not valid_xpub(xpub):
        return {'error': 'Invalid xpub: %s' % xpub}

    return RandomAddress(address=address,
                         xpub=xpub,
                         sil_block_height=sil_block_height).get(source='LRL',
                                                                rng_block_height=rng_block_height)


def random_address_from_lsl(address, xpub, sil_block_height=0, rng_block_height=0):
    if not valid_address(address):
        return {'error': 'Invalid address: %s' % address}

    if not valid_xpub(xpub):
        return {'error': 'Invalid xpub: %s' % xpub}

    return RandomAddress(address=address,
                         xpub=xpub,
                         sil_block_height=sil_block_height).get(source='LSL',
                                                                rng_block_height=rng_block_height)


class RandomAddress(object):
    def __init__(self, address, sil_block_height=0, xpub=None):
        self.address = address
        self.block_height = sil_block_height
        self.xpub = xpub

    def get(self, source, rng_block_height=0):
        distribution = self.get_distribution(source)
        random_number = random_number_from_blockhash(rng_block_height)

        response = {'distribution_source': source,
                    'distribution': distribution,
                    'random_number': random_number}

        response.update(self.results(distribution, random_number))

        return response

    def get_distribution(self, source):
        """
        Get the distribution values for the random address

        :param source: The type of the distribution source (SIL, LBL, LRL or LSL)
        :return: A list of items each containing (address, value)
        """
        if source == 'SIL':
            distribution_data = get_sil(self.address, self.block_height)
        elif source == 'SUL':
            distribution_data = get_sul(self.address, confirmations=1)
        elif source == 'LBL':
            distribution_data = get_lbl(self.address, self.xpub, self.block_height)
        elif source == 'LRL':
            distribution_data = get_lrl(self.address, self.xpub, self.block_height)
        elif source == 'LSL':
            distribution_data = get_lsl(self.address, self.xpub, self.block_height)
        else:
            raise NotImplementedError('Unknown distribution source: %s' % source)

        return [(item[0], item[1]) for item in distribution_data[source]]

    def results(self, distribution, random_number):
        """
        Pick an address from a given distribution and a random number

        :param distribution: A list of (address, value) tuples
        :param random_number: A floating point number between 0 and 1
        :return: A dict containing:
                    'chosen_address': The address that was picked
                    'chosen_index': The index of the address in the distribution
                    'target': The total of the values in the distribution multiplied by the random number
        """
        if not distribution:
            return {}

        values = [item[1] for item in distribution]
        chosen_index = self.get_chosen_index(values, random_number)
        chosen_address = distribution[chosen_index][0]

        return {'chosen_address': chosen_address,
                'chosen_index': chosen_index,
                'target': sum(values) * random_number}

    @staticmethod
    def get_chosen_index(values, random_number):
        """
        Get the index of the value that was chosen by the random number
        The chosen value is the first value where the cumulative value is higher or equal to the random_number * total_value

        :param values: A list of integer values
        :param random_number: A floating number between 0 and 1
        :return: The index of the value that was chosen
        """
        total = sum(values)

        if total > 0:
            target = random_number*total
            cumulative = 0.0
            for i in range(0, len(values)):
                cumulative = cumulative + values[i]
                if cumulative >= target:
                    return i
