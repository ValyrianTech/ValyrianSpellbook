#!/usr/bin/env python
"""Helper functions for managing the encrypted hot wallet (keys, addresses, seeds)."""

import base64
import binascii
import getpass
import os

import simplejson
from Crypto.Cipher import AES  # nosec B413 # pycryptodome, not the deprecated pyCrypto

from AESCipher import V2_PREFIX, VERSION, AESCipher
from bips.bip39 import get_seed
from bips.bip44 import (
    get_address_from_xpub,
    get_addresses_from_xpub,
    get_private_key,
    get_xpriv_key,
    get_xpub_key,
)
from helpers.configurationhelpers import get_default_wallet, get_wallet_dir
from helpers.loghelpers import LOG

HOT_WALLET_PASSWORD = None
ALLOW_INSECURE_PASSWORD_ENV_VAR = 'SPELLBOOK_ALLOW_INSECURE_WALLET_PASSWORD'
ALLOW_LEGACY_DECRYPT_ENV_VAR = 'SPELLBOOK_ALLOW_LEGACY_WALLET_DECRYPT'


class LegacyWalletDecryptDisabled(ValueError):
    """Raised when a legacy (v1) hot wallet is found but the explicit opt-in env var is not set.

    Subclasses ``ValueError`` so existing ``except ValueError`` handlers keep working, but
    :func:`get_hot_wallet` re-raises it verbatim so the operator sees the actionable migration
    guidance instead of the generic 'Invalid password to decrypt hot wallet!' message.
    """


def _insecure_password_allowed():
    """Return True when the explicit insecure-password opt-in env var is set (covers empty AND short passwords)."""
    return os.environ.get(ALLOW_INSECURE_PASSWORD_ENV_VAR, '').strip().lower() in ('1', 'true', 'yes', 'on')


def _legacy_decrypt_allowed():
    """Return True when the explicit legacy-wallet-decrypt opt-in env var is set."""
    return os.environ.get(ALLOW_LEGACY_DECRYPT_ENV_VAR, '').strip().lower() in ('1', 'true', 'yes', 'on')


def is_legacy_encrypted_payload(encrypted_data):
    """Return True only when the payload is not a v2 payload but is structurally a legacy (v1) AES-CBC payload."""
    if isinstance(encrypted_data, str):
        encrypted_data = encrypted_data.encode('utf-8')

    try:
        data = base64.b64decode(encrypted_data, validate=True)
    except (binascii.Error, ValueError, TypeError):
        return False

    if not isinstance(data, bytes) or len(data) < 2 * AES.block_size:
        return False

    return not data.startswith(V2_PREFIX) and data[:1] != VERSION \
        and (len(data) - AES.block_size) % AES.block_size == 0


def decrypt_legacy_wallet_data(encrypted_data, password):
    """Decrypt a legacy (v1) AES-CBC wallet payload into a dict, gated by the explicit opt-in env var.

    :raises LegacyWalletDecryptDisabled: If the opt-in env var is not set (carries the migration guidance).
    :raises ValueError: If the payload is malformed, tampered with, or the password is wrong.
    """
    if not _legacy_decrypt_allowed():
        raise LegacyWalletDecryptDisabled(
            f'Legacy (unauthenticated AES-CBC) hot wallets are not decrypted by default. '
            f'Set {ALLOW_LEGACY_DECRYPT_ENV_VAR}=1 to opt in to decrypting them.'
        )
    LOG.warning('Decrypted an unauthenticated legacy (AES-CBC) hot wallet; re-saving the wallet re-encrypts it in the authenticated v2 format.')
    return simplejson.loads(AESCipher(key=password).decrypt_legacy(encrypted_data))


def _decrypt_with_empty_password(encrypted_data):
    """Decrypt the hot wallet with an empty password, falling back to the legacy path when applicable.

    Legacy (v1) AES-CBC payloads are read through :func:`decrypt_legacy_wallet_data`, which stays
    gated by the explicit legacy opt-in env var, so empty-password legacy wallets keep working
    without prompting.

    :returns: The decrypted wallet dict, or ``None`` when the empty password does not open the
        wallet (the caller then prompts for a password).
    :raises KeyError: If decryption fails with an unexpected error.
    :raises TypeError: If decryption fails with an unexpected error.
    """
    try:
        return simplejson.loads(AESCipher(key='').decrypt(encrypted_data))
    except (KeyError, TypeError) as ex:
        LOG.error(f'Empty-password decryption attempt failed with an unexpected error: {ex}')
        raise
    except ValueError as ex:
        if not is_legacy_encrypted_payload(encrypted_data):
            if len(encrypted_data) > 0:
                LOG.warning('Empty-password decryption attempt failed for a non-empty wallet file; '
                            'the wallet is most likely protected by a non-empty password, or it may be corrupt or tampered with: '
                            f'{ex}')
            else:
                LOG.warning(f'Empty-password decryption attempt failed: {ex}')
            return None

    try:
        return decrypt_legacy_wallet_data(encrypted_data, '')
    except LegacyWalletDecryptDisabled as ex:
        LOG.warning(f'Empty-password decryption of a legacy hot wallet is disabled: {ex}')
    except (ValueError, KeyError, TypeError) as ex:
        LOG.warning(f'Empty-password decryption of a legacy hot wallet failed: {ex}')

    return None


