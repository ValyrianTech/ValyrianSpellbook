#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pytest
from unittest.mock import patch, MagicMock

from darwin.evolver import Evolver


def make_config(tmp_path):
    """Create a valid config dict for Evolver.load_config."""
    save_dir = str(tmp_path / 'saves')
    champions_dir = str(tmp_path / 'champions')
    darwin_dir = str(tmp_path / 'darwin')
    return {
        'title': 'test_job',
        'description': 'Test job description',
        'dir': darwin_dir,
        'save_dir': save_dir,
        'load_last_save': False,
        'champions_dir': champions_dir,
        'model_script': 'model/booleantest.py',
        'model_class': 'BooleanTest',
        'rosetta_stone_script': 'rosettastone/booleantestrosettastone.py',
        'rosetta_stone_class': 'BooleanTestRosettaStone',
        'fitness_function_script': 'fitnessfunction/booleantestfitnessfunction.py',
        'fitness_function_class': 'BooleanTestFitnessFunction',
        'periodic_save': 20,
        'population_size': 10,
        'target_fitness': 10000,
        'truncation': 25,
        'elitism': 1,
        'n_parents': 2,
        'recombination_type': 3,
        'tournament_size': 5,
        'max_generations': 100,
        'max_time_total': 300,
        'max_time_generation': 5,
        'stagnation': 100,
        'mutations': {
            'boolean': {'uniform': 10.0, 'flip': 10.0},
            'integer': {'uniform': 10.0, 'boundary': 10.0, 'gaussian': 10.0, 'gaussian_sigma': 1.0},
            'float': {'uniform': 10.0, 'boundary': 10.0, 'gaussian': 10.0, 'gaussian_sigma': 1.0},
            'string': {'uniform': 10.0, 'bitstring': 10.0, 'duplication': 10.0,
                       'deletion': 10.0, 'insertion': 10.0, 'swap': 10.0},
            'chromosome': {'uniform': 10.0, 'duplication': 10.0, 'deletion': 10.0,
                           'insertion': 10.0, 'swap': 10.0, 'split': 10.0, 'merge': 10.0}
        }
    }


class TestEvolverInit:

    def test_defaults(self):
        evolver = Evolver()
        assert evolver.title == 'Title of this job'
        assert evolver.description == 'A more detailed description of this job.'
        assert evolver.dir == r'D:\darwin'
        assert evolver.save_dir == r'D:\darwin\saves'
        assert evolver.load_last_save is False
        assert evolver.champions_dir == r'D:\darwin\champions'
        assert evolver.load_champions is False
        assert evolver.current_generation == 0
        assert evolver.elapsed_time == 0
        assert evolver.generations_since_new_champion == 0
        assert evolver.highest_fitness is None
        assert evolver.population_size == 100
        assert evolver.target_fitness == 10000
        assert evolver.truncation == 25
        assert evolver.elitism == 1
        assert evolver.n_parents == 2
        assert evolver.recombination_type == 3
        assert evolver.tournament_size == 5
        assert evolver.max_generations == 100
        assert evolver.max_time_total == 300
        assert evolver.max_time_generation == 5
        assert evolver.stagnation == 100
        assert evolver.periodic_save == 20

    def test_mutation_chances_initialized(self):
        evolver = Evolver()
        assert evolver.boolean_mutation_chance is not None
        assert evolver.integer_mutation_chance is not None
        assert evolver.float_mutation_chance is not None
        assert evolver.string_mutation_chance is not None
        assert evolver.chromosome_mutation_chance is not None


