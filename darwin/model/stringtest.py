#!/usr/bin/env python
# -*- coding: utf-8 -*-
from model import Model


class StringTest(Model):
    """String test model for Darwin."""
    def __init__(self, name=None):
        """  init  ."""
        super(StringTest, self).__init__(name=name)
        self.HelloWorld = None
        self.Alphabet = None
        self.Gattaca = None
