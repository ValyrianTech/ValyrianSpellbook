#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import randint
from darwin.genome import Genome

from copy import deepcopy


def recombine(parent_a, parent_b):
    offspring = Genome()

    for chromosome_id in parent_a.chromosomes.keys():
        if randint(0, 1) == 0:
            offspring.chromosomes[chromosome_id] = deepcopy(parent_a.chromosomes[chromosome_id])
        else:
            offspring.chromosomes[chromosome_id] = deepcopy(parent_b.chromosomes[chromosome_id])

    return offspring
