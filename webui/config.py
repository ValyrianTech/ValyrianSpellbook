#!/usr/bin/env python3
"""
Configuration for the Valyrian Spellbook Web UI.

The session secret key is sourced from the ``SPELLBOOK_SESSION_SECRET``
environment variable when it is set and non-empty. Otherwise it is read from a
persisted file at ``<repo_root>/configuration/session_secret.key``, which is
generated on first access using ``secrets.token_hex(32)`` and then reused on
subsequent accesses. This keeps the key stable across process restarts and
shared across worker processes.

To generate a key manually::

    python -c 'import secrets; print(secrets.token_hex(32))'
"""

import os
import secrets
import sys
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.configurationhelpers import get_host, get_port

# Absolute path to the persisted session secret key file, rooted at the repo
# root (the parent directory of the ``webui/`` package).
SESSION_SECRET_KEY_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "configuration",
    "session_secret.key",
)


class Settings:
    """Application settings.

    The session secret key is sourced from the ``SPELLBOOK_SESSION_SECRET``
    environment variable when set and non-empty, otherwise from a persisted
    file at ``SESSION_SECRET_KEY_FILE`` (generated on first access). This makes
    the key stable across process restarts and shared across workers.
    """

    # Web UI server settings
    WEBUI_HOST: str = "0.0.0.0"
    WEBUI_PORT: int = 5001
    DEBUG: bool = True

    # Spellbook REST API settings (the existing Bottle server)
    @property
    def SPELLBOOK_API_HOST(self) -> str:
        """Return the Spellbook REST API host from configuration."""
        return get_host()

    @property
    def SPELLBOOK_API_PORT(self) -> int:
        """Return the Spellbook REST API port from configuration."""
        return get_port()

    @property
    def SPELLBOOK_API_URL(self) -> str:
        """Return the full Spellbook REST API URL."""
        return f"http://{self.SPELLBOOK_API_HOST}:{self.SPELLBOOK_API_PORT}"

    @property
    def SESSION_SECRET_KEY(self) -> str:
        """Return the session secret key.

        The key is sourced from the ``SPELLBOOK_SESSION_SECRET`` environment
        variable when set and non-empty. Otherwise it is read from the
        persisted file at ``SESSION_SECRET_KEY_FILE``, generating and writing a
        new ``secrets.token_hex(32)`` key (with permissions 0o600) on first
        access. First-time creation is atomic via ``os.O_CREAT | os.O_EXCL``,
        so concurrent workers cannot diverge on the key; if another process
        wins the race, its file is re-read instead, retrying a few times in
        case the winning process has not yet written the secret. The result is
        always a non-empty stripped string and is stable across process
        restarts and shared across workers.
        """
        env_secret = os.environ.get("SPELLBOOK_SESSION_SECRET")
        if env_secret:
            return env_secret

        key_file = SESSION_SECRET_KEY_FILE
        os.makedirs(os.path.dirname(key_file), exist_ok=True)

        try:
            fd = os.open(key_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            for _ in range(10):
                with open(key_file, "r") as key_file_handle:
                    secret = key_file_handle.read().strip()
                if secret:
                    return secret
                time.sleep(0.05)
            return secret

        secret = secrets.token_hex(32)
        with os.fdopen(fd, "w") as key_file_handle:
            key_file_handle.write(secret)
        os.chmod(key_file, 0o600)
        return secret


settings = Settings()
