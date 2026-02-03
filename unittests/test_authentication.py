#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock

import authentication

NONCE = 1


class TestAuthentication(object):
    headers = None
    data = None

    def setup_method(self):
        global NONCE

        authentication.load_from_json_file = mock.MagicMock(return_value={'foo': {'secret': 'bar1'}})
        self.data = {'test': 'test'}
        NONCE = NONCE + 1

        self.headers = {'API_Key': 'foo',
                        'API_Sign': authentication.signature(self.data, NONCE, 'bar1'),
                        'API_Nonce': NONCE}

    def test_check_authentication_with_valid_headers_and_data(self):
        assert authentication.check_authentication(self.headers, self.data) == authentication.AuthenticationStatus.OK

    def test_check_authentication_with_valid_headers_and_data_but_the_same_nonce(self):
        self.headers['API_Sign'] = authentication.signature(self.data, NONCE-1, 'bar1')
        self.headers['API_Nonce'] = NONCE - 1
        assert authentication.check_authentication(self.headers, self.data) == authentication.AuthenticationStatus.INVALID_NONCE

    def test_check_authentication_with_valid_headers_and_data_and_a_nonce_that_is_higher_than_the_previous_request(self):
        assert authentication.check_authentication(self.headers, self.data) == authentication.AuthenticationStatus.OK

    def test_check_authentication_without_api_key_header(self):
        del self.headers['API_Key']
        assert authentication.check_authentication(self.headers, self.data) == authentication.AuthenticationStatus.NO_API_KEY

    def test_check_authentication_without_api_sign_header(self):
        del self.headers['API_Sign']
        assert authentication.check_authentication(self.headers, self.data) == authentication.AuthenticationStatus.NO_SIGNATURE

    def test_check_authentication_without_api_nonce_header(self):
        del self.headers['API_Nonce']
        assert authentication.check_authentication(self.headers, self.data) == authentication.AuthenticationStatus.NO_NONCE

    def test_check_authentication_with_wrong_secret(self):
        self.headers['API_Sign'] = authentication.signature(self.data, NONCE, 'ABCD')
        assert authentication.check_authentication(self.headers, self.data) == authentication.AuthenticationStatus.INVALID_SIGNATURE

    def test_check_authentication_with_api_key(self):
        self.headers['API_Key'] = 'bar'
        assert authentication.check_authentication(self.headers, self.data) == authentication.AuthenticationStatus.INVALID_API_KEY

    def test_check_authentication_with_changed_data(self):
        self.data = {'something': 'else'}
        assert authentication.check_authentication(self.headers, self.data) == authentication.AuthenticationStatus.INVALID_SIGNATURE

    def test_signature_with_secret_that_is_not_a_multiple_of_4_characters(self):
        with pytest.raises(Exception) as ex:
            authentication.signature(self.data, NONCE, 'a')
        assert 'The secret must be a string with a length of a multiple of 4!' in str(ex.value)

    def test_check_authentication_with_invalid_json_file(self):
        authentication.load_from_json_file = mock.MagicMock(return_value=None)
        assert authentication.check_authentication(self.headers, self.data) == authentication.AuthenticationStatus.INVALID_JSON_FILE

    def test_check_authentication_with_invalid_nonce_format(self):
        self.headers['API_Nonce'] = 'not_a_number'
        assert authentication.check_authentication(self.headers, self.data) == authentication.AuthenticationStatus.INVALID_NONCE


class TestAuthenticationStatus(object):
    """Tests for AuthenticationStatus constants"""

    def test_authentication_status_constants(self):
        assert authentication.AuthenticationStatus.OK == 'OK'
        assert authentication.AuthenticationStatus.INVALID_API_KEY == 'Invalid API key'
        assert authentication.AuthenticationStatus.NO_API_KEY == 'No API key supplied'
        assert authentication.AuthenticationStatus.INVALID_SIGNATURE == 'Invalid signature'
        assert authentication.AuthenticationStatus.NO_SIGNATURE == 'No signature supplied'
        assert authentication.AuthenticationStatus.INVALID_JSON_FILE == 'Invalid json file'
        assert authentication.AuthenticationStatus.NO_NONCE == 'No nonce supplied'
        assert authentication.AuthenticationStatus.INVALID_NONCE == 'Invalid nonce'


class TestHashMessage(object):
    """Tests for hash_message function"""

    def test_hash_message(self):
        data = {'key': 'value'}
        nonce = 12345
        result = authentication.hash_message(data, nonce)
        assert isinstance(result, bytes)
        assert len(result) == 64  # SHA512 produces 64 bytes

    def test_hash_message_different_nonces(self):
        data = {'key': 'value'}
        result1 = authentication.hash_message(data, 1)
        result2 = authentication.hash_message(data, 2)
        assert result1 != result2

    def test_hash_message_different_data(self):
        nonce = 12345
        result1 = authentication.hash_message({'key': 'value1'}, nonce)
        result2 = authentication.hash_message({'key': 'value2'}, nonce)
        assert result1 != result2


class TestSignature(object):
    """Tests for signature function"""

    def test_signature_valid_secret(self):
        data = {'key': 'value'}
        nonce = 12345
        secret = 'ABCD'  # Length 4, multiple of 4
        result = authentication.signature(data, nonce, secret)
        assert isinstance(result, str)

    def test_signature_deterministic(self):
        data = {'key': 'value'}
        nonce = 12345
        secret = 'ABCD'
        result1 = authentication.signature(data, nonce, secret)
        result2 = authentication.signature(data, nonce, secret)
        assert result1 == result2
