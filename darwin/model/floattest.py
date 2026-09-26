#!/usr/bin/env python
"""Float test model for Darwin."""

from model import Model


class FloatTest(Model):
    """Float test model for Darwin."""
    def __init__(self, name=None):
        super().__init__(name=name)
        self.Single42 = None
        self.ZeroToNine = None
