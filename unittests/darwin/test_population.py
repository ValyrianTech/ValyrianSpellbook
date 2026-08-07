#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from unittest.mock import patch

from darwin.population import Population
from darwin.genome import Genome
from darwin.encodingtype import EncodingType
from darwin.gene import BooleanGene, IntegerGene, FloatGene, StringGene


class TestPopulationInit:

    def test_init(self):
        pop = Population()
        assert pop.genomes == []


class TestAddGenome:

    def test_add_genome(self):
        pop = Population()
        genome = Genome()
        pop.add_genome(genome)
        assert len(pop.genomes) == 1
        assert pop.genomes[0] is genome

    def test_add_multiple_genomes(self):
        pop = Population()
        for _ in range(3):
            pop.add_genome(Genome())
        assert len(pop.genomes) == 3


class TestSave:

    @patch('darwin.population.shutil.rmtree')
    @patch('darwin.population.time.sleep')
    @patch('darwin.population.save_to_json_file')
    def test_save(self, mock_save, mock_sleep, mock_rmtree):
        pop = Population()
        genome = Genome()
        genome.add_chromosome(chromosome_id='test', encoding_type=EncodingType.BOOLEAN, n_genes=1)
        pop.add_genome(genome)
        pop.save(directory='/tmp/test_darwin_save')
        mock_rmtree.assert_called_once_with('/tmp/test_darwin_save')
        mock_sleep.assert_called_once_with(1)
        assert mock_save.call_count == 1


class TestLoadGenome:

    def test_load_genome_boolean(self):
        pop = Population()
        genome_data = {
            'chromosomes': {
                'test': {
                    'id': 'test',
                    'n_genes': 2,
                    'genes': [True, False],
                    'encoding_type': 'Boolean',
                    'min': None,
                    'max': None,
                    'charset': None
                }
            },
            'fitness': 42,
            'id': 'test_id'
        }
        pop.load_genome(genome_data)
        assert len(pop.genomes) == 1
        genome = pop.genomes[0]
        assert genome.chromosomes['test'].genes[0].data is True
        assert genome.chromosomes['test'].genes[1].data is False
        assert isinstance(genome.chromosomes['test'].genes[0], BooleanGene)

    def test_load_genome_integer(self):
        pop = Population()
        genome_data = {
            'chromosomes': {
                'test': {
                    'id': 'test',
                    'n_genes': 2,
                    'genes': [10, 20],
                    'encoding_type': 'Integer',
                    'min': 0,
                    'max': 100,
                    'charset': None
                }
            },
            'fitness': None,
            'id': 'test_id'
        }
        pop.load_genome(genome_data)
        genome = pop.genomes[0]
        assert genome.chromosomes['test'].genes[0].data == 10
        assert genome.chromosomes['test'].genes[1].data == 20
        assert isinstance(genome.chromosomes['test'].genes[0], IntegerGene)
        assert genome.chromosomes['test'].genes[0].min == 0
        assert genome.chromosomes['test'].genes[0].max == 100

    def test_load_genome_float(self):
        pop = Population()
        genome_data = {
            'chromosomes': {
                'test': {
                    'id': 'test',
                    'n_genes': 2,
                    'genes': [10.5, 20.5],
                    'encoding_type': 'Float',
                    'min': 0.0,
                    'max': 100.0,
                    'charset': None
                }
            },
            'fitness': None,
            'id': 'test_id'
        }
        pop.load_genome(genome_data)
        genome = pop.genomes[0]
        assert genome.chromosomes['test'].genes[0].data == 10.5
        assert isinstance(genome.chromosomes['test'].genes[0], FloatGene)
        assert genome.chromosomes['test'].genes[0].min == 0.0
        assert genome.chromosomes['test'].genes[0].max == 100.0

    def test_load_genome_string(self):
        pop = Population()
        genome_data = {
            'chromosomes': {
                'test': {
                    'id': 'test',
                    'n_genes': 2,
                    'genes': ['hello', 'world'],
                    'encoding_type': 'String',
                    'min': None,
                    'max': None,
                    'charset': 'abc'
                }
            },
            'fitness': None,
            'id': 'test_id'
        }
        pop.load_genome(genome_data)
        genome = pop.genomes[0]
        assert genome.chromosomes['test'].genes[0].data == 'hello'
        assert isinstance(genome.chromosomes['test'].genes[0], StringGene)
        assert genome.chromosomes['test'].genes[0].charset == 'abc'

    def test_load_genome_unknown_encoding_raises(self):
        pop = Population()
        genome_data = {
            'chromosomes': {
                'test': {
                    'id': 'test',
                    'n_genes': 1,
                    'genes': [42],
                    'encoding_type': 'Unknown',
                    'min': None,
                    'max': None,
                    'charset': None
                }
            },
            'fitness': None,
            'id': 'test_id'
        }
        with pytest.raises(NotImplementedError, match='Unknown Encoding type'):
            pop.load_genome(genome_data)

    def test_load_genome_multiple_chromosomes(self):
        pop = Population()
        genome_data = {
            'chromosomes': {
                'c1': {
                    'id': 'c1',
                    'n_genes': 1,
                    'genes': [True],
                    'encoding_type': 'Boolean',
                    'min': None,
                    'max': None,
                    'charset': None
                },
                'c2': {
                    'id': 'c2',
                    'n_genes': 1,
                    'genes': [42],
                    'encoding_type': 'Integer',
                    'min': 0,
                    'max': 100,
                    'charset': None
                }
            },
            'fitness': None,
            'id': 'test_id'
        }
        pop.load_genome(genome_data)
        genome = pop.genomes[0]
        assert len(genome.chromosomes) == 2
        assert genome.chromosomes['c1'].genes[0].data is True
        assert genome.chromosomes['c2'].genes[0].data == 42


class TestLoadDirectory:

    @patch('darwin.population.load_from_json_file')
    @patch('darwin.population.glob.glob')
    def test_load_directory(self, mock_glob, mock_load):
        mock_glob.return_value = ['/tmp/test1.json', '/tmp/test2.json']
        mock_load.return_value = {
            'chromosomes': {
                'test': {
                    'id': 'test',
                    'n_genes': 1,
                    'genes': [True],
                    'encoding_type': 'Boolean',
                    'min': None,
                    'max': None,
                    'charset': None
                }
            },
            'fitness': None,
            'id': 'test_id'
        }
        pop = Population()
        pop.load_directory(directory='/tmp/test_darwin')
        assert len(pop.genomes) == 2

    @patch('darwin.population.glob.glob', return_value=[])
    def test_load_directory_empty(self, _mock):
        pop = Population()
        pop.load_directory(directory='/tmp/empty_dir')
        assert len(pop.genomes) == 0
