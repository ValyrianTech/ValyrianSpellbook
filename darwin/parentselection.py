#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy


def roulette_wheel_selection(genomes, n_parents=2):
    # probabilities must all be non-negative, so shift all fitnesses with the lowest fitness value
    min_fitness = min([genome.fitness for genome in genomes])
    total_fitness = float(sum([genome.fitness - min_fitness for genome in genomes]))

    probabilities = None
    # If all fitnesses are equal, the selection will be completely random instead of based on fitness
    if total_fitness > 0:
        probabilities = [(genome.fitness - min_fitness)/total_fitness for genome in genomes]

    # Make sure there are more non-zero probabilities than n_parents, this could happen if all but one genome have the same fitness
    if probabilities is not None and len(probabilities) - probabilities.count(0.0) < n_parents:
        probabilities = None

    # Make sure we don't select more parents that there are genomes
    if n_parents > len(genomes):
        n_parents = len(genomes)

    # Select a sample of size n_parents with probabilities based on the fitness, parents can only be selected once in the sample
    selection = numpy.random.choice(genomes, size=n_parents, p=probabilities, replace=False)

    return selection


def rank_selection(genomes, n_parents=2):
    # Probability of being selected depends on rank instead of fitness
    ranks = range(len(genomes), 0, -1)  # genomes are sorted from highest fitness to lowest, so the first genome must highest probability
    total = float(sum(ranks))
    probabilities = [rank/total for rank in ranks]

    # Make sure we don't select more parents that there are genomes
    if n_parents > len(genomes):
        n_parents = len(genomes)

    # Select a sample of size n_parents with probabilities based on the rank, parents can only be selected once in the sample
    selection = numpy.random.choice(genomes, size=n_parents, p=probabilities, replace=False)

    return selection


def stochastic_universal_sampling(genomes, n_parents=10):
    # probabilities must all be non-negative, so shift all fitnesses with the lowest fitness value
    min_fitness = min([genome.fitness for genome in genomes])
    total_fitness = float(sum([genome.fitness - min_fitness for genome in genomes]))
    step_size = total_fitness/float(n_parents)
    rand = numpy.random.uniform(0, total_fitness)
    selection = []
    for i in range(n_parents):

        accumulated_fitness = 0.0
        for genome in genomes:
            accumulated_fitness += genome.fitness - min_fitness

            if accumulated_fitness >= rand:
                selection.append(genome)
                break

        rand += step_size
        if rand >= total_fitness:
            rand -= total_fitness

    return selection


def tournament_selection(genomes, n_parents=2, tournament_size=5):
    selection = []

    if tournament_size > len(genomes):
        tournament_size = len(genomes)

    for i in range(n_parents):
        # Note: it is possible that a parent is selected more than once
        # Select a sample of size tournament_size from a list containing the indexes of all genomes
        tournament = numpy.random.choice(range(len(genomes)), size=tournament_size, replace=False)

        # The genomes are already sorted by highest fitness, so add the genome with the index of the winner of the tournament
        selection.append(genomes[sorted(tournament)[0]])

    return selection
