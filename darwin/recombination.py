#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import randint
from genome import Genome

from copy import deepcopy


def recombine(parent_a, parent_b):
    if not (isinstance(parent_a, Genome) and isinstance(parent_b, Genome)):
        raise Exception('Can not recombine: both parents must be of type Genome')

    offspring = Genome()

    for chromosome_id in parent_a.chromosomes.keys():
        if randint(0, 1) == 0:
            offspring.chromosomes[chromosome_id] = deepcopy(parent_a.chromosomes[chromosome_id])
        else:
            offspring.chromosomes[chromosome_id] = deepcopy(parent_b.chromosomes[chromosome_id])

    return offspring
