#!/usr/bin/env python
# -*- coding: utf-8 -*-
from model import Model


class FloatTest(Model):
    def __init__(self, name=None):
        super(FloatTest, self).__init__(name=name)
        self.Single42 = None
        self.ZeroToNine = None