class TestLoadConfig:

    def test_load_config(self, tmp_path):
        evolver = Evolver()
        config = make_config(tmp_path)
        evolver.load_config(config)
        assert evolver.title == 'test_job'
        assert evolver.population_size == 10
        assert evolver.max_generations == 100
        assert evolver.boolean_mutation_chance.uniform == 10.0
        assert evolver.boolean_mutation_chance.flip == 10.0

    def test_load_config_creates_directories(self, tmp_path):
        evolver = Evolver()
        config = make_config(tmp_path)
        evolver.load_config(config)
        assert os.path.isdir(evolver.job_dir)
        assert os.path.isdir(evolver.champions_dir)
        assert os.path.isdir(evolver.save_dir)

    def test_load_config_non_dict_raises(self):
        evolver = Evolver()
        with pytest.raises(Exception, match='config is not a dict'):
            evolver.load_config("not a dict")

    def test_load_config_with_optional_keys(self, tmp_path):
        evolver = Evolver()
        config = make_config(tmp_path)
        config['load_champions'] = True
        config['scripts_dir'] = '/tmp/scripts'
        config['parameters'] = {'key': 'value'}
        evolver.load_config(config)
        assert evolver.load_champions is True
        assert evolver.scripts_dir == '/tmp/scripts'
        assert evolver.parameters == {'key': 'value'}

    def test_load_config_sets_progress_file(self, tmp_path):
        evolver = Evolver()
        config = make_config(tmp_path)
        evolver.load_config(config)
        assert evolver.progress_file is not None
        assert evolver.progress_file.endswith('progress.txt')


class TestSaveConfig:

    @patch('darwin.evolver.save_to_json_file')
    def test_save_config(self, mock_save):
        evolver = Evolver()
        evolver.save_config(filename='/tmp/test_config.json')
        mock_save.assert_called_once()
        call_args = mock_save.call_args
        assert call_args[1]['filename'] == '/tmp/test_config.json'
        config = call_args[1]['data']
        assert config['title'] == 'Title of this job'
        assert config['population_size'] == 100
        assert 'mutations' in config
        assert 'boolean' in config['mutations']
        assert 'integer' in config['mutations']
        assert 'float' in config['mutations']
        assert 'string' in config['mutations']
        assert 'chromosome' in config['mutations']


class TestTermination:

    def test_no_termination(self, tmp_path):
        evolver = Evolver()
        evolver.dir = str(tmp_path)
        evolver.max_generations = 0
        evolver.stagnation = 0
        evolver.max_time_total = 0
        evolver.target_fitness = 0
        assert evolver.termination() is False

    def test_max_generations_reached(self):
        evolver = Evolver()
        evolver.max_generations = 10
        evolver.current_generation = 10
        evolver.stagnation = 0
        evolver.max_time_total = 0
        evolver.target_fitness = 0
        assert evolver.termination() is True

    def test_stagnation_reached(self):
        evolver = Evolver()
        evolver.max_generations = 0
        evolver.stagnation = 50
        evolver.generations_since_new_champion = 50
        evolver.max_time_total = 0
        evolver.target_fitness = 0
        assert evolver.termination() is True

    def test_max_time_reached(self):
        evolver = Evolver()
        evolver.max_generations = 0
        evolver.stagnation = 0
        evolver.max_time_total = 100
        evolver.elapsed_time = 100
        evolver.target_fitness = 0
        assert evolver.termination() is True

    def test_target_fitness_reached(self):
        evolver = Evolver()
        evolver.max_generations = 0
        evolver.stagnation = 0
        evolver.max_time_total = 0
        evolver.target_fitness = 500
        evolver.highest_fitness = 500
        assert evolver.termination() is True

    def test_abort_file(self, tmp_path):
        evolver = Evolver()
        evolver.dir = str(tmp_path)
        evolver.max_generations = 0
        evolver.stagnation = 0
        evolver.max_time_total = 0
        evolver.target_fitness = 0
        abort_file = os.path.join(str(tmp_path), 'abort')
        with open(abort_file, 'w') as f:
            f.write('abort')
        assert evolver.termination() is True
        assert not os.path.exists(abort_file)

    def test_no_termination_when_conditions_not_met(self, tmp_path):
        evolver = Evolver()
        evolver.dir = str(tmp_path)
        evolver.max_generations = 100
        evolver.current_generation = 5
        evolver.stagnation = 100
        evolver.generations_since_new_champion = 10
        evolver.max_time_total = 300
        evolver.elapsed_time = 50
        evolver.target_fitness = 10000
        evolver.highest_fitness = 500
        assert evolver.termination() is False


class TestPrintSettings:

    def test_print_settings_no_parameters(self, capsys):
        evolver = Evolver()
        evolver.print_settings()
        captured = capsys.readouterr()
        assert 'Mutations' in captured.out

    def test_print_settings_with_parameters(self, capsys):
        evolver = Evolver()
        evolver.parameters = {'key': 'value'}
        evolver.print_settings()
        captured = capsys.readouterr()
        assert 'PARAMETERS' in captured.out
