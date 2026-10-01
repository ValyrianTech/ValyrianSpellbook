#!/usr/bin/env python
"""Integer test model for the Darwin evolutionary framework."""
from model import Model


class IntegerTest(Model):
    """Integer test model for Darwin."""
    def __init__(self, name=None):
        super().__init__(name=name)
        self.Single42 = None
        self.ZeroToNine = None
