#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock
import time

from decorators import (
    authentication_required,
    use_explorer,
    output_json,
    verify_config,
    log_runtime,
    retry,
    CONFIGURATION_FILE
)
from authentication import AuthenticationStatus


class TestAuthenticationRequired(object):
    """Tests for authentication_required decorator"""

    @mock.patch('decorators.request')
    @mock.patch('decorators.check_authentication')
    def test_authentication_ok(self, mock_check, mock_request):
        mock_check.return_value = AuthenticationStatus.OK
        mock_request.headers = {}
        mock_request.json = {}

        @authentication_required
        def test_func():
            return {'success': True}

        result = test_func()
        assert result == {'success': True}

    @mock.patch('decorators.request')
    @mock.patch('decorators.check_authentication')
    def test_authentication_failed(self, mock_check, mock_request):
        mock_check.return_value = AuthenticationStatus.INVALID_API_KEY
        mock_request.headers = {}
        mock_request.json = {}

        @authentication_required
        def test_func():
            return {'success': True}

        result = test_func()
        assert 'error' in result
        assert result['error'] == AuthenticationStatus.INVALID_API_KEY


class TestUseExplorer(object):
    """Tests for use_explorer decorator"""

    @mock.patch('decorators.clear_explorer')
    @mock.patch('decorators.get_last_explorer')
    @mock.patch('decorators.set_explorer')
    @mock.patch('decorators.request')
    def test_use_explorer_with_explorer(self, mock_request, mock_set, mock_get_last, mock_clear):
        mock_request.query.explorer = 'blockstream'
        mock_get_last.return_value = 'blockstream'

        @use_explorer
        def test_func():
            return {'data': 'test'}

        result = test_func()
        mock_set.assert_called_once_with('blockstream')
        mock_clear.assert_called_once()
        assert result['explorer'] == 'blockstream'

    @mock.patch('decorators.clear_explorer')
    @mock.patch('decorators.get_last_explorer')
    @mock.patch('decorators.set_explorer')
    @mock.patch('decorators.request')
    def test_use_explorer_without_explorer(self, mock_request, mock_set, mock_get_last, mock_clear):
        mock_request.query.explorer = ''
        mock_get_last.return_value = None

        @use_explorer
        def test_func():
            return {'data': 'test'}

        result = test_func()
        mock_set.assert_not_called()
        mock_clear.assert_called_once()

    @mock.patch('decorators.clear_explorer')
    @mock.patch('decorators.get_last_explorer')
    @mock.patch('decorators.set_explorer')
    @mock.patch('decorators.request')
    def test_use_explorer_non_dict_return(self, mock_request, mock_set, mock_get_last, mock_clear):
        mock_request.query.explorer = ''

        @use_explorer
        def test_func():
            return "string result"

        result = test_func()
        assert result == "string result"
        mock_clear.assert_called_once()


class TestOutputJson(object):
    """Tests for output_json decorator"""

    def test_output_json_dict(self):
        @output_json
        def test_func():
            return {'key': 'value'}

        result = test_func()
        assert '"key": "value"' in result

    def test_output_json_list(self):
        @output_json
        def test_func():
            return [1, 2, 3]

        result = test_func()
        assert '1' in result
        assert '2' in result
        assert '3' in result

    def test_output_json_none(self):
        @output_json
        def test_func():
            return None

        result = test_func()
        assert result is None


class TestVerifyConfig(object):
    """Tests for verify_config decorator"""

    @mock.patch('decorators.ConfigParser')
    def test_verify_config_missing_section(self, mock_config_class):
        mock_config = mock.MagicMock()
        mock_config.has_section.return_value = False
        mock_config_class.return_value = mock_config

        @verify_config('TestSection', 'test_option')
        def test_func():
            return True

        with pytest.raises(Exception) as exc_info:
            test_func()
        assert 'does not have a [TestSection] section' in str(exc_info.value)

    @mock.patch('decorators.ConfigParser')
    def test_verify_config_missing_option(self, mock_config_class):
        mock_config = mock.MagicMock()
        mock_config.has_section.return_value = True
        mock_config.has_option.return_value = False
        mock_config_class.return_value = mock_config

        @verify_config('TestSection', 'test_option')
        def test_func():
            return True

        with pytest.raises(Exception) as exc_info:
            test_func()
        assert "does not have an option 'test_option'" in str(exc_info.value)

    @mock.patch('decorators.ConfigParser')
    def test_verify_config_success(self, mock_config_class):
        mock_config = mock.MagicMock()
        mock_config.has_section.return_value = True
        mock_config.has_option.return_value = True
        mock_config_class.return_value = mock_config

        @verify_config('TestSection', 'test_option')
        def test_func():
            return 'success'

        result = test_func()
        assert result == 'success'


class TestLogRuntime(object):
    """Tests for log_runtime decorator"""

    @mock.patch('decorators.LOG')
    def test_log_runtime(self, mock_log):
        @log_runtime
        def test_func():
            return 'result'

        result = test_func()
        assert result == 'result'
        mock_log.info.assert_called_once()
        call_args = mock_log.info.call_args[0][0]
        assert 'Script runtime' in call_args


class TestRetry(object):
    """Tests for retry decorator"""

    def test_retry_success_first_try(self):
        call_count = [0]

        @retry(retries=3)
        def test_func():
            call_count[0] += 1
            return 'success'

        result = test_func()
        assert result == 'success'
        assert call_count[0] == 1

    @mock.patch('decorators.time.sleep')
    @mock.patch('decorators.LOG')
    def test_retry_success_after_failures(self, mock_log, mock_sleep):
        call_count = [0]

        @retry(retries=3)
        def test_func():
            call_count[0] += 1
            if call_count[0] < 3:
                raise Exception('Temporary error')
            return 'success'

        result = test_func()
        assert result == 'success'
        assert call_count[0] == 3

    @mock.patch('decorators.time.sleep')
    @mock.patch('decorators.LOG')
    def test_retry_all_failures(self, mock_log, mock_sleep):
        call_count = [0]

        @retry(retries=3)
        def test_func():
            call_count[0] += 1
            raise Exception('Permanent error')

        result = test_func()
        assert result is None
        assert call_count[0] == 3
        assert mock_log.error.call_count == 3


class TestConfigurationFile(object):
    """Tests for CONFIGURATION_FILE constant"""

    def test_configuration_file_path(self):
        assert 'spellbook.conf' in CONFIGURATION_FILE
        assert 'configuration' in CONFIGURATION_FILE
