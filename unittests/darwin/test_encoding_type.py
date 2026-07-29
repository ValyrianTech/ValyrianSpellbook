#!/usr/bin/env python
# -*- coding: utf-8 -*-
from darwin.encodingtype import EncodingType


class TestEncodingType:

    def test_boolean_constant(self):
        assert EncodingType.BOOLEAN == 'Boolean'

    def test_integer_constant(self):
        assert EncodingType.INTEGER == 'Integer'

    def test_float_constant(self):
        assert EncodingType.FLOAT == 'Float'

    def test_string_constant(self):
        assert EncodingType.STRING == 'String'

    def test_all_constants_distinct(self):
        values = [EncodingType.BOOLEAN, EncodingType.INTEGER,
                  EncodingType.FLOAT, EncodingType.STRING]
        assert len(set(values)) == 4
