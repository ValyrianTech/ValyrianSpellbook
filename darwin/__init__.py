#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

PROGRAM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
# sys.path.insert(0, PROGRAM_DIR)

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

DARWIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, DARWIN_DIR)
