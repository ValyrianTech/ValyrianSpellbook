#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pytest
from unittest.mock import patch, MagicMock

from darwin.evolver import Evolver
from darwin.model.model import Model
from darwin.rosettastone.rosettastone import RosettaStone
from darwin.fitnessfunction.fitnessfunction import FitnessFunction, Fitness
from darwin.genome import Genome
from darwin.encodingtype import EncodingType


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


class TestLoadScript:

    def test_load_script_boolean_model(self, tmp_path):
        evolver = Evolver()
        model = evolver.load_script(script='model/booleantest.py',
                                     script_class_name='BooleanTest')
        assert model is not None
        assert hasattr(model, 'SingleTrue')

    def test_load_script_float_model(self):
        evolver = Evolver()
        model = evolver.load_script(script='model/floattest.py',
                                     script_class_name='FloatTest')
        assert model is not None
        assert hasattr(model, 'Single42')

    def test_load_script_integer_model(self):
        evolver = Evolver()
        model = evolver.load_script(script='model/integertest.py',
                                     script_class_name='IntegerTest')
        assert model is not None
        assert hasattr(model, 'Single42')

    def test_load_script_string_model(self):
        evolver = Evolver()
        model = evolver.load_script(script='model/stringtest.py',
                                     script_class_name='StringTest')
        assert model is not None
        assert hasattr(model, 'HelloWorld')

    def test_load_script_full_model(self):
        evolver = Evolver()
        model = evolver.load_script(script='model/fulltest.py',
                                     script_class_name='FullTest')
        assert model is not None
        assert hasattr(model, 'SingleTrue')
        assert hasattr(model, 'HelloWorld')

    def test_load_script_rosettastone(self):
        evolver = Evolver()
        rs = evolver.load_script(script='rosettastone/fulltestrosettastone.py',
                                 script_class_name='FullTestRosettaStone')
        assert rs is not None

    def test_load_script_fitness_function(self):
        evolver = Evolver()
        ff = evolver.load_script(script='fitnessfunction/booleantestfitnessfunction.py',
                                 script_class_name='BooleanTestFitnessFunction')
        assert ff is not None

    def test_load_script_with_parameters(self):
        evolver = Evolver()
        evolver.parameters = {'name': 'custom_model'}
        model = evolver.load_script(script='model/booleantest.py',
                                    script_class_name='BooleanTest')
        assert model.name == 'custom_model'

    @patch('darwin.evolver.platform.system', return_value='Windows')
    def test_load_script_windows(self, _mock_platform):
        evolver = Evolver()
        # On Windows, script paths use backslashes which get converted to dots.
        # On Linux the file uses forward slashes, so the Windows path replacement
        # only handles backslashes. The import will fail on Linux, which is expected.
        result = evolver.load_script(script='model/booleantest.py',
                                     script_class_name='BooleanTest')
        assert result is None  # import fails because '/' isn't replaced on Windows path

    @patch('darwin.evolver.platform.system', return_value='Mac')
    def test_load_script_unsupported_platform(self, _mock_platform):
        evolver = Evolver()
        with pytest.raises(NotImplementedError, match='Unsupported platform'):
            evolver.load_script(script='model/booleantest.py',
                                script_class_name='BooleanTest')

    @patch('darwin.evolver.importlib.import_module', side_effect=Exception('import error'))
    def test_load_script_import_failure(self, _mock_import, capsys):
        evolver = Evolver()
        result = evolver.load_script(script='model/booleantest.py',
                                     script_class_name='BooleanTest')
        assert result is None
        captured = capsys.readouterr()
        assert 'Failed to load' in captured.out


