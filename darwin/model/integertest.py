#!/usr/bin/env python
# -*- coding: utf-8 -*-
from model import Model


class IntegerTest(Model):
    def __init__(self, name=None):
        super(IntegerTest, self).__init__(name=name)
        self.Single42 = None
        self.ZeroToNine = None
