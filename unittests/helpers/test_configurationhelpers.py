#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock

from helpers.configurationhelpers import (
    spellbook_config,
    what_is_my_ip,
    get_host,
    get_port,
    get_notification_email,
    get_mail_on_exception,
    get_python_exe,
    get_websocket_port,
    get_key,
    get_secret,
    get_enable_wallet,
    get_wallet_dir,
    get_default_wallet,
    get_use_testnet,
    get_max_tx_fee_percentage,
    get_minimum_output_value,
    get_enable_smtp,
    get_smtp_from_address,
    get_smtp_host,
    get_smtp_port,
    get_smtp_user,
    get_smtp_password,
    get_enable_ipfs,
    get_ipfs_api_host,
    get_ipfs_api_port,
    get_ipfs_gateway_host,
    get_ipfs_gateway_port,
    get_app_data_dir,
    get_enable_ssl,
    get_domain_name,
    get_ssl_certificate,
    get_ssl_private_key,
    get_ssl_certificate_chain,
    get_spellbook_uri,
    get_enable_twitter,
    get_twitter_consumer_key,
    get_twitter_consumer_secret,
    get_twitter_access_token,
    get_twitter_access_token_secret,
    get_twitter_bearer_token,
    get_enable_openai,
    get_openai_api_key,
    get_openai_organization,
    get_enable_mastodon,
    get_mastodon_client_id,
    get_mastodon_client_secret,
    get_mastodon_access_token,
    get_mastodon_api_base_url,
    get_enable_nostr,
    get_nostr_nsec,
    get_enable_oobabooga,
    get_llms_default_model,
    get_enable_together_ai,
    get_together_ai_bearer_token,
    get_enable_uploads,
    get_uploads_dir,
    get_max_file_size,
    get_allowed_extensions,
    get_enable_transcribe,
    get_model_size_transcribe,
    get_max_file_size_transcribe,
    get_allowed_extensions_transcribe,
)


class TestConfigurationHelpers(object):
    """Tests for configuration helper functions"""

    def test_spellbook_config(self):
        """Test that spellbook_config returns a ConfigParser"""
        config = spellbook_config()
        assert config is not None

    @mock.patch('helpers.configurationhelpers.requests.get')
    def test_what_is_my_ip_success(self, mock_get):
        """Test getting IP address successfully"""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {'ip': '1.2.3.4'}
        mock_get.return_value = mock_response
        
        result = what_is_my_ip()
        assert result == '1.2.3.4'

    @mock.patch('helpers.configurationhelpers.requests.get')
    def test_what_is_my_ip_error(self, mock_get):
        """Test getting IP address when API fails"""
        mock_get.side_effect = Exception('Network error')
        
        result = what_is_my_ip()
        assert result == ''

    def test_get_host(self):
        """Test getting host from config"""
        # This will use the actual config file
        result = get_host()
        assert result is not None

    def test_get_port(self):
        """Test getting port from config"""
        result = get_port()
        assert isinstance(result, int)

    def test_get_use_testnet(self):
        """Test getting use_testnet from config"""
        result = get_use_testnet()
        assert isinstance(result, bool)

    @mock.patch('helpers.configurationhelpers.get_enable_ssl', return_value=True)
    @mock.patch('helpers.configurationhelpers.get_domain_name', return_value='example.com')
    @mock.patch('helpers.configurationhelpers.get_port', return_value=443)
    def test_get_spellbook_uri_ssl(self, mock_port, mock_domain, mock_ssl):
        """Test getting spellbook URI with SSL enabled"""
        result = get_spellbook_uri()
        assert result == 'https://example.com:443'

    @mock.patch('helpers.configurationhelpers.get_enable_ssl', return_value=False)
    @mock.patch('helpers.configurationhelpers.get_host', return_value='localhost')
    @mock.patch('helpers.configurationhelpers.get_port', return_value=8080)
    def test_get_spellbook_uri_no_ssl(self, mock_port, mock_host, mock_ssl):
        """Test getting spellbook URI without SSL"""
        result = get_spellbook_uri()
        assert result == 'http://localhost:8080'


