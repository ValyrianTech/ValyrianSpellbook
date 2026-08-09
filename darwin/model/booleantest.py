#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Boolean test model for Darwin."""

from model import Model


class BooleanTest(Model):
    """Boolean test model for Darwin."""
    def __init__(self, name=None):
        super(BooleanTest, self).__init__(name=name)
        self.SingleTrue = None
        self.SingleFalse = None
        self.Fixed10True = None
        self.Fixed10False = None
        self.Variable10True = None
        self.Variable10False = None
        self.Alternating = None
