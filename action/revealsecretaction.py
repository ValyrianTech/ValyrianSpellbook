#!/usr/bin/env python

"""Action that reveals a pre-configured secret."""

import os

import simplejson

from AESCipher import AESCipher
from helpers.jsonhelpers import load_from_json_file, save_to_json_file
from helpers.loghelpers import LOG
from helpers.pathhelpers import safe_path

from .action import Action
from .actionresult import ActionResult
from .actiontype import ActionType

SECRETS_DIR = 'json/private/secrets'
SECRET_STORE_KEY_FILE = 'json/private/secret_store.key'


def _get_secret_store_key():
    """Return the secret-store encryption key, creating it on first use.

    The key is a random 32-byte hex string persisted to ``SECRET_STORE_KEY_FILE``
    with mode ``0o600`` inside a directory that is forced to mode ``0o700``. The
    key file is created lazily so that importing this module does not touch the
    filesystem.

    :return: The secret-store encryption key as a hex string.
    """
    parent_dir = os.path.dirname(SECRET_STORE_KEY_FILE)
    if not os.path.isdir(parent_dir):
        os.makedirs(parent_dir, mode=0o700)
    else:
        os.chmod(parent_dir, 0o700)

    if not os.path.isfile(SECRET_STORE_KEY_FILE):
        key = os.urandom(32).hex()
        with open(SECRET_STORE_KEY_FILE, 'w') as key_file:
            key_file.write(key)
        os.chmod(SECRET_STORE_KEY_FILE, 0o600)

    with open(SECRET_STORE_KEY_FILE, 'r') as key_file:
        return key_file.read().strip()


class RevealSecretAction(Action):
    """Action that reveals a pre-configured secret."""
    def __init__(self, action_id):
        super().__init__(action_id=action_id)
        self.action_type = ActionType.REVEALSECRET
        self.reveal_text = None
        self.reveal_link = None
        self.secret_id = None
        self.allow_reveal = False
        self.secret_load_failed = False

    def run(self):
        """
        Run the action

        :return: An ActionResult indicating success or failure
        """
        LOG.info(f'Allowing reveal of RevealSecret action {self.id}')
        self.allow_reveal = True
        self.save()
        return ActionResult(success=True)

    def configure(self, **config):
        """
        Configure the action with given config settings

        :param config: A dict containing the configuration settings
                       - config['reveal_text']  : A secret text
                       - config['reveal_link']  : A secret link
                       - config['secret_id']    : The id used to store the secret
                       - config['allow_reveal'] : Is the secret allowed to be revealed?
        """
        super().configure(**config)
        if 'reveal_text' in config:
            self.reveal_text = config['reveal_text']

        if 'reveal_link' in config:
            self.reveal_link = config['reveal_link']

        if 'secret_id' in config:
            self.secret_id = config['secret_id']

        if 'allow_reveal' in config:
            self.allow_reveal = config['allow_reveal'] is True

    def json_encodable(self):
        """
        Get the action config in a json encodable format

        :return: A dict containing the configuration settings
        """
        ret = super().json_encodable()
        ret.update({'allow_reveal': self.allow_reveal,
                    'secret_id': self.secret_id})
        return ret

    def save_secret(self):
        """Encrypt and persist this action's secret fields to the private secrets store."""
        self.secret_id = self.secret_id or self.id
        if self.secret_load_failed and self.reveal_text is None and self.reveal_link is None:
            LOG.warning(f'Refusing to overwrite stored secret for RevealSecret action {self.id}: could not be decrypted')
            return
        payload = {'reveal_text': self.reveal_text, 'reveal_link': self.reveal_link}
        ciphertext = AESCipher(key=_get_secret_store_key()).encrypt(simplejson.dumps(payload).encode('utf-8'))
        secret_file = safe_path(SECRETS_DIR, f'{self.secret_id}.json')
        save_to_json_file(secret_file, {'secret_id': self.secret_id, 'data': ciphertext.decode('utf-8')})
        os.chmod(secret_file, 0o600)
        secrets_dir = os.path.dirname(secret_file)
        if os.path.isdir(secrets_dir):
            # The secret store must be private like json/private, regardless of the
            # default permissions applied by save_to_json_file's os.makedirs.
            os.chmod(secrets_dir, 0o700)
        self.secret_load_failed = False

    def load_secret(self):
        """Load and decrypt this action's secret fields from the private secrets store."""
        if self.secret_id is None:
            return

        self.secret_load_failed = False

        try:
            secret_file = safe_path(SECRETS_DIR, f'{self.secret_id}.json')
            data = load_from_json_file(secret_file)
        except (FileNotFoundError, OSError, ValueError, TypeError, KeyError):
            self.secret_load_failed = False
            LOG.warning(f'Unable to load secret for RevealSecret action {self.id}: missing or unreadable secret file')
            return

        try:
            plaintext = AESCipher(key=_get_secret_store_key()).decrypt(data['data'])
            payload = simplejson.loads(plaintext)
            self.reveal_text = payload['reveal_text']
            self.reveal_link = payload['reveal_link']
        except (ValueError, KeyError, TypeError) as ex:
            self.secret_load_failed = True
            LOG.warning(f'Unable to decrypt secret for RevealSecret action {self.id}: {ex}')
            return

    def delete_secret(self):
        """Delete this action's encrypted secret file from the private secrets store.

        The secret file is named after ``secret_id`` when set, otherwise the
        action id. A missing file is tolerated (no error), and an invalid
        secret id that fails ``safe_path`` validation only logs a warning.
        """
        secret_id = self.secret_id or self.id
        try:
            secret_file = safe_path(SECRETS_DIR, f'{secret_id}.json')
        except ValueError:
            LOG.warning(f'Unable to delete secret for RevealSecret action {self.id}: invalid secret id {secret_id!r}')
            return

        if os.path.isfile(secret_file):
            os.remove(secret_file)

    def save(self):
        """Save the action config and its encrypted secret.

        The public action file is written and chmodded to ``0o600`` by
        ``Action.save()``, so only the secret needs extra handling here.
        """
        self.save_secret()
        super().save()
