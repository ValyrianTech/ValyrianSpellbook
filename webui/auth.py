#!/usr/bin/env python3
"""
Authentication helpers for the Valyrian Spellbook Web UI
"""

import hmac
import json
import os
import secrets
import sys
import tempfile
import threading
import time
from functools import wraps

from fastapi import Request
from fastapi.responses import RedirectResponse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_client import SpellbookAPIClient

from helpers.configurationhelpers import get_key, get_secret

# How long a server-side session record remains valid (seconds).
SESSION_TTL_SECONDS = 86400

# Absolute path to the shared, on-disk session store directory, rooted at the
# repo root (the parent directory of the ``webui/`` package). Because records
# are stored as files here (rather than in process memory), they are visible
# across worker processes and survive restarts.
SESSION_STORE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "configuration",
    "webui_sessions",
)


def _session_file_path(directory: str, session_id: str) -> str:
    """Return the filesystem-safe path for a session record.

    Session ids come from ``secrets.token_urlsafe(32)``, but the id is hex
    encoded so the resulting filename is guaranteed to contain only characters
    that are safe in a filename and can never escape ``directory``.
    """
    encoded = session_id.encode("utf-8").hex()
    return os.path.join(directory, f"{encoded}.json")


class SessionStore:
    """Thread-safe, file-backed store for server-side session credentials.

    Only an opaque session id is stored in the client cookie. The API key and
    secret are kept server-side in this store and looked up by that id, so the
    signed (not encrypted) session cookie never carries secrets.

    Records are persisted as one JSON file per session id under ``directory``
    (created with mode 0o600), so they are visible across worker processes and
    survive restarts. Writes are atomic (a temporary file flushed/fsynced and
    moved into place with ``os.replace``), and cross-process reads tolerate
    files that disappear mid-read.
    """

    def __init__(self, directory: str = SESSION_STORE_DIR):
        self._directory = directory
        self._lock = threading.Lock()

    def create(self, api_key: str, api_secret: str) -> str:
        """Store credentials and return an opaque session id."""
        session_id = secrets.token_urlsafe(32)
        record = {
            'api_key': api_key,
            'api_secret': api_secret,
            'created': time.time(),
        }
        path = _session_file_path(self._directory, session_id)
        with self._lock:
            self._atomic_write(path, record)
        return session_id

    def _atomic_write(self, path: str, record: dict) -> None:
        """Atomically write ``record`` as JSON to ``path`` with mode 0o600.

        The record is written to a temporary file in the same directory (so
        that ``os.replace`` is atomic on the same filesystem), flushed and
        fsynced, chmod'd to 0o600, and then moved into place. On any failure
        the temporary file is removed before the original exception is
        re-raised.
        """
        directory = os.path.dirname(path)
        os.makedirs(directory, exist_ok=True)

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", dir=directory, delete=False) as tmp_file:
                tmp_path = tmp_file.name
                json.dump(record, tmp_file)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
            os.chmod(tmp_path, 0o600)
            os.replace(tmp_path, path)
        except OSError:
            if tmp_path is not None and os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

    def get(self, session_id: str | None) -> dict | None:
        """Return the stored record for ``session_id`` or None.

        Records older than ``SESSION_TTL_SECONDS`` are treated as expired,
        purged from the store, and reported as absent. A missing, unreadable,
        or corrupt record is reported as absent.
        """
        if not session_id:
            return None
        path = _session_file_path(self._directory, session_id)
        with self._lock:
            try:
                with open(path, "r") as session_file:
                    record = json.load(session_file)
            except FileNotFoundError:
                return None
            except (ValueError, OSError):
                return None
            if not isinstance(record, dict):
                return None
            created = record.get("created")
            if created is None or time.time() - created > SESSION_TTL_SECONDS:
                self._remove(path)
                return None
            return record

    def delete(self, session_id: str | None) -> None:
        """Remove the record for ``session_id`` (no-op if absent)."""
        if not session_id:
            return
        path = _session_file_path(self._directory, session_id)
        with self._lock:
            self._remove(path)

    def _remove(self, path: str) -> None:
        """Remove a session record file, tolerating a missing file (no-op)."""
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


# Module-level, process-wide session store.
_SESSION_STORE = SessionStore()


def get_api_client(request: Request) -> SpellbookAPIClient:
    """Get an API client from the server-side session store."""
    session_id = request.session.get('session_id')
    record = _SESSION_STORE.get(session_id)
    api_key = record['api_key'] if record else None
    api_secret = record['api_secret'] if record else None

    # Always return a client - credentials are optional for many endpoints
    return SpellbookAPIClient(api_key=api_key, api_secret=api_secret)


def is_authenticated(request: Request) -> bool:
    """Check if the user is authenticated"""
    return request.session.get('authenticated', False)


def require_auth(func):
    """Decorator to require authentication for a route"""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        """Check authentication before calling the wrapped route handler."""
        if not is_authenticated(request):
            return RedirectResponse(url="/login", status_code=303)
        return await func(request, *args, **kwargs)
    return wrapper


def validate_credentials(api_key: str, api_secret: str) -> bool:
    """
    Validate API credentials by checking against the configured keys.
    Returns True if credentials are valid.
    """
    configured_key = get_key()
    configured_secret = get_secret()

    key_matches = hmac.compare_digest(
        str(api_key).encode("utf-8"), str(configured_key).encode("utf-8")
    )
    secret_matches = hmac.compare_digest(
        str(api_secret).encode("utf-8"), str(configured_secret).encode("utf-8")
    )
    return key_matches and secret_matches


def login_user(request: Request, api_key: str, api_secret: str) -> bool:
    """
    Attempt to log in a user with the given credentials.
    Returns True if successful.
    """
    if validate_credentials(api_key, api_secret):
        session_id = _SESSION_STORE.create(api_key, api_secret)
        request.session['authenticated'] = True
        request.session['session_id'] = session_id
        return True
    return False


def logout_user(request: Request):
    """Log out the current user"""
    _SESSION_STORE.delete(request.session.get('session_id'))
    request.session.clear()
