#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest.mock import patch

from darwin.genome import Genome
from darwin.encodingtype import EncodingType
from darwin.recombination import recombine


class TestRecombine:

    def _make_genome(self, chrom_data):
        genome = Genome()
        for chrom_id, data in chrom_data.items():
            genome.add_chromosome(chromosome_id=chrom_id, encoding_type=EncodingType.BOOLEAN, n_genes=1)
            genome.chromosomes[chrom_id].genes[0].data = data
        return genome

    @patch('darwin.recombination.randint', return_value=0)
    def test_recombine_takes_parent_a(self, _mock):
        parent_a = self._make_genome({'c1': True, 'c2': False})
        parent_b = self._make_genome({'c1': False, 'c2': True})
        offspring = recombine(parent_a, parent_b)
        assert offspring.chromosomes['c1'].genes[0].data is True
        assert offspring.chromosomes['c2'].genes[0].data is False

    @patch('darwin.recombination.randint', return_value=1)
    def test_recombine_takes_parent_b(self, _mock):
        parent_a = self._make_genome({'c1': True, 'c2': False})
        parent_b = self._make_genome({'c1': False, 'c2': True})
        offspring = recombine(parent_a, parent_b)
        assert offspring.chromosomes['c1'].genes[0].data is False
        assert offspring.chromosomes['c2'].genes[0].data is True

    @patch('darwin.recombination.randint', side_effect=[0, 1])
    def test_recombine_mixed(self, _mock):
        parent_a = self._make_genome({'c1': True, 'c2': False})
        parent_b = self._make_genome({'c1': False, 'c2': True})
        offspring = recombine(parent_a, parent_b)
        assert offspring.chromosomes['c1'].genes[0].data is True
        assert offspring.chromosomes['c2'].genes[0].data is True

    def test_recombine_creates_new_genome(self):
        parent_a = self._make_genome({'c1': True})
        parent_b = self._make_genome({'c1': False})
        offspring = recombine(parent_a, parent_b)
        assert offspring is not parent_a
        assert offspring is not parent_b
        assert isinstance(offspring, Genome)

    def test_recombine_deep_copies(self):
        parent_a = self._make_genome({'c1': True})
        parent_b = self._make_genome({'c1': False})
        offspring = recombine(parent_a, parent_b)
        offspring.chromosomes['c1'].genes[0].data = False
        assert parent_a.chromosomes['c1'].genes[0].data is True
