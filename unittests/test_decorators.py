#!/usr/bin/env python
from unittest import mock

import pytest

from authentication import AuthenticationStatus
from decorators import (
    CONFIGURATION_FILE,
    _scrub_trigger_secret,
    authentication_required,
    log_runtime,
    output_json,
    retry,
    trigger_authentication_required,
    use_explorer,
    verify_config,
)


class TestAuthenticationRequired:
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


class TestUseExplorer:
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

        test_func()
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


class TestOutputJson:
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


class TestVerifyConfig:
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


class TestLogRuntime:
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


class TestRetry:
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
                raise ValueError('Temporary error')
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
            raise ValueError('Permanent error')

        result = test_func()
        assert result is None
        assert call_count[0] == 3
        assert mock_log.error.call_count == 3


class TestConfigurationFile:
    """Tests for CONFIGURATION_FILE constant"""

    def test_configuration_file_path(self):
        assert 'spellbook.conf' in CONFIGURATION_FILE
        assert 'configuration' in CONFIGURATION_FILE


class TestTriggerAuthenticationRequired:
    """Tests for trigger_authentication_required decorator"""

    @mock.patch('helpers.triggerhelpers.load_trigger_config')
    @mock.patch('decorators.check_authentication')
    @mock.patch('decorators.request')
    def test_api_key_auth_ok(self, mock_request, mock_check, mock_get_config):
        mock_check.return_value = AuthenticationStatus.OK
        mock_request.headers = {}
        mock_request.json = None

        calls = []

        @trigger_authentication_required
        def test_func(trigger_id):
            calls.append(trigger_id)
            return {'success': True}

        result = test_func('trig1')
        assert result == {'success': True}
        assert calls == ['trig1']
        mock_get_config.assert_not_called()

    @mock.patch('helpers.triggerhelpers.load_trigger_config', return_value={})
    @mock.patch('decorators.check_authentication', return_value=AuthenticationStatus.NO_API_KEY)
    @mock.patch('decorators.request')
    def test_not_public_no_api_auth(self, mock_request, mock_check, mock_get_config):
        mock_request.headers = {}
        mock_request.json = None
        mock_request.query = mock.MagicMock()
        mock_request.query.secret = ''

        calls = []

        @trigger_authentication_required
        def test_func(trigger_id):
            calls.append(trigger_id)
            return {'success': True}

        result = test_func('trig1')
        assert 'error' in result
        assert result['error'] == AuthenticationStatus.NO_API_KEY
        assert calls == []

    @mock.patch('helpers.triggerhelpers.load_trigger_config', return_value={'public': False, 'secret': 's3cret'})
    @mock.patch('decorators.check_authentication', return_value=AuthenticationStatus.NO_API_KEY)
    @mock.patch('decorators.request')
    def test_public_false_no_api_auth(self, mock_request, mock_check, mock_get_config):
        mock_request.headers = {}
        mock_request.json = None
        mock_request.query = mock.MagicMock()
        mock_request.query.secret = ''

        calls = []

        @trigger_authentication_required
        def test_func(trigger_id):
            calls.append(trigger_id)
            return {'success': True}

        result = test_func('trig1')
        assert 'error' in result
        assert result['error'] == AuthenticationStatus.NO_API_KEY
        assert calls == []

    @mock.patch('helpers.triggerhelpers.load_trigger_config', return_value={'public': True, 'secret': 'sécret-ünïcode-日本'})
    @mock.patch('decorators.check_authentication', return_value=AuthenticationStatus.NO_API_KEY)
    @mock.patch('decorators.request')
    def test_public_non_ascii_secret(self, mock_request, mock_check, mock_get_config):
        mock_request.headers = {}
        mock_request.json = {'secret': 'sécret-ünïcode-日本'}
        mock_request.query = mock.MagicMock()
        mock_request.query.secret = ''

        calls = []

        @trigger_authentication_required
        def test_func(trigger_id):
            calls.append(trigger_id)
            return {'success': True}

        result = test_func('trig1')
        assert result == {'success': True}
        assert calls == ['trig1']

    @mock.patch('helpers.triggerhelpers.load_trigger_config', return_value={'public': True, 'secret': 's3cret'})
    @mock.patch('decorators.check_authentication', return_value=AuthenticationStatus.NO_API_KEY)
    @mock.patch('decorators.request')
    def test_public_secret_json_body(self, mock_request, mock_check, mock_get_config):
        mock_request.headers = {}
        mock_request.json = {'secret': 's3cret', 'data': 'x'}
        mock_request.query = mock.MagicMock()
        mock_request.query.secret = ''

        calls = []

        @trigger_authentication_required
        def test_func(trigger_id):
            calls.append(trigger_id)
            return {'success': True}

        result = test_func('trig1')
        assert result == {'success': True}
        assert calls == ['trig1']
        assert 'secret' not in mock_request.json

    @mock.patch('helpers.triggerhelpers.load_trigger_config', return_value={'public': True, 'secret': 's3cret'})
    @mock.patch('decorators.check_authentication', return_value=AuthenticationStatus.NO_API_KEY)
    @mock.patch('decorators.request')
    def test_public_secret_query_string(self, mock_request, mock_check, mock_get_config):
        mock_request.headers = {}
        mock_request.json = None
        mock_request.query = {'secret': 's3cret', 'foo': 'bar'}

        calls = []

        @trigger_authentication_required
        def test_func(trigger_id):
            calls.append(trigger_id)
            return {'success': True}

        result = test_func('trig1')
        assert result == {'success': True}
        assert calls == ['trig1']
        assert 'secret' not in mock_request.query
        assert mock_request.query['foo'] == 'bar'

    @mock.patch('helpers.triggerhelpers.load_trigger_config', return_value={'public': True, 'secret': 's3cret'})
    @mock.patch('decorators.check_authentication', return_value=AuthenticationStatus.NO_API_KEY)
    @mock.patch('decorators.request')
    def test_public_secret_header(self, mock_request, mock_check, mock_get_config):
        mock_request.headers = {'API_Secret': 's3cret'}
        mock_request.json = None
        mock_request.query = {}

        calls = []

        @trigger_authentication_required
        def test_func(trigger_id):
            calls.append(trigger_id)
            return {'success': True}

        result = test_func('trig1')
        assert result == {'success': True}
        assert calls == ['trig1']
        assert mock_request.headers['API_Secret'] == 's3cret'

    @mock.patch('helpers.triggerhelpers.load_trigger_config', return_value={'public': True, 'secret': 's3cret'})
    @mock.patch('decorators.check_authentication', return_value=AuthenticationStatus.NO_API_KEY)
    @mock.patch('decorators.request')
    def test_public_wrong_secret(self, mock_request, mock_check, mock_get_config):
        mock_request.headers = {}
        mock_request.json = {'secret': 'wrong'}
        mock_request.query = mock.MagicMock()
        mock_request.query.secret = ''

        calls = []

        @trigger_authentication_required
        def test_func(trigger_id):
            calls.append(trigger_id)
            return {'success': True}

        result = test_func('trig1')
        assert 'error' in result
        assert result['error'] == AuthenticationStatus.NO_API_KEY
        assert calls == []

    @mock.patch('helpers.triggerhelpers.load_trigger_config', return_value={'public': True, 'secret': 's3cret'})
    @mock.patch('decorators.check_authentication', return_value=AuthenticationStatus.NO_API_KEY)
    @mock.patch('decorators.request')
    def test_public_no_secret(self, mock_request, mock_check, mock_get_config):
        mock_request.headers = {}
        mock_request.json = None
        mock_request.query = mock.MagicMock()
        mock_request.query.secret = ''

        calls = []

        @trigger_authentication_required
        def test_func(trigger_id):
            calls.append(trigger_id)
            return {'success': True}

        result = test_func('trig1')
        assert 'error' in result
        assert result['error'] == AuthenticationStatus.NO_API_KEY
        assert calls == []

    @mock.patch('helpers.triggerhelpers.load_trigger_config', side_effect=OSError('boom'))
    @mock.patch('decorators.check_authentication', return_value=AuthenticationStatus.NO_API_KEY)
    @mock.patch('decorators.request')
    def test_get_trigger_config_oserror(self, mock_request, mock_check, mock_get_config):
        mock_request.headers = {}
        mock_request.json = None

        calls = []

        @trigger_authentication_required
        def test_func(trigger_id):
            calls.append(trigger_id)
            return {'success': True}

        result = test_func('trig1')
        assert 'error' in result
        assert result['error'] == AuthenticationStatus.NO_API_KEY
        assert calls == []

    @mock.patch('helpers.triggerhelpers.load_trigger_config', return_value={'public': True, 'secret': 's3cret'})
    @mock.patch('decorators.check_authentication', return_value=AuthenticationStatus.NO_API_KEY)
    @mock.patch('decorators.request')
    def test_trigger_id_kwarg(self, mock_request, mock_check, mock_get_config):
        mock_request.headers = {'API_Secret': 's3cret'}
        mock_request.json = None
        mock_request.query = {}

        calls = []

        @trigger_authentication_required
        def test_func(trigger_id):
            calls.append(trigger_id)
            return {'success': True}

        result = test_func(trigger_id='trig1')
        assert result == {'success': True}
        assert calls == ['trig1']
        mock_get_config.assert_called_once_with('trig1')

    @mock.patch('helpers.triggerhelpers.load_trigger_config', return_value={})
    @mock.patch('decorators.check_authentication', return_value=AuthenticationStatus.NO_API_KEY)
    @mock.patch('decorators.request')
    def test_no_args_no_kwargs(self, mock_request, mock_check, mock_get_config):
        mock_request.headers = {}
        mock_request.json = None
        mock_request.query = mock.MagicMock()
        mock_request.query.secret = ''

        calls = []

        @trigger_authentication_required
        def test_func(trigger_id=None):
            calls.append(trigger_id)
            return {'success': True}

        result = test_func()
        assert 'error' in result
        assert result['error'] == AuthenticationStatus.NO_API_KEY
        assert calls == []
        mock_get_config.assert_called_once_with(None)

    @mock.patch('decorators.request')
    def test_scrub_trigger_secret_direct(self, mock_request):
        mock_request.json = None
        mock_request.query = {'foo': 'bar'}
        mock_request.headers = {'API_Key': 'x'}

        _scrub_trigger_secret()

        assert mock_request.query == {'foo': 'bar'}
        assert mock_request.headers == {'API_Key': 'x'}

    @mock.patch('decorators.request')
    def test_scrub_trigger_secret_removes_all_paths(self, mock_request):
        mock_request.json = {'secret': 's3cret', 'data': 'x'}
        mock_request.query = {'secret': 's3cret', 'foo': 'bar'}
        mock_request.headers = {'API_Secret': 's3cret', 'API_Key': 'x'}

        _scrub_trigger_secret()

        assert 'secret' not in mock_request.json
        assert 'secret' not in mock_request.query
        assert mock_request.headers['API_Secret'] == 's3cret'
        assert mock_request.json['data'] == 'x'
        assert mock_request.query['foo'] == 'bar'
        assert mock_request.headers['API_Key'] == 'x'

    @mock.patch('helpers.triggerhelpers.load_trigger_config', return_value={'public': True, 'secret': 's3cret'})
    @mock.patch('decorators.check_authentication', return_value=AuthenticationStatus.NO_API_KEY)
    @mock.patch('decorators.request')
    def test_public_secret_header_readonly_mapping(self, mock_request, mock_check, mock_get_config):
        """Regression: bottle's read-only WSGIHeaderDict reports hasattr(..., 'pop')==True but pop() raises TypeError."""
        class ReadOnlyHeaderDict(dict):
            def pop(self, *args, **kwargs):
                raise TypeError("read-only")

        headers = ReadOnlyHeaderDict({'API_Secret': 's3cret'})
        mock_request.headers = headers
        mock_request.json = None
        mock_request.query = {}

        calls = []

        @trigger_authentication_required
        def test_func(trigger_id):
            calls.append(trigger_id)
            return {'success': True}

        result = test_func('trig1')

        assert result == {'success': True}
        assert calls == ['trig1']
        # The header must not have been mutated/removed
        assert headers['API_Secret'] == 's3cret'

    @mock.patch('decorators.request')
    def test_scrub_trigger_secret_readonly_header_and_query(self, mock_request):
        class ReadOnlyMapping(dict):
            def pop(self, *args, **kwargs):
                raise TypeError("read-only")

        mock_request.json = None
        mock_request.query = ReadOnlyMapping({'secret': 'x'})
        mock_request.headers = ReadOnlyMapping({'API_Secret': 'x'})
        _scrub_trigger_secret()  # must not raise
