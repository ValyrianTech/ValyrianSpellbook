#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Integer test model for the Darwin evolutionary framework."""
from model import Model


class IntegerTest(Model):
    """Integer test model for Darwin."""
    def __init__(self, name=None):
        """  init  ."""
        super(IntegerTest, self).__init__(name=name)
        self.Single42 = None
        self.ZeroToNine = None
