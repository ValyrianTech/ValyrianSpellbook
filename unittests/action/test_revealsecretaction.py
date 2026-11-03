#!/usr/bin/env python
from unittest import mock

import simplejson

from action import action as action_module
from action import revealsecretaction
from action.actiontype import ActionType
from action.revealsecretaction import RevealSecretAction, _get_secret_store_key
from AESCipher import AESCipher
from helpers.jsonhelpers import save_to_json_file


class TestRevealSecretAction:
    """Tests for RevealSecretAction"""

    def test_revealsecretaction_init(self):
        action = RevealSecretAction('test_reveal_action')
        assert action.id == 'test_reveal_action'
        assert action.action_type == ActionType.REVEALSECRET
        assert action.reveal_text is None
        assert action.reveal_link is None
        assert action.secret_id is None
        assert not action.allow_reveal

    def test_revealsecretaction_configure(self):
        action = RevealSecretAction('test_reveal_action')
        action.configure(
            reveal_text='secret message',
            reveal_link='http://secret.link',
            secret_id='my_secret_id',
            allow_reveal=True
        )
        assert action.reveal_text == 'secret message'
        assert action.reveal_link == 'http://secret.link'
        assert action.secret_id == 'my_secret_id'
        assert action.allow_reveal

    def test_revealsecretaction_configure_coerces_non_boolean_allow_reveal(self):
        """Test that a non-boolean allow_reveal value is coerced to a real bool"""
        action = RevealSecretAction('test_reveal_action')
        action.configure(allow_reveal='False')
        assert action.allow_reveal is False
        action.configure(allow_reveal='false')
        assert action.allow_reveal is False
        action.configure(allow_reveal=1)
        assert action.allow_reveal is False
        action.configure(allow_reveal=True)
        assert action.allow_reveal is True

    def test_revealsecretaction_configure_partial(self):
        action = RevealSecretAction('test_reveal_action')
        action.configure(reveal_text='only text')
        assert action.reveal_text == 'only text'
        assert action.reveal_link is None
        assert action.secret_id is None
        assert not action.allow_reveal

    def test_revealsecretaction_json_encodable(self):
        action = RevealSecretAction('test_reveal_action')
        action.configure(
            reveal_text='secret',
            reveal_link='http://link.com',
            secret_id='secret_id_value',
            allow_reveal=True,
            created=1609459200
        )
        result = action.json_encodable()
        assert result['id'] == 'test_reveal_action'
        assert result['action_type'] == ActionType.REVEALSECRET
        assert result['allow_reveal']
        assert result['secret_id'] == 'secret_id_value'
        assert 'reveal_text' not in result
        assert 'reveal_link' not in result

    @mock.patch.object(RevealSecretAction, 'save')
    def test_revealsecretaction_run(self, mock_save):
        action = RevealSecretAction('test_reveal_action')
        action.allow_reveal = False
        result = action.run()
        assert result
        assert action.allow_reveal
        mock_save.assert_called_once()


class TestSecretStoreKey:
    """Tests for the module-level secret-store key helper"""

    def test_get_secret_store_key_creates_and_reuses(self, tmp_path, monkeypatch):
        key_file = tmp_path / 'nested' / 'secret_store.key'
        monkeypatch.setattr(revealsecretaction, 'SECRET_STORE_KEY_FILE', str(key_file))

        key1 = _get_secret_store_key()

        assert key_file.exists()
        assert oct(key_file.stat().st_mode & 0o777) == '0o600'
        assert oct(key_file.parent.stat().st_mode & 0o777) == '0o700'
        assert len(key1) == 64

        key2 = _get_secret_store_key()
        assert key2 == key1
        assert key_file.read_text() == key1

    def test_get_secret_store_key_chmods_existing_parent_dir(self, tmp_path, monkeypatch):
        key_file = tmp_path / 'secret_store.key'
        tmp_path.chmod(0o755)
        monkeypatch.setattr(revealsecretaction, 'SECRET_STORE_KEY_FILE', str(key_file))

        _get_secret_store_key()

        assert oct(tmp_path.stat().st_mode & 0o777) == '0o700'


