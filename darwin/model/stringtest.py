#!/usr/bin/env python
"""String test model for the Darwin evolutionary framework."""
from model import Model


class StringTest(Model):
    """String test model for Darwin."""
    def __init__(self, name=None):
        super().__init__(name=name)
        self.HelloWorld = None
        self.Alphabet = None
        self.Gattaca = None