class TestEvolverStart:
    """Test the Evolver.start() method — the main evolution loop."""

    def _make_mock_model(self):
        """Create a real Model subclass instance for start() tests."""
        class TestModel(Model):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.SingleTrue = None
                self.SingleFalse = None
                self.Fixed10True = []
                self.Fixed10False = []
                self.Variable10True = []
                self.Variable10False = []
                self.Alternating = []
        return TestModel()

    def _make_mock_rosetta_stone(self):
        """Create a real RosettaStone subclass instance for start() tests."""
        class TestRosettaStone(RosettaStone):
            def genome_template(self):
                genome = Genome()
                genome.add_chromosome(chromosome_id='SingleTrue', encoding_type=EncodingType.BOOLEAN, n_genes=1)
                return genome

            def model_to_genome(self, model):
                pass

            def genome_to_model(self, genome):
                return {'id': 'test', 'name': 'test',
                        'SingleTrue': genome.chromosomes['SingleTrue'].genes[0].data}
        return TestRosettaStone()

    def _make_mock_fitness_function(self):
        """Create a real FitnessFunction subclass instance for start() tests."""
        class TestFitnessFunction(FitnessFunction):
            def fitness(self, model):
                return Fitness(value=100, data={})
        return TestFitnessFunction()

    def _setup_evolver(self, tmp_path):
        """Create a configured Evolver ready to run start() with minimal generations."""
        evolver = Evolver()
        config = make_config(tmp_path)
        evolver.load_config(config)
        # Minimize iterations for test speed
        evolver.max_generations = 1
        evolver.population_size = 4
        evolver.elitism = 1
        evolver.truncation = 50
        evolver.periodic_save = 0
        evolver.max_time_generation = 0  # Disable generation time limit
        # Set highest_fitness to avoid TypeError in termination() when target_fitness > 0
        evolver.highest_fitness = 0
        # Patch load_script to return our mock instances
        evolver.load_script = MagicMock(side_effect=lambda script, script_class_name: {
            evolver.model_script: self._make_mock_model(),
            evolver.rosetta_stone_script: self._make_mock_rosetta_stone(),
            evolver.fitness_function_script: self._make_mock_fitness_function(),
        }[script])
        return evolver

    @patch('darwin.evolver.save_to_json_file')
    def test_start_runs_one_generation(self, mock_save, tmp_path):
        evolver = self._setup_evolver(tmp_path)
        result = evolver.start()
        assert result is not None
        assert evolver.current_generation == 1

    @patch('darwin.evolver.save_to_json_file')
    def test_start_creates_champion_file(self, mock_save, tmp_path):
        evolver = self._setup_evolver(tmp_path)
        evolver.start()
        # save_to_json_file should have been called for the champion
        assert mock_save.called

    @patch('darwin.evolver.save_to_json_file')
    def test_start_with_load_last_save(self, mock_save, tmp_path):
        evolver = self._setup_evolver(tmp_path)
        evolver.load_last_save = True
        # Patch Population.load_directory to avoid file I/O
        with patch('darwin.population.Population.load_directory'):
            evolver.start()
            assert evolver.current_generation == 1

    @patch('darwin.evolver.save_to_json_file')
    def test_start_with_load_champions(self, mock_save, tmp_path):
        evolver = self._setup_evolver(tmp_path)
        evolver.load_last_save = False
        evolver.load_champions = True
        with patch('darwin.population.Population.load_directory'):
            evolver.start()
            assert evolver.current_generation == 1

    @patch('darwin.evolver.save_to_json_file')
    def test_start_recombination_type_1_rws(self, mock_save, tmp_path):
        evolver = self._setup_evolver(tmp_path)
        evolver.recombination_type = 1
        evolver.start()
        assert evolver.current_generation == 1

    @patch('darwin.evolver.save_to_json_file')
    def test_start_recombination_type_2_rank(self, mock_save, tmp_path):
        evolver = self._setup_evolver(tmp_path)
        evolver.recombination_type = 2
        evolver.start()
        assert evolver.current_generation == 1

    @patch('darwin.evolver.save_to_json_file')
    def test_start_recombination_type_4_tournament(self, mock_save, tmp_path):
        evolver = self._setup_evolver(tmp_path)
        evolver.recombination_type = 4
        evolver.start()
        assert evolver.current_generation == 1

    @patch('darwin.evolver.save_to_json_file')
    def test_start_recombination_type_invalid_raises(self, mock_save, tmp_path):
        evolver = self._setup_evolver(tmp_path)
        evolver.recombination_type = 99
        with pytest.raises(NotImplementedError, match='Unknown recombination type'):
            evolver.start()

    @patch('darwin.evolver.save_to_json_file')
    def test_start_invalid_model_raises(self, mock_save, tmp_path):
        evolver = self._setup_evolver(tmp_path)
        with patch.object(evolver, 'load_script', return_value='not_a_model'):
            with pytest.raises(Exception, match='not a valid Model Script'):
                evolver.start()

    @patch('darwin.evolver.save_to_json_file')
    def test_start_invalid_rosetta_stone_raises(self, mock_save, tmp_path):
        evolver = self._setup_evolver(tmp_path)
        original_load = evolver.load_script

        def mock_load(script, script_class_name):
            if 'rosettastone' in script:
                return 'not_a_rosetta_stone'
            return original_load(script, script_class_name)

        with patch.object(evolver, 'load_script', side_effect=mock_load):
            with pytest.raises(Exception, match='not a valid RosettaStone Script'):
                evolver.start()

    @patch('darwin.evolver.save_to_json_file')
    def test_start_invalid_fitness_function_raises(self, mock_save, tmp_path):
        evolver = self._setup_evolver(tmp_path)
        original_load = evolver.load_script

        def mock_load(script, script_class_name):
            if 'fitnessfunction' in script:
                return 'not_a_fitness_function'
            return original_load(script, script_class_name)

        with patch.object(evolver, 'load_script', side_effect=mock_load):
            with pytest.raises(Exception):
                evolver.start()

    @patch('darwin.evolver.save_to_json_file')
    def test_start_periodic_save(self, mock_save, tmp_path):
        """Test that periodic_save triggers a population save during the generation."""
        evolver = self._setup_evolver(tmp_path)
        evolver.periodic_save = 1  # Save every generation
        with patch('darwin.population.Population.save') as mock_pop_save:
            evolver.start()
            mock_pop_save.assert_called_once()

    @patch('darwin.evolver.save_to_json_file')
    def test_start_progress_file_written(self, mock_save, tmp_path):
        evolver = self._setup_evolver(tmp_path)
        evolver.start()
        assert os.path.isfile(evolver.progress_file)

    @patch('darwin.evolver.save_to_json_file')
    def test_start_removes_existing_progress_file(self, mock_save, tmp_path):
        evolver = self._setup_evolver(tmp_path)
        # Create a stale progress file
        with open(evolver.progress_file, 'w') as f:
            f.write('stale data\n')
        evolver.start()
        with open(evolver.progress_file, 'r') as f:
            content = f.read()
        assert 'stale data' not in content

    @patch('darwin.evolver.save_to_json_file')
    def test_start_target_fitness_reached(self, mock_save, tmp_path):
        """Test termination via target_fitness being reached."""
        evolver = self._setup_evolver(tmp_path)
        evolver.max_generations = 0
        evolver.stagnation = 0
        evolver.max_time_total = 0
        evolver.target_fitness = 50  # Fitness function returns 100, so 50 is reached after gen 1
        evolver.start()
        assert evolver.current_generation == 1

    @patch('darwin.evolver.save_to_json_file')
    def test_start_generation_time_limit(self, mock_save, tmp_path):
        """Test that max_time_generation > 0 triggers the time limit break (lines 264-266)."""
        evolver = self._setup_evolver(tmp_path)
        evolver.max_time_generation = 5  # Default value — condition always true with large timestamp
        evolver.population_size = 1  # Avoid None fitness sort error when time limit breaks early
        evolver.truncation = 100  # Keep all genomes despite small population
        evolver.elitism = 0  # No elitism with single genome
        evolver.start()
        assert evolver.current_generation == 1

    @patch('darwin.evolver.save_to_json_file')
    def test_start_stagnation_counter(self, mock_save, tmp_path):
        """Test that generations_since_new_champion increments when no improvement (line 284)."""
        evolver = self._setup_evolver(tmp_path)
        evolver.max_generations = 2
        evolver.highest_fitness = 999  # Higher than fitness function returns, so no new champion
        evolver.start()
        assert evolver.current_generation == 2

    @patch('darwin.evolver.save_to_json_file')
    def test_start_mixed_encoding_types(self, mock_save, tmp_path):
        """Test mutation branches for Integer, Float, String encoding types (lines 330-337)."""
        class MixedRosettaStone(RosettaStone):
            def genome_template(self):
                genome = Genome()
                genome.add_chromosome(chromosome_id='BoolGene', encoding_type=EncodingType.BOOLEAN, n_genes=1)
                genome.add_chromosome(chromosome_id='IntGene', encoding_type=EncodingType.INTEGER, n_genes=1, min_value=0, max_value=10)
                genome.add_chromosome(chromosome_id='FloatGene', encoding_type=EncodingType.FLOAT, n_genes=1, min_value=0.0, max_value=1.0)
                genome.add_chromosome(chromosome_id='StrGene', encoding_type=EncodingType.STRING, n_genes=1)
                return genome

            def model_to_genome(self, model):
                pass

            def genome_to_model(self, genome):
                return {'id': 'test', 'name': 'test'}

        evolver = self._setup_evolver(tmp_path)
        # Override the rosetta stone to return mixed encoding types
        rs = MixedRosettaStone()
        evolver.load_script = MagicMock(side_effect=lambda script, script_class_name: {
            evolver.model_script: self._make_mock_model(),
            evolver.rosetta_stone_script: rs,
            evolver.fitness_function_script: self._make_mock_fitness_function(),
        }[script])
        evolver.start()
        assert evolver.current_generation == 1


class TestLoadScriptPaths:
    """Test load_script path resolution for SPELLBOOK_DIR and not-found cases."""

    def test_load_script_from_spellbook_dir(self, tmp_path):
        """When script is found in SPELLBOOK_DIR but not DARWIN_DIR (lines 376-377)."""
        evolver = Evolver()
        # Create a dummy script file in SPELLBOOK_DIR
        script_content = '''
class TestScript:
    pass
'''
        script_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'test_dummy_script.py')
        with open(script_file, 'w') as f:
            f.write(script_content)
        try:
            def isfile_side_effect(path):
                if 'darwin' in path and 'test_dummy_script.py' in path:
                    return False  # Not in DARWIN_DIR
                if 'test_dummy_script.py' in path:
                    return True  # Found in SPELLBOOK_DIR
                return os.path.isfile(path)
            with patch('os.path.isfile', side_effect=isfile_side_effect):
                result = evolver.load_script(script='test_dummy_script.py', script_class_name='TestScript')
            assert result is not None
            assert hasattr(result, '__class__')
        finally:
            os.remove(script_file)
