#!/usr/bin/env python
# -*- coding: utf-8 -*-
from model import Model


class FullTest(Model):
    def __init__(self, name=None):
        super(FullTest, self).__init__(name=name)
        self.SingleTrue = None
        self.SingleFalse = None
        self.Fixed10True = None
        self.Fixed10False = None
        self.Variable10True = None
        self.Variable10False = None
        self.Alternating = None

        self.Single42 = None
        self.ZeroToNine = None
        self.Lowest42 = None
        self.Average42 = None
        self.Highest42 = None

        self.Single42f = None
        self.ZeroToNinef = None
        self.Lowest42f = None
        self.Average42f = None
        self.Highest42f = None

        self.HelloWorld = None
        self.Alphabet = None
        self.Gattaca = None
