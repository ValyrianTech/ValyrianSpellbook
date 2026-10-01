#!/usr/bin/env python
"""Boolean test model for Darwin."""

from model import Model


class BooleanTest(Model):
    """Boolean test model for Darwin."""
    def __init__(self, name=None):
        super().__init__(name=name)
        self.SingleTrue = None
        self.SingleFalse = None
        self.Fixed10True = None
        self.Fixed10False = None
        self.Variable10True = None
        self.Variable10False = None
        self.Alternating = None
