#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import platform
import importlib
import time
from pprint import pprint
import random

from darwin.fitnessfunction.fitnessfunction import FitnessFunction
from darwin.rosettastone.rosettastone import RosettaStone
from darwin.model.model import Model

from helpers.jsonhelpers import load_from_json_file, save_to_json_file
from darwin.mutationchance import BooleanMutationChance, IntegerMutationChance, FloatMutationChance, StringMutationChance, ChromosomeMutationChance
from darwin.parentselection import roulette_wheel_selection, rank_selection, stochastic_universal_sampling, tournament_selection
from darwin.population import Population
from darwin.recombination import recombine
from darwin.encodingtype import EncodingType

DARWIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
SPELLBOOK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Evolver(object):
    def __init__(self):
        self.title = 'Title of this job'
        self.description = 'A more detailed description of this job.'
        self.dir = r'D:\darwin'
        self.save_dir = r'D:\darwin\saves'
        self.load_last_save = False
        self.champions_dir = r'D:\darwin\champions'
        self.load_champions = False
        self.job_dir = None
        self.progress_file = None

        # Termination variables
        self.current_generation = 0
        self.elapsed_time = 0
        self.generations_since_new_champion = 0
        self.highest_fitness = None

        self.scripts_dir = None

        self.model_script = None
        self.model_class = None

        self.rosetta_stone_script = None
        self.rosetta_stone_class = None

        self.fitness_function_script = None
        self.fitness_function_class = None

        self.periodic_save = 20

        # Settings
        self.population_size = 100
        self.target_fitness = 10000
        self.truncation = 25
        self.truncation_normalization = 1
        self.elitism = 1
        self.n_parents = 2
        self.recombination_type = 3  # RWS, SUS or tournament
        self.tournament_size = 5

        # Termination
        self.max_generations = 100
        self.max_time_total = 300
        self.max_time_generation = 5
        self.stagnation = 100

        # Mutations
        self.boolean_mutation_chance = BooleanMutationChance()
        self.integer_mutation_chance = IntegerMutationChance()
        self.float_mutation_chance = FloatMutationChance()
        self.string_mutation_chance = StringMutationChance()
        self.chromosome_mutation_chance = ChromosomeMutationChance()

    def load_config(self, config):
        if not isinstance(config, dict):
            raise Exception('config is not a dict!')

        self.title = config['title']
        self.description = config['description']
        self.dir = config['dir']
        self.save_dir = config['save_dir']
        self.load_last_save = config['load_last_save']
        self.champions_dir = config['champions_dir']
        self.load_champions = config['load_champions'] if 'load_champions' in config else False

        self.scripts_dir = config['scripts_dir'] if 'scripts_dir' in config else None
        self.model_script = config['model_script']
        self.model_class = config['model_class']
        self.rosetta_stone_script = config['rosetta_stone_script']
        self.rosetta_stone_class = config['rosetta_stone_class']
        self.fitness_function_script = config['fitness_function_script']
        self.fitness_function_class = config['fitness_function_class']

        self.periodic_save = config['periodic_save']

        # Settings
        self.population_size = config['population_size']
        self.target_fitness = config['target_fitness']
        self.truncation = config['truncation']
        self.elitism = config['elitism']
        self.n_parents = config['n_parents']
        self.recombination_type = config['recombination_type']  # RWS, SUS or tournament
        self.tournament_size = config['tournament_size']

        # Termination
        self.max_generations = config['max_generations']
        self.max_time_total = config['max_time_total']
        self.max_time_generation = config['max_time_generation']
        self.stagnation = config['stagnation']

        # Mutations
        self.boolean_mutation_chance.load(config['mutations']['boolean'])
        self.integer_mutation_chance.load(config['mutations']['integer'])
        self.float_mutation_chance.load(config['mutations']['float'])
        self.string_mutation_chance.load(config['mutations']['string'])
        self.chromosome_mutation_chance.load(config['mutations']['chromosome'])

        self.job_dir = os.path.join(self.save_dir, self.title)
        if not os.path.isdir(self.job_dir):
            os.makedirs(self.job_dir)

        if not os.path.isdir(self.champions_dir):
            os.makedirs(self.champions_dir)

        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)

        self.progress_file = os.path.join(DARWIN_DIR, 'progress.txt')

    def save_config(self, filename):

        config = {'title': self.title,
                  'description': self.description,
                  'dir': self.dir,
                  'save_dir': self.save_dir,
                  'load_last_save': self.load_last_save,
                  'champions_dir': self.champions_dir,
                  'model_script': self.model_script,
                  'model_class': self.model_class,
                  'rosetta_stone_script': self.rosetta_stone_script,
                  'rosetta_stone_class': self.rosetta_stone_class,
                  'fitness_function_script': self.fitness_function_script,
                  'fitness_function_class': self.fitness_function_class,
                  'periodic_save': self.periodic_save,
                  'population_size': self.population_size,
                  'target_fitness': self.target_fitness,
                  'truncation': self.truncation,
                  'truncation_normalization': self.truncation_normalization,
                  'elitism': self.elitism,
                  'n_parents': self.n_parents,
                  'recombination_type': self.recombination_type,
                  'tournament_size': self.tournament_size,
                  'max_generations': self.max_generations,
                  'max_time_total': self.max_time_total,
                  'max_time_generation': self.max_time_generation,
                  'stagnation': self.stagnation,
                  'mutations': {
                      'boolean': self.boolean_mutation_chance.__dict__,
                      'integer': self.integer_mutation_chance.__dict__,
                      'float': self.float_mutation_chance.__dict__,
                      'string': self.string_mutation_chance.__dict__,
                      'chromosome': self.chromosome_mutation_chance.__dict__}
                  }

        save_to_json_file(filename=filename, data=config)

    def print_settings(self):
        pprint(self.__dict__)
        pprint('Mutations')
        pprint('Boolean')
        pprint(self.boolean_mutation_chance.__dict__)
        pprint('Integer')
        pprint(self.integer_mutation_chance.__dict__)
        pprint('Float')
        pprint(self.float_mutation_chance.__dict__)
        pprint('String')
        pprint(self.string_mutation_chance.__dict__)
        pprint('Chromosome')
        pprint(self.chromosome_mutation_chance.__dict__)

    def start(self):
        population = Population()

        # Load the Model script
        model = self.load_script(script=self.model_script,
                                 script_class_name=self.model_class)

        if not isinstance(model, Model):
            raise Exception('Script %s is not a valid Model Script, instead it is a %s' % (model, type(model)))

        model.darwin_init_actions()
        model.info()

        # Load the RosettaStone script
        rosetta_stone = self.load_script(script=self.rosetta_stone_script,
                                         script_class_name=self.rosetta_stone_class)

        if not isinstance(rosetta_stone, RosettaStone):
            raise Exception('Script %s is not a valid RosettaStone Script, instead it is a %s' % (rosetta_stone, type(rosetta_stone)))

        # Load the FitnessFunction script
        fitness_function = self.load_script(script=self.fitness_function_script,
                                            script_class_name=self.fitness_function_class)

        fitness_function.darwin_init_actions()

        if not isinstance(fitness_function, FitnessFunction):
            raise Exception('Script %s is not a valid FitnessFunction Script, instead it is a %s' % (fitness_function, type(fitness_function)))

        if self.load_last_save is True:
            # Load saved generation
            population.load_directory(directory=self.job_dir)
        elif self.load_champions is True:
            # Load previous champions
            population.load_directory(directory=self.champions_dir)

        if len(population.genomes) < self.population_size:
            # Initialize all genomes in the population
            for i in range(self.population_size - len(population.genomes)):
                genome = rosetta_stone.genome_template()

                # Fill the genome with random data
                genome.init_with_random_data()
                population.add_genome(genome)

        champion = population.genomes[0]

        evolver_start_time = time.time()

        # Remove the progress file from earlier runs to start with a clean slate
        if os.path.isfile(self.progress_file):
            os.remove(self.progress_file)

        while not self.termination():
            self.current_generation += 1
            generation_start_time = time.time()
            print('\n\n=========================================')
            print('Calculating generation %s in %s' % (self.current_generation, self.title))
            next_generation = Population()

            for j, genome in enumerate(population.genomes):
                # Translate the genome to the model
                model_template = rosetta_stone.genome_to_model(genome=genome)
                model.configure(config=model_template)

                genome.fitness = fitness_function.fitness(model=model)

                print('Genome %s (%s): %s' % (j, genome.id(), genome.fitness))

                if 0 < self.max_time_generation <= generation_start_time + self.max_time_generation:
                    print('Generation is taking too long to calculate, skipping to next generation')
                    break

            # Sort the population by highest fitness
            population.genomes = sorted(population.genomes, key=lambda x: -x.fitness)

            # Periodically save the current population as json files
            if self.periodic_save > 0 and self.current_generation % self.periodic_save == 0:
                population.save(directory=self.job_dir)

            # Truncate the population by removing the worst performing genomes so they don't have a chance to be selected for recombination
            population.genomes = population.genomes[:int((len(population.genomes) * self.truncation) / 100)]

            if self.highest_fitness is None or population.genomes[0].fitness > self.highest_fitness:
                self.highest_fitness = population.genomes[0].fitness
                champion = population.genomes[0]
                self.generations_since_new_champion = 0
            else:
                self.generations_since_new_champion += 1

            print('Highest fitness: %s' % self.highest_fitness)
            print('Generations since improvement: %s' % self.generations_since_new_champion)

            with open(self.progress_file, 'a') as output_file:
                output_file.write('%s;%s;%s;%s\n' % (int(time.time()), self.current_generation, self.highest_fitness, (time.time()-generation_start_time)))

            # Set a new random seed because some models might use a specific seed which could influence the evolution process
            random.seed(time.time())

            # Calculate how many different genomes are left after truncation
            diversity = len(set([genome.id() for genome in population.genomes]))
            print('Diversity: %s different genomes' % diversity)

            # If there is not enough diversity, then evolution will slow down, so set a multiplier for the mutation chances that gets bigger if diversity is low
            # or when there hasn't been a new champion for many generations
            mutation_multiplier = len(population.genomes) / float(diversity) + self.generations_since_new_champion * 0.01
            print('Mutation multiplier: %s' % mutation_multiplier)

            # Recombine the best genomes into the next generation
            for i in range(self.population_size - self.elitism):
                if self.recombination_type == 1:
                    parent_a, parent_b = roulette_wheel_selection(genomes=population.genomes, n_parents=self.n_parents)
                elif self.recombination_type == 2:
                    parent_a, parent_b = rank_selection(genomes=population.genomes, n_parents=self.n_parents)
                elif self.recombination_type == 3:
                    parent_a, parent_b = stochastic_universal_sampling(genomes=population.genomes, n_parents=self.n_parents)
                elif self.recombination_type == 4:
                    parent_a, parent_b = tournament_selection(genomes=population.genomes, n_parents=self.n_parents, tournament_size=self.tournament_size)
                else:
                    raise NotImplementedError('Unknown recombination type: %s' % self.recombination_type)

                offspring = recombine(parent_a=parent_a, parent_b=parent_b)
                next_generation.add_genome(offspring)

            # Apply mutations to the next generation
            for genome in next_generation.genomes:
                for chromosome_id, chromosome in genome.chromosomes.items():
                    # Apply chromosome mutations
                    chromosome.apply_mutations(mutation_chance=self.chromosome_mutation_chance, multiplier=mutation_multiplier)

                    for gene in chromosome.genes:
                        # Apply gene mutations
                        if chromosome.encoding_type == EncodingType.BOOLEAN:
                            gene.apply_mutations(mutation_chance=self.boolean_mutation_chance, multiplier=mutation_multiplier)
                        elif chromosome.encoding_type == EncodingType.INTEGER:
                            gene.apply_mutations(mutation_chance=self.integer_mutation_chance, multiplier=mutation_multiplier)
                        elif chromosome.encoding_type == EncodingType.FLOAT:
                            gene.apply_mutations(mutation_chance=self.float_mutation_chance, multiplier=mutation_multiplier)
                        elif chromosome.encoding_type == EncodingType.STRING:
                            gene.apply_mutations(mutation_chance=self.string_mutation_chance, multiplier=mutation_multiplier)
                        else:
                            raise NotImplementedError('Unknown encoding type: %s' % chromosome.encoding_type)

            # Copy the n genomes with highest fitness to the next generation if elitism is greater than 0,
            # these genomes will not be modified by mutations
            for i in range(self.elitism):
                if len(population.genomes) > i:
                    next_generation.add_genome(genome=population.genomes[i])

            # Copy the next generation to the current population for the next iteration of the loop
            population.genomes = next_generation.genomes

            self.elapsed_time = time.time() - evolver_start_time

        # Print out the best solution
        print('\n\nBest solution:')
        print('--------------')
        print(champion.info())
        model_template = rosetta_stone.genome_to_model(champion)
        pprint(model_template)
        print('\nFitness: %s' % champion.fitness)

        model.configure(config=model_template)
        model.champion_actions()

        champion_file = os.path.join(self.champions_dir, '%s.json' % champion.id())
        save_to_json_file(filename=champion_file, data=champion.to_dict())

        return champion.fitness

    def load_script(self, script, script_class_name):
        script_name = script[:-3]  # script name without the .py extension
        script_path = os.path.join(SPELLBOOK_DIR, script)

        # Search for the script in the darwin directory
        if os.path.isfile(os.path.join(DARWIN_DIR, script)):
            script_path = os.path.join(DARWIN_DIR, script)
        elif os.path.isfile(os.path.join(SPELLBOOK_DIR, script)):
            script_path = os.path.join(SPELLBOOK_DIR, script)

        if script_path is None:
            print('Can not find script %s' % script)
            print(os.getcwd())
            return

        if platform.system() == 'Windows':
            script_module_name = '%s' % script_name.replace('\\', '.')
        elif platform.system() == 'Linux':
            script_module_name = '%s' % script_name.replace('/', '.')
        else:
            raise NotImplementedError('Unsupported platform: only windows and linux are supported')

        print('Loading Script %s' % script_path)
        print('Loading module %s' % script_module_name)
        try:
            script_module = importlib.import_module(script_module_name)
        except Exception as ex:
            print('Failed to load Spellbook Script %s: %s' % (script_path, ex))
            return

        darwin_script = getattr(script_module, script_class_name)
        kwargs = {}

        loaded_script = darwin_script(**kwargs)

        return loaded_script

    def termination(self):
        if 0 < self.max_generations <= self.current_generation:
            print('Maximum number of generations has been reached, stopping now')
            return True

        if 0 < self.stagnation <= self.generations_since_new_champion:
            print('Evolution has stagnated, stopping now')
            return True

        if 0 < self.max_time_total <= self.elapsed_time:
            print('Maximum time for evolution has been reached, stopping now')
            return True

        if 0 < self.target_fitness <= self.highest_fitness:
            print('Target fitness has been reached, stopping now')
            return True

        # check if there is a file called 'abort' in the darwin directory
        abort_file = os.path.join(self.dir, 'abort')
        if os.path.exists(abort_file) is True:
            print('Manual abort file detected, stopping now')
            os.remove(abort_file)  # Remove the abort file
            return True

        return False
