#!/usr/bin/env python
"""Recombination (crossover) operations for Darwin."""

from copy import deepcopy
from random import randint

from darwin.genome import Genome


def recombine(parent_a, parent_b):
    """Recombine two parent genomes into an offspring by randomly choosing chromosomes from each parent."""
    offspring = Genome()

    for chromosome_id in parent_a.chromosomes:
        if randint(0, 1) == 0:
            offspring.chromosomes[chromosome_id] = deepcopy(parent_a.chromosomes[chromosome_id])
        else:
            offspring.chromosomes[chromosome_id] = deepcopy(parent_b.chromosomes[chromosome_id])

    return offspring
