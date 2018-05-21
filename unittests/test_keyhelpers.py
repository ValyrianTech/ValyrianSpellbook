#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytest
import mock
from helpers.privatekeyhelpers import PrivateKey

private_key_decimal = 68578345631418883606849416554834375778771641053887312743419655680624313714076
private_key_base64 = 'l5331jNEv8AMOB8kBfsgLBzKntAFYpfcvalHvzVfRZw='

private_key_hex_compressed = '979DF7D63344BFC00C381F2405FB202C1CCA9ED0056297DCBDA947BF355F459C01'
private_key_wif_compressed = 'L2JSANyWZK6US9HPhW5eep3cGP5J36aBJaw9qqwmrWAnbh9hHBh6'
address_compressed = '1AC8nA8g7tZoEUreZ47L9SPGLacsYDQQ3C'
public_key_compressed = '023782620F3397D7AAC738DD7AAD7C4D769C6DA8571DC0E1C4EE60A61883E7E5C5'

private_key_hex_uncompressed = '979DF7D63344BFC00C381F2405FB202C1CCA9ED0056297DCBDA947BF355F459C'
private_key_wif_uncompressed = '5Jy4SEb6nqWLMeg4L9QFsi23Z2q6fzT6WMq4pKLfFqkTC389CrG'
address_uncompressed = '1GnvtEY28hzbuEhrWjUNA2aAX5FtRKChHR'
public_key_uncompressed = '043782620F3397D7AAC738DD7AAD7C4D769C6DA8571DC0E1C4EE60A61883E7E5C56525367FB5BE8EDF81290E150F840446A80754EDD61A59A99BB1B271931C1EFA'


class TestPrivateKey(object):
    def test_given_no_parameters_when_initializing_private_key_then_exception_is_raised(self):
        with pytest.raises(Exception):
            PrivateKey()

    def test_given_private_key_in_decimal_format_when_initializing_private_key_then_private_key_object_is_created(self):
        private_key = PrivateKey(private_key=private_key_decimal)
        assert isinstance(private_key, PrivateKey)

    def test_given_private_key_in_wif_compressed_format_when_initializing_private_key_then_private_key_object_is_created(self):
        private_key = PrivateKey(private_key=private_key_wif_compressed)
        assert isinstance(private_key, PrivateKey)

    def test_given_private_key_in_wif_uncompressed_format_when_initializing_private_key_then_private_key_object_is_created(self):
        private_key = PrivateKey(private_key=private_key_wif_uncompressed)
        assert isinstance(private_key, PrivateKey)

    def test_given_private_key_in_hexadecimal_uncompressed_format_when_initializing_private_key_then_private_key_object_is_created(self):
        private_key = PrivateKey(private_key=private_key_hex_uncompressed)
        assert isinstance(private_key, PrivateKey)

    def test_given_private_key_in_hexadecimal_compressed_format_when_initializing_private_key_then_private_key_object_is_created(self):
        private_key = PrivateKey(private_key=private_key_hex_compressed)
        assert isinstance(private_key, PrivateKey)

    def test_given_private_key_in_base64_format_when_initializing_private_key_then_private_key_object_is_created(self):
        private_key = PrivateKey(private_key=private_key_base64)
        assert isinstance(private_key, PrivateKey)

    def test_given_invalid_private_key_in_wif_compressed_format_when_initializing_private_key_then_exception_is_raised(self):
        with pytest.raises(Exception):
            PrivateKey(private_key='foobar')


    def test_given_private_key_in_decimal_format_when_initializing_private_key_then_other_formats_are_calculated_correctly(self):
        private_key = PrivateKey(private_key=private_key_decimal)
        assert private_key.decimal == private_key_decimal
        assert private_key.wif == private_key_wif_uncompressed
        assert private_key.wifc == private_key_wif_compressed
        assert private_key.hex == private_key_hex_uncompressed
        assert private_key.hexc == private_key_hex_compressed

    def test_given_private_key_in_wif_compressed_format_when_initializing_private_key_then_other_formats_are_calculated_correctly(self):
        private_key = PrivateKey(private_key=private_key_wif_compressed)
        assert private_key.decimal == private_key_decimal
        assert private_key.wif == private_key_wif_uncompressed
        assert private_key.wifc == private_key_wif_compressed
        assert private_key.hex == private_key_hex_uncompressed
        assert private_key.hexc == private_key_hex_compressed

    def test_given_private_key_in_wif_uncompressed_format_when_initializing_private_key_then_other_formats_are_calculated_correctly(self):
        private_key = PrivateKey(private_key=private_key_wif_uncompressed)
        assert private_key.decimal == private_key_decimal
        assert private_key.wif == private_key_wif_uncompressed
        assert private_key.wifc == private_key_wif_compressed
        assert private_key.hex == private_key_hex_uncompressed
        assert private_key.hexc == private_key_hex_compressed

    def test_given_private_key_in_hexadecimal_compressed_format_when_initializing_private_key_then_other_formats_are_calculated_correctly(self):
        private_key = PrivateKey(private_key=private_key_hex_compressed)
        assert private_key.decimal == private_key_decimal
        assert private_key.wif == private_key_wif_uncompressed
        assert private_key.wifc == private_key_wif_compressed
        assert private_key.hex == private_key_hex_uncompressed
        assert private_key.hexc == private_key_hex_compressed

    def test_given_private_key_in_hexadecimal_uncompressed_format_when_initializing_private_key_then_other_formats_are_calculated_correctly(self):
        private_key = PrivateKey(private_key=private_key_hex_uncompressed)
        assert private_key.decimal == private_key_decimal
        assert private_key.wif == private_key_wif_uncompressed
        assert private_key.wifc == private_key_wif_compressed
        assert private_key.hex == private_key_hex_uncompressed
        assert private_key.hexc == private_key_hex_compressed
