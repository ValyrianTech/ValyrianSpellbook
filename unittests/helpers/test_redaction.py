#!/usr/bin/env python
from helpers.redaction import (
    NORMALIZED_SENSITIVE_KEYS,
    REDACTED_VALUE,
    SENSITIVE_KEYS,
    is_sensitive_key,
    redact,
)


class TestRedaction:
    """Tests for the shared sensitive-key redaction helpers"""

    def test_sensitive_keys_contents(self):
        """Test SENSITIVE_KEYS contains the expected sensitive key names"""
        assert SENSITIVE_KEYS == {
            'api_key', 'api_secret', 'secret', 'private_key', 'privkey',
            'mnemonic', 'xpriv', 'password', 'passphrase', 'seed',
            'API_Sign', 'API_Key',
        }

    def test_redacted_value(self):
        """Test REDACTED_VALUE is the expected placeholder"""
        assert REDACTED_VALUE == '********'

    def test_normalized_sensitive_keys_lowercases_mixed_case(self):
        """Test NORMALIZED_SENSITIVE_KEYS lowercases every SENSITIVE_KEYS entry"""
        assert NORMALIZED_SENSITIVE_KEYS == frozenset(key.lower() for key in SENSITIVE_KEYS)
        assert 'api_sign' in NORMALIZED_SENSITIVE_KEYS
        assert 'api_key' in NORMALIZED_SENSITIVE_KEYS

    def test_is_sensitive_key_exact_names(self):
        """Test is_sensitive_key returns True for exact sensitive names"""
        for key in SENSITIVE_KEYS:
            assert is_sensitive_key(key) is True

    def test_is_sensitive_key_case_variants(self):
        """Test is_sensitive_key matches case-insensitively"""
        for name in ('private_key', 'Private_Key', 'PRIVATE_KEY', 'api_key', 'Api_Key', 'API_Key', 'api_sign', 'API_Sign'):
            assert is_sensitive_key(name) is True

    def test_is_sensitive_key_non_sensitive(self):
        """Test is_sensitive_key returns False for non-sensitive names"""
        assert is_sensitive_key('safe') is False
        assert is_sensitive_key('name') is False

    def test_is_sensitive_key_non_str(self):
        """Test is_sensitive_key returns False for non-str inputs"""
        assert is_sensitive_key(None) is False
        assert is_sensitive_key(123) is False

    def test_redact_sensitive_keys(self):
        """Test redact replaces sensitive values with REDACTED_VALUE"""
        result = redact({'api_key': 'secret', 'private_key': 'priv', 'seed': 'seed'})
        assert result == {'api_key': REDACTED_VALUE, 'private_key': REDACTED_VALUE, 'seed': REDACTED_VALUE}

    def test_redact_case_insensitive(self):
        """Test redact matches sensitive keys case-insensitively"""
        assert redact({'Api_Key': 'x'})['Api_Key'] == REDACTED_VALUE
        assert redact({'API_Sign': 'y'})['API_Sign'] == REDACTED_VALUE

    def test_redact_preserves_non_sensitive(self):
        """Test redact preserves non-sensitive values"""
        result = redact({'safe': 'visible', 'name': 'blockstream'})
        assert result == {'safe': 'visible', 'name': 'blockstream'}