class TestSecretPersistence:
    """Tests for encrypted secret persistence (save_secret/load_secret/save)"""

    def test_save_and_load_secret_round_trip(self, tmp_path, monkeypatch):
        monkeypatch.setattr(revealsecretaction, 'SECRETS_DIR', str(tmp_path / 'secrets'))
        monkeypatch.setattr(revealsecretaction, 'SECRET_STORE_KEY_FILE', str(tmp_path / 'secret_store.key'))

        action = RevealSecretAction('test_reveal_action')
        action.configure(reveal_text='secret message', reveal_link='http://secret.link')
        action.save_secret()

        assert action.secret_id == 'test_reveal_action'
        secret_file = tmp_path / 'secrets' / 'test_reveal_action.json'
        assert secret_file.exists()
        assert oct(secret_file.stat().st_mode & 0o777) == '0o600'

        raw = secret_file.read_text()
        assert 'secret message' not in raw
        assert 'http://secret.link' not in raw
        stored = simplejson.loads(raw)
        assert stored['secret_id'] == 'test_reveal_action'

        new_action = RevealSecretAction('test_reveal_action')
        new_action.secret_id = 'test_reveal_action'
        new_action.load_secret()
        assert new_action.reveal_text == 'secret message'
        assert new_action.reveal_link == 'http://secret.link'

    def test_load_secret_no_secret_id(self):
        action = RevealSecretAction('test_reveal_action')
        action.load_secret()
        assert action.reveal_text is None
        assert action.reveal_link is None

    @mock.patch.object(revealsecretaction.LOG, 'warning')
    def test_load_secret_missing_file(self, mock_warning, tmp_path, monkeypatch):
        monkeypatch.setattr(revealsecretaction, 'SECRETS_DIR', str(tmp_path / 'secrets'))
        monkeypatch.setattr(revealsecretaction, 'SECRET_STORE_KEY_FILE', str(tmp_path / 'secret_store.key'))

        action = RevealSecretAction('test_reveal_action')
        action.secret_id = 'test_reveal_action'
        action.load_secret()

        assert action.reveal_text is None
        assert action.reveal_link is None
        mock_warning.assert_called_once()

    @mock.patch.object(revealsecretaction.LOG, 'warning')
    def test_load_secret_decryption_fails(self, mock_warning, tmp_path, monkeypatch):
        monkeypatch.setattr(revealsecretaction, 'SECRETS_DIR', str(tmp_path / 'secrets'))
        monkeypatch.setattr(revealsecretaction, 'SECRET_STORE_KEY_FILE', str(tmp_path / 'secret_store.key'))

        action = RevealSecretAction('test_reveal_action')
        action.secret_id = 'test_reveal_action'
        secret_file = tmp_path / 'secrets' / 'test_reveal_action.json'
        save_to_json_file(str(secret_file), {'secret_id': 'test_reveal_action', 'data': 'not-a-valid-ciphertext'})

        action.load_secret()

        assert action.reveal_text is None
        assert action.reveal_link is None
        mock_warning.assert_called_once()

    @mock.patch.object(revealsecretaction.LOG, 'warning')
    def test_load_secret_malformed_payload(self, mock_warning, tmp_path, monkeypatch):
        monkeypatch.setattr(revealsecretaction, 'SECRETS_DIR', str(tmp_path / 'secrets'))
        monkeypatch.setattr(revealsecretaction, 'SECRET_STORE_KEY_FILE', str(tmp_path / 'secret_store.key'))

        key = _get_secret_store_key()
        ciphertext = AESCipher(key=key).encrypt(simplejson.dumps({'foo': 'bar'}).encode('utf-8')).decode('utf-8')
        secret_file = tmp_path / 'secrets' / 'test_reveal_action.json'
        save_to_json_file(str(secret_file), {'secret_id': 'test_reveal_action', 'data': ciphertext})

        action = RevealSecretAction('test_reveal_action')
        action.secret_id = 'test_reveal_action'
        action.load_secret()

        assert action.reveal_text is None
        assert action.reveal_link is None
        mock_warning.assert_called_once()

    @mock.patch.object(revealsecretaction.LOG, 'warning')
    def test_load_secret_non_dict_data(self, mock_warning, tmp_path, monkeypatch):
        monkeypatch.setattr(revealsecretaction, 'SECRETS_DIR', str(tmp_path / 'secrets'))
        monkeypatch.setattr(revealsecretaction, 'SECRET_STORE_KEY_FILE', str(tmp_path / 'secret_store.key'))

        secret_file = tmp_path / 'secrets' / 'test_reveal_action.json'
        save_to_json_file(str(secret_file), [1, 2, 3])

        action = RevealSecretAction('test_reveal_action')
        action.secret_id = 'test_reveal_action'
        action.load_secret()

        assert action.reveal_text is None
        assert action.reveal_link is None
        mock_warning.assert_called_once()

    def test_save_persists_secret_not_public_plaintext(self, tmp_path, monkeypatch):
        monkeypatch.setattr(revealsecretaction, 'SECRETS_DIR', str(tmp_path / 'secrets'))
        monkeypatch.setattr(revealsecretaction, 'SECRET_STORE_KEY_FILE', str(tmp_path / 'secret_store.key'))
        monkeypatch.setattr(revealsecretaction, 'ACTIONS_DIR', str(tmp_path / 'actions'))
        monkeypatch.setattr(action_module, 'ACTIONS_DIR', str(tmp_path / 'actions'))

        action = RevealSecretAction('test_reveal_action')
        action.configure(reveal_text='secret text', reveal_link='http://example.com')
        action.save()

        public_file = tmp_path / 'actions' / 'test_reveal_action.json'
        assert public_file.exists()
        assert oct(public_file.stat().st_mode & 0o777) == '0o600'
        public_content = public_file.read_text()
        assert 'secret text' not in public_content
        assert 'http://example.com' not in public_content

        secret_file = tmp_path / 'secrets' / 'test_reveal_action.json'
        assert secret_file.exists()
        assert oct(secret_file.stat().st_mode & 0o777) == '0o600'

    @mock.patch.object(action_module.Action, 'save')
    def test_save_when_public_action_file_missing(self, mock_super_save, tmp_path, monkeypatch):
        monkeypatch.setattr(revealsecretaction, 'SECRETS_DIR', str(tmp_path / 'secrets'))
        monkeypatch.setattr(revealsecretaction, 'SECRET_STORE_KEY_FILE', str(tmp_path / 'secret_store.key'))
        monkeypatch.setattr(revealsecretaction, 'ACTIONS_DIR', str(tmp_path / 'actions'))

        action = RevealSecretAction('test_reveal_action')
        action.configure(reveal_text='secret text')
        action.save()

        mock_super_save.assert_called_once()
        assert (tmp_path / 'secrets' / 'test_reveal_action.json').exists()
        assert not (tmp_path / 'actions' / 'test_reveal_action.json').exists()