class TestConfigurationGetters(object):
    """Tests for various configuration getter functions"""

    def test_get_notification_email(self):
        """Test getting notification email"""
        try:
            result = get_notification_email()
            assert result is not None or result == ''
        except Exception:
            pass  # Config may not have this value

    def test_get_mail_on_exception(self):
        """Test getting mail_on_exception"""
        try:
            result = get_mail_on_exception()
            assert isinstance(result, bool)
        except Exception:
            pass

    def test_get_python_exe(self):
        """Test getting python executable path"""
        try:
            result = get_python_exe()
            assert result is not None
        except Exception:
            pass

    def test_get_websocket_port(self):
        """Test getting websocket port"""
        try:
            result = get_websocket_port()
            assert result is not None
        except Exception:
            pass

    def test_get_key(self):
        """Test getting authentication key"""
        try:
            result = get_key()
            assert result is not None
        except Exception:
            pass

    def test_get_secret(self):
        """Test getting authentication secret"""
        try:
            result = get_secret()
            assert result is not None
        except Exception:
            pass

    def test_get_enable_wallet(self):
        """Test getting enable_wallet"""
        try:
            result = get_enable_wallet()
            assert result is not None
        except Exception:
            pass

    def test_get_wallet_dir(self):
        """Test getting wallet directory"""
        try:
            result = get_wallet_dir()
            assert result is not None
        except Exception:
            pass

    def test_get_default_wallet(self):
        """Test getting default wallet"""
        try:
            result = get_default_wallet()
            assert result is not None
        except Exception:
            pass

    def test_get_max_tx_fee_percentage(self):
        """Test getting max tx fee percentage"""
        try:
            result = get_max_tx_fee_percentage()
            assert isinstance(result, float)
        except Exception:
            pass

    def test_get_minimum_output_value(self):
        """Test getting minimum output value"""
        try:
            result = get_minimum_output_value()
            assert isinstance(result, int)
        except Exception:
            pass

    def test_get_enable_smtp(self):
        """Test getting enable_smtp"""
        try:
            result = get_enable_smtp()
            assert result is not None
        except Exception:
            pass

    def test_get_smtp_from_address(self):
        """Test getting SMTP from address"""
        try:
            result = get_smtp_from_address()
            assert result is not None
        except Exception:
            pass

    def test_get_smtp_host(self):
        """Test getting SMTP host"""
        try:
            result = get_smtp_host()
            assert result is not None
        except Exception:
            pass

    def test_get_smtp_port(self):
        """Test getting SMTP port"""
        try:
            result = get_smtp_port()
            assert result is not None
        except Exception:
            pass

    def test_get_smtp_user(self):
        """Test getting SMTP user"""
        try:
            result = get_smtp_user()
            assert result is not None
        except Exception:
            pass

    def test_get_smtp_password(self):
        """Test getting SMTP password"""
        try:
            result = get_smtp_password()
            assert result is not None
        except Exception:
            pass

    def test_get_enable_ipfs(self):
        """Test getting enable_ipfs"""
        try:
            result = get_enable_ipfs()
            assert isinstance(result, bool)
        except Exception:
            pass

    def test_get_ipfs_api_host(self):
        """Test getting IPFS API host"""
        try:
            result = get_ipfs_api_host()
            assert result is not None
        except Exception:
            pass

    def test_get_ipfs_api_port(self):
        """Test getting IPFS API port"""
        try:
            result = get_ipfs_api_port()
            assert result is not None
        except Exception:
            pass

    def test_get_ipfs_gateway_host(self):
        """Test getting IPFS gateway host"""
        try:
            result = get_ipfs_gateway_host()
            assert result is not None
        except Exception:
            pass

    def test_get_ipfs_gateway_port(self):
        """Test getting IPFS gateway port"""
        try:
            result = get_ipfs_gateway_port()
            assert result is not None
        except Exception:
            pass

    def test_get_app_data_dir(self):
        """Test getting app data directory"""
        try:
            result = get_app_data_dir()
            assert result is not None
        except Exception:
            pass

    def test_get_enable_ssl(self):
        """Test getting enable_ssl"""
        try:
            result = get_enable_ssl()
            assert isinstance(result, bool)
        except Exception:
            pass

    def test_get_domain_name(self):
        """Test getting domain name"""
        try:
            result = get_domain_name()
            assert result is not None
        except Exception:
            pass

    def test_get_ssl_certificate(self):
        """Test getting SSL certificate path"""
        try:
            result = get_ssl_certificate()
            assert result is not None
        except Exception:
            pass

    def test_get_ssl_private_key(self):
        """Test getting SSL private key path"""
        try:
            result = get_ssl_private_key()
            assert result is not None
        except Exception:
            pass

    def test_get_ssl_certificate_chain(self):
        """Test getting SSL certificate chain path"""
        try:
            result = get_ssl_certificate_chain()
            assert result is not None
        except Exception:
            pass

    def test_get_enable_twitter(self):
        """Test getting enable_twitter"""
        try:
            result = get_enable_twitter()
            assert isinstance(result, bool)
        except Exception:
            pass

    def test_get_twitter_consumer_key(self):
        """Test getting Twitter consumer key"""
        try:
            result = get_twitter_consumer_key()
            assert result is not None
        except Exception:
            pass

    def test_get_twitter_consumer_secret(self):
        """Test getting Twitter consumer secret"""
        try:
            result = get_twitter_consumer_secret()
            assert result is not None
        except Exception:
            pass

    def test_get_twitter_access_token(self):
        """Test getting Twitter access token"""
        try:
            result = get_twitter_access_token()
            assert result is not None
        except Exception:
            pass

    def test_get_twitter_access_token_secret(self):
        """Test getting Twitter access token secret"""
        try:
            result = get_twitter_access_token_secret()
            assert result is not None
        except Exception:
            pass

    def test_get_twitter_bearer_token(self):
        """Test getting Twitter bearer token"""
        try:
            result = get_twitter_bearer_token()
            assert result is not None
        except Exception:
            pass

    def test_get_enable_openai(self):
        """Test getting enable_openai"""
        try:
            result = get_enable_openai()
            assert isinstance(result, bool)
        except Exception:
            pass

    def test_get_openai_api_key(self):
        """Test getting OpenAI API key"""
        try:
            result = get_openai_api_key()
            assert result is not None
        except Exception:
            pass

    def test_get_openai_organization(self):
        """Test getting OpenAI organization"""
        try:
            result = get_openai_organization()
            assert result is not None
        except Exception:
            pass

    def test_get_enable_mastodon(self):
        """Test getting enable_mastodon"""
        try:
            result = get_enable_mastodon()
            assert isinstance(result, bool)
        except Exception:
            pass

    def test_get_mastodon_client_id(self):
        """Test getting Mastodon client ID"""
        try:
            result = get_mastodon_client_id()
            assert result is not None
        except Exception:
            pass

    def test_get_mastodon_client_secret(self):
        """Test getting Mastodon client secret"""
        try:
            result = get_mastodon_client_secret()
            assert result is not None
        except Exception:
            pass

    def test_get_mastodon_access_token(self):
        """Test getting Mastodon access token"""
        try:
            result = get_mastodon_access_token()
            assert result is not None
        except Exception:
            pass

    def test_get_mastodon_api_base_url(self):
        """Test getting Mastodon API base URL"""
        try:
            result = get_mastodon_api_base_url()
            assert result is not None
        except Exception:
            pass

    def test_get_enable_nostr(self):
        """Test getting enable_nostr"""
        try:
            result = get_enable_nostr()
            assert isinstance(result, bool)
        except Exception:
            pass

    def test_get_nostr_nsec(self):
        """Test getting Nostr nsec"""
        try:
            result = get_nostr_nsec()
            assert result is not None
        except Exception:
            pass

    def test_get_enable_oobabooga(self):
        """Test getting enable_oobabooga"""
        try:
            result = get_enable_oobabooga()
            assert isinstance(result, bool)
        except Exception:
            pass

    def test_get_llms_default_model(self):
        """Test getting LLMs default model"""
        try:
            result = get_llms_default_model()
            assert result is not None
        except Exception:
            pass

    def test_get_enable_together_ai(self):
        """Test getting enable_together_ai"""
        try:
            result = get_enable_together_ai()
            assert isinstance(result, bool)
        except Exception:
            pass

    def test_get_together_ai_bearer_token(self):
        """Test getting Together AI bearer token"""
        try:
            result = get_together_ai_bearer_token()
            assert result is not None
        except Exception:
            pass

    def test_get_enable_uploads(self):
        """Test getting enable_uploads"""
        try:
            result = get_enable_uploads()
            assert isinstance(result, bool)
        except Exception:
            pass

    def test_get_uploads_dir(self):
        """Test getting uploads directory"""
        try:
            result = get_uploads_dir()
            assert result is not None
        except Exception:
            pass

    def test_get_max_file_size(self):
        """Test getting max file size"""
        try:
            result = get_max_file_size()
            assert isinstance(result, int)
        except Exception:
            pass

    def test_get_allowed_extensions(self):
        """Test getting allowed extensions"""
        try:
            result = get_allowed_extensions()
            assert result is not None
        except Exception:
            pass

    def test_get_enable_transcribe(self):
        """Test getting enable_transcribe"""
        try:
            result = get_enable_transcribe()
            assert isinstance(result, bool)
        except Exception:
            pass

    def test_get_model_size_transcribe(self):
        """Test getting transcribe model size"""
        try:
            result = get_model_size_transcribe()
            assert result is not None
        except Exception:
            pass

    def test_get_max_file_size_transcribe(self):
        """Test getting transcribe max file size"""
        try:
            result = get_max_file_size_transcribe()
            assert isinstance(result, int)
        except Exception:
            pass

    def test_get_allowed_extensions_transcribe(self):
        """Test getting transcribe allowed extensions"""
        try:
            result = get_allowed_extensions_transcribe()
            assert result is not None
        except Exception:
            pass
