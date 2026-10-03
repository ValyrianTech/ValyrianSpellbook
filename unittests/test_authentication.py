#!/usr/bin/env python
import json
import os
import threading
from unittest import mock

import pytest

import authentication

NONCE = 1
_REAL_SAVE_LAST_NONCES = authentication.save_last_nonces


class TestAuthentication:
    headers = None
    data = None

    def setup_method(self):
        global NONCE

        authentication.load_from_json_file = mock.MagicMock(return_value={'foo': {'secret': 'bar1'}})
        authentication.save_last_nonces = mock.MagicMock()
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


class TestAuthenticationStatus:
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


class TestHashMessage:
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


class TestSignature:
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


class TestInitializeApiKeysFile:
    """Tests for initialize_api_keys_file function"""

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('configparser.ConfigParser')
    @mock.patch('authentication.save_to_json_file')
    @mock.patch('os.makedirs')
    @mock.patch('os.path.isdir', return_value=False)
    def test_initialize_api_keys_file_dir_not_exists(self, mock_isdir, mock_makedirs, mock_save, mock_config_cls, mock_open):
        authentication.initialize_api_keys_file()
        mock_isdir.assert_called_once_with('json/private/')
        mock_makedirs.assert_called_once_with('json/private')
        mock_save.assert_called_once()
        mock_config_cls.assert_called_once()

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('configparser.ConfigParser')
    @mock.patch('authentication.save_to_json_file')
    @mock.patch('os.makedirs')
    @mock.patch('os.path.isdir', return_value=True)
    def test_initialize_api_keys_file_dir_exists(self, mock_isdir, mock_makedirs, mock_save, mock_config_cls, mock_open):
        authentication.initialize_api_keys_file()
        mock_isdir.assert_called_once_with('json/private/')
        mock_makedirs.assert_not_called()
        mock_save.assert_called_once()
        mock_config_cls.assert_called_once()

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('configparser.ConfigParser')
    @mock.patch('authentication.save_to_json_file')
    @mock.patch('os.path.isdir', return_value=True)
    def test_initialize_api_keys_file_generates_valid_keys(self, mock_isdir, mock_save, mock_config_cls, mock_open):
        authentication.initialize_api_keys_file()
        saved_data = mock_save.call_args[0][1]
        assert len(saved_data) == 1
        api_key = next(iter(saved_data.keys()))
        assert len(api_key) == 32
        assert all(char in authentication._API_KEY_ALPHABET for char in api_key)
        assert 'secret' in saved_data[api_key]
        assert len(saved_data[api_key]['secret']) == 32
        assert all(char in authentication._API_KEY_ALPHABET for char in saved_data[api_key]['secret'])
        assert saved_data[api_key]['permissions'] == 'all'