def get_hot_wallet():
    """Decrypt and return the hot wallet data, prompting for password if needed."""
    wallet_dir, wallet_id = get_wallet_dir(), get_default_wallet()
    wallet_path = os.path.join(wallet_dir, f'{wallet_id}.enc')

    if HOT_WALLET_PASSWORD is None:
        if _insecure_password_allowed():
            with open(wallet_path, 'r') as input_file:
                encrypted_data = input_file.read()

            data = _decrypt_with_empty_password(encrypted_data)
            if data is not None:
                LOG.critical('Hot wallet decrypted with an EMPTY password! This is insecure. '
                             'Set a strong password to protect the hot wallet.')
                return data

        prompt_decryption_password()

    try:
        with open(wallet_path, 'r') as input_file:
            encrypted_data = input_file.read()
        try:
            cipher = AESCipher(key=HOT_WALLET_PASSWORD)
            return simplejson.loads(cipher.decrypt(encrypted_data))
        except ValueError:
            if is_legacy_encrypted_payload(encrypted_data):
                return decrypt_legacy_wallet_data(encrypted_data, HOT_WALLET_PASSWORD)
            raise

    except LegacyWalletDecryptDisabled:
        # Re-raise verbatim: the operator needs the migration guidance, not a bogus 'invalid password'.
        raise
    except (ValueError, KeyError, TypeError, OSError) as ex:
        raise ValueError('Invalid password to decrypt hot wallet!') from ex


def prompt_decryption_password():
    """Prompt the user for the hot wallet decryption password."""
    global HOT_WALLET_PASSWORD
    # if this is running in pycharm console, make sure 'Emulate terminal in output console' is checked in the configuration
    HOT_WALLET_PASSWORD = getpass.getpass('Enter the password to decrypt the hot wallet: ')


def get_address_from_wallet(account, index):
    """Derive a Bitcoin address from the hot wallet for the given account and index."""
    xpub_key = get_xpub_key_from_wallet(account)
    return get_address_from_xpub(xpub=xpub_key, i=index)


def get_xpub_key_from_wallet(account):
    """Derive the xpub key for the given account from the hot wallet."""
    hot_wallet = get_hot_wallet()
    xpub_key = get_xpub_key(mnemonic=' '.join(hot_wallet['mnemonic']),
                            passphrase=hot_wallet['passphrase'],
                            account=account)

    # Explicitly delete the local variable hot wallet from memory as soon as possible for security reasons
    del hot_wallet

    return xpub_key


def get_xpriv_key_from_wallet(account):
    """Derive the xpriv key for the given account from the hot wallet."""
    hot_wallet = get_hot_wallet()
    xpriv_key = get_xpriv_key(mnemonic=' '.join(hot_wallet['mnemonic']),
                              passphrase=hot_wallet['passphrase'],
                              account=account)

    # Explicitly delete the local variable hot wallet from memory as soon as possible for security reasons
    del hot_wallet

    return xpriv_key


def get_private_key_from_wallet(account, index):
    """Derive the private key for the given account and index from the hot wallet."""
    xpriv_key = get_xpriv_key_from_wallet(account=account)
    return get_private_key(xpriv=xpriv_key, i=index)


def get_single_address_private_key(address):
    """Retrieve the private key for a single address stored directly in the hot wallet."""
    hot_wallet = get_hot_wallet()

    if address in hot_wallet:
        return {address: hot_wallet[address]}


def find_address_in_wallet(address, accounts=1, indexes=20):
    """Search the hot wallet for the given address across accounts and indexes."""
    hot_wallet = get_hot_wallet()

    for account in range(accounts):
        xpub_key = get_xpub_key(mnemonic=' '.join(hot_wallet['mnemonic']),
                                passphrase=hot_wallet['passphrase'],
                                account=account)

        addresses = get_addresses_from_xpub(xpub=xpub_key, i=indexes)

        if address in addresses:
            return account, addresses.index(address)

    return None, None


def find_single_address_in_wallet(address):
    """Check if a single address exists directly in the hot wallet."""
    hot_wallet = get_hot_wallet()

    return hot_wallet.get(address, None)


def hot_wallet_seed():
    """Derive the seed from the hot wallet mnemonic and passphrase."""
    hot_wallet = get_hot_wallet()
    return get_seed(mnemonic=' '.join(hot_wallet['mnemonic']), passphrase=hot_wallet['passphrase'])


def find_account_by_xpub(xpub, n=20):
    """Find the account index that matches the given xpub by scanning up to n accounts."""
    hot_wallet = get_hot_wallet()

    for i in range(n):
        account_xpub = get_xpub_key(mnemonic=' '.join(hot_wallet['mnemonic']),
                                    passphrase=hot_wallet['passphrase'],
                                    account=i)
        if xpub == account_xpub:
            return i
