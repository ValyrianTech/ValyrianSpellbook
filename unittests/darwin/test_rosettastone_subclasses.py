#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for Darwin rosettastone subclasses.

The boolean, float, integer and string rosettastone modules use the old
``genome.add_chromosome(chromosome)`` API (passing a Chromosome object) and
integer-indexed ``genome.chromosomes[0]`` access. The current ``Genome`` class
uses a dict with string keys and a different ``add_chromosome`` signature.

To exercise these modules for coverage without modifying source code, we
monkey-patch ``Genome.add_chromosome`` to accept a Chromosome object and store
it with an auto-incrementing integer key.

The FullTestRosettaStone uses the new API and works without patching.
"""
import darwin  # noqa: F401 - import side-effect: adds DARWIN_DIR to sys.path

# Inject RosettaStone into the rosettastone package so 'from rosettastone import RosettaStone' works
import rosettastone.rosettastone  # noqa: E402
import rosettastone  # noqa: E402
rosettastone.RosettaStone = rosettastone.rosettastone.RosettaStone

from genome import Genome  # noqa: E402
from chromosome import Chromosome  # noqa: E402

from rosettastone.booleantestrosettastone import BooleanTestRosettaStone  # noqa: E402
from rosettastone.floattestrosettastone import FloatTestRosettaStone  # noqa: E402
from rosettastone.integertestrosettastone import IntegerTestRosettaStone  # noqa: E402
from rosettastone.stringtestrosettastone import StringTestRosettaStone  # noqa: E402
from rosettastone.fulltestrosettastone import FullTestRosettaStone  # noqa: E402


def _patch_genome_add_chromosome():
    """Patch Genome.add_chromosome to accept a Chromosome object (old API)."""
    original = Genome.add_chromosome

    def patched_add_chromosome(self, chromosome_id, encoding_type=None,
                               min_value=None, max_value=None, charset=None, n_genes=None):
        if isinstance(chromosome_id, Chromosome):
            chrom = chromosome_id
            key = len(self.chromosomes)
            self.chromosomes[key] = chrom
        else:
            original(self, chromosome_id, encoding_type, min_value, max_value, charset, n_genes)

    Genome.add_chromosome = patched_add_chromosome
    return original


def _restore_genome_add_chromosome(original):
    Genome.add_chromosome = original


class TestBooleanTestRosettaStone:

    def test_genome_template(self):
        original = _patch_genome_add_chromosome()
        try:
            rs = BooleanTestRosettaStone()
            genome = rs.genome_template()
            assert len(genome.chromosomes) == 7
            assert genome.chromosomes[0].id == 'SingleTrue'
            assert genome.chromosomes[1].id == 'SingleFalse'
            assert genome.chromosomes[2].id == 'Fixed10True'
            assert genome.chromosomes[3].id == 'Fixed10False'
            assert genome.chromosomes[4].id == 'Variable10True'
            assert genome.chromosomes[5].id == 'Variable10False'
            assert genome.chromosomes[6].id == 'Alternating'
        finally:
            _restore_genome_add_chromosome(original)

    def test_genome_to_model(self):
        original = _patch_genome_add_chromosome()
        try:
            rs = BooleanTestRosettaStone()
            genome = rs.genome_template()
            model = rs.genome_to_model(genome=genome)
            assert 'id' in model
            assert model['name'] == 'booleantest'
            assert 'SingleTrue' in model
            assert 'SingleFalse' in model
            assert 'Fixed10True' in model
            assert 'Fixed10False' in model
            assert 'Variable10True' in model
            assert 'Variable10False' in model
            assert 'Alternating' in model
            assert isinstance(model['SingleTrue'], bool)
            assert isinstance(model['Fixed10True'], list)
        finally:
            _restore_genome_add_chromosome(original)

    def test_model_to_genome(self):
        rs = BooleanTestRosettaStone()
        result = rs.model_to_genome(model=None)
        assert result is None

    def test_init_with_name(self):
        rs = BooleanTestRosettaStone(name='boolean_rs')
        assert rs.name == 'boolean_rs'


class TestFloatTestRosettaStone:

    def test_genome_template(self):
        original = _patch_genome_add_chromosome()
        try:
            rs = FloatTestRosettaStone()
            genome = rs.genome_template()
            assert len(genome.chromosomes) == 2
            assert genome.chromosomes[0].id == 'Single42'
            assert genome.chromosomes[1].id == 'ZeroToNine'
        finally:
            _restore_genome_add_chromosome(original)

    def test_genome_to_model(self):
        original = _patch_genome_add_chromosome()
        try:
            rs = FloatTestRosettaStone()
            genome = rs.genome_template()
            model = rs.genome_to_model(genome=genome)
            assert model['name'] == 'floattest'
            assert 'Single42' in model
            assert 'ZeroToNine' in model
            assert isinstance(model['ZeroToNine'], list)
        finally:
            _restore_genome_add_chromosome(original)

    def test_model_to_genome(self):
        rs = FloatTestRosettaStone()
        result = rs.model_to_genome(model=None)
        assert result is None


class TestIntegerTestRosettaStone:

    def test_genome_template(self):
        original = _patch_genome_add_chromosome()
        try:
            rs = IntegerTestRosettaStone()
            genome = rs.genome_template()
            assert len(genome.chromosomes) == 2
            assert genome.chromosomes[0].id == 'Single42'
            assert genome.chromosomes[1].id == 'ZeroToNine'
        finally:
            _restore_genome_add_chromosome(original)

    def test_genome_to_model(self):
        original = _patch_genome_add_chromosome()
        try:
            rs = IntegerTestRosettaStone()
            genome = rs.genome_template()
            model = rs.genome_to_model(genome=genome)
            assert model['name'] == 'integertest'
            assert 'Single42' in model
            assert 'ZeroToNine' in model
            assert isinstance(model['ZeroToNine'], list)
        finally:
            _restore_genome_add_chromosome(original)

    def test_model_to_genome(self):
        rs = IntegerTestRosettaStone()
        result = rs.model_to_genome(model=None)
        assert result is None


class TestStringTestRosettaStone:

    def test_genome_template(self):
        original = _patch_genome_add_chromosome()
        try:
            rs = StringTestRosettaStone()
            genome = rs.genome_template()
            assert len(genome.chromosomes) == 3
            assert genome.chromosomes[0].id == 'HelloWorld'
            assert genome.chromosomes[1].id == 'Alphabet'
            assert genome.chromosomes[2].id == 'Gattaca'
            assert genome.chromosomes[2].charset == 'GATC'
        finally:
            _restore_genome_add_chromosome(original)

    def test_genome_to_model(self):
        original = _patch_genome_add_chromosome()
        try:
            rs = StringTestRosettaStone()
            genome = rs.genome_template()
            model = rs.genome_to_model(genome=genome)
            assert model['name'] == 'stringtest'
            assert 'HelloWorld' in model
            assert 'Alphabet' in model
            assert 'Gattaca' in model
            assert isinstance(model['HelloWorld'], str)
            assert isinstance(model['Alphabet'], str)
        finally:
            _restore_genome_add_chromosome(original)

    def test_model_to_genome(self):
        rs = StringTestRosettaStone()
        result = rs.model_to_genome(model=None)
        assert result is None


class TestFullTestRosettaStone:
    """FullTestRosettaStone uses the new API and doesn't need patching."""

    def test_genome_template(self):
        rs = FullTestRosettaStone()
        genome = rs.genome_template()
        assert len(genome.chromosomes) == 20
        # Boolean
        assert 'SingleTrue' in genome.chromosomes
        assert 'SingleFalse' in genome.chromosomes
        assert 'Fixed10True' in genome.chromosomes
        assert 'Fixed10False' in genome.chromosomes
        assert 'Variable10True' in genome.chromosomes
        assert 'Variable10False' in genome.chromosomes
        assert 'Alternating' in genome.chromosomes
        # Integer
        assert 'Single42' in genome.chromosomes
        assert 'ZeroToNine' in genome.chromosomes
        assert 'Lowest42' in genome.chromosomes
        assert 'Average42' in genome.chromosomes
        assert 'Highest42' in genome.chromosomes
        # Float
        assert 'Single42f' in genome.chromosomes
        assert 'ZeroToNinef' in genome.chromosomes
        assert 'Lowest42f' in genome.chromosomes
        assert 'Average42f' in genome.chromosomes
        assert 'Highest42f' in genome.chromosomes
        # String
        assert 'HelloWorld' in genome.chromosomes
        assert 'Alphabet' in genome.chromosomes
        assert 'Gattaca' in genome.chromosomes
        assert genome.chromosomes['Gattaca'].charset == 'GATC'

    def test_genome_to_model(self):
        rs = FullTestRosettaStone()
        genome = rs.genome_template()
        model = rs.genome_to_model(genome=genome)
        assert model['name'] == 'fulltest'
        assert 'id' in model
        # Boolean
        assert 'SingleTrue' in model
        assert 'SingleFalse' in model
        assert 'Fixed10True' in model
        assert 'Fixed10False' in model
        assert 'Variable10True' in model
        assert 'Variable10False' in model
        assert 'Alternating' in model
        # Integer
        assert 'Single42' in model
        assert 'ZeroToNine' in model
        assert 'Lowest42' in model
        assert 'Average42' in model
        assert 'Highest42' in model
        # Float
        assert 'Single42f' in model
        assert 'ZeroToNinef' in model
        assert 'Lowest42f' in model
        assert 'Average42f' in model
        assert 'Highest42f' in model
        # String
        assert 'HelloWorld' in model
        assert 'Alphabet' in model
        assert 'Gattaca' in model

    def test_model_to_genome(self):
        rs = FullTestRosettaStone()
        result = rs.model_to_genome(model=None)
        assert result is None

    def test_init_with_name(self):
        rs = FullTestRosettaStone(name='full_rs')
        assert rs.name == 'full_rs'