class TestLastNonces:
    """Tests for load_last_nonces and save_last_nonces helpers."""

    def test_load_last_nonces_updates_last_nonces(self):
        authentication.LAST_NONCES.clear()
        authentication.load_from_json_file = mock.MagicMock(return_value={'foo': 42})
        authentication.load_last_nonces()
        assert authentication.LAST_NONCES == {'foo': 42}

    def test_load_last_nonces_none_leaves_last_nonces_unchanged(self):
        authentication.LAST_NONCES.clear()
        authentication.load_from_json_file = mock.MagicMock(return_value=None)
        authentication.load_last_nonces()
        assert authentication.LAST_NONCES == {}

    def test_load_last_nonces_oserror_leaves_last_nonces_unchanged(self):
        authentication.LAST_NONCES.clear()
        authentication.LAST_NONCES['existing'] = 5
        authentication.load_from_json_file = mock.MagicMock(side_effect=OSError('boom'))
        with mock.patch.object(authentication, 'LOG') as mock_log:
            authentication.load_last_nonces()
        assert authentication.LAST_NONCES == {'existing': 5}
        mock_log.error.assert_called_once()

    def test_load_last_nonces_file_not_found_does_not_raise(self):
        authentication.LAST_NONCES.clear()
        authentication.LAST_NONCES['existing'] = 5
        authentication.load_from_json_file = mock.MagicMock(side_effect=FileNotFoundError('boom'))
        authentication.load_last_nonces()
        assert authentication.LAST_NONCES == {'existing': 5}

    def test_save_last_nonces_persists(self, tmp_path):
        nonce_file = str(tmp_path / 'last_nonces.json')
        authentication.LAST_NONCES.clear()
        authentication.LAST_NONCES['foo'] = 7
        with mock.patch.object(authentication, 'LAST_NONCES_FILE', nonce_file):
            _REAL_SAVE_LAST_NONCES()
        assert os.path.isfile(nonce_file)
        with open(nonce_file, 'r') as f:
            assert json.load(f) == {'foo': 7}

    def test_save_last_nonces_creates_missing_directory(self, tmp_path):
        nonce_file = str(tmp_path / 'nested' / 'private' / 'last_nonces.json')
        authentication.LAST_NONCES.clear()
        authentication.LAST_NONCES['bar'] = 3
        with mock.patch.object(authentication, 'LAST_NONCES_FILE', nonce_file):
            _REAL_SAVE_LAST_NONCES()
        assert os.path.isfile(nonce_file)
        with open(nonce_file, 'r') as f:
            assert json.load(f) == {'bar': 3}

    def test_save_last_nonces_logs_error_and_cleans_up_on_replace_failure(self, tmp_path):
        nonce_file = str(tmp_path / 'last_nonces.json')
        authentication.LAST_NONCES.clear()
        authentication.LAST_NONCES['foo'] = 1
        with mock.patch.object(authentication, 'LAST_NONCES_FILE', nonce_file), \
             mock.patch.object(authentication, 'LOG') as mock_log, \
             mock.patch('os.replace', side_effect=OSError('boom')):
            _REAL_SAVE_LAST_NONCES()
        mock_log.error.assert_called_once()
        assert not os.path.isfile(nonce_file)
        assert os.listdir(str(tmp_path)) == []

    def test_save_last_nonces_logs_error_when_temp_file_creation_fails(self, tmp_path):
        nonce_file = str(tmp_path / 'last_nonces.json')
        authentication.LAST_NONCES.clear()
        authentication.LAST_NONCES['foo'] = 1
        with mock.patch.object(authentication, 'LAST_NONCES_FILE', nonce_file), \
             mock.patch.object(authentication, 'LOG') as mock_log, \
             mock.patch('tempfile.NamedTemporaryFile', side_effect=OSError('boom')):
            _REAL_SAVE_LAST_NONCES()
        mock_log.error.assert_called_once()
        assert not os.path.isfile(nonce_file)

    def test_invalid_signature_does_not_record_nonce(self):
        authentication.LAST_NONCES.clear()
        authentication.save_last_nonces = mock.MagicMock()
        authentication.load_from_json_file = mock.MagicMock(return_value={'foo': {'secret': 'bar1'}})
        headers = {'API_Key': 'foo',
                   'API_Sign': 'invalid_signature',
                   'API_Nonce': 999999999}
        assert authentication.check_authentication(headers, {'test': 'test'}) == authentication.AuthenticationStatus.INVALID_SIGNATURE
        assert 'foo' not in authentication.LAST_NONCES

    def test_valid_request_calls_save_last_nonces(self):
        authentication.LAST_NONCES.clear()
        authentication.save_last_nonces = mock.MagicMock()
        authentication.load_from_json_file = mock.MagicMock(return_value={'foo': {'secret': 'bar1'}})
        data = {'test': 'test'}
        nonce = 12345
        headers = {'API_Key': 'foo',
                   'API_Sign': authentication.signature(data, nonce, 'bar1'),
                   'API_Nonce': nonce}
        assert authentication.check_authentication(headers, data) == authentication.AuthenticationStatus.OK
        authentication.save_last_nonces.assert_called_once_with()

    def test_nonce_lock_is_a_threading_lock(self):
        assert isinstance(authentication._NONCE_LOCK, type(threading.Lock()))
