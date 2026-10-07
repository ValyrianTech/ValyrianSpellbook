#!/usr/bin/env python3
"""
Authentication helpers for the Valyrian Spellbook Web UI
"""

import hmac
import os
import secrets
import sys
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


class SessionStore:
    """Thread-safe, in-memory store for server-side session credentials.

    Only an opaque session id is stored in the client cookie. The API key and
    secret are kept server-side in this store and looked up by that id, so the
    signed (not encrypted) session cookie never carries secrets.
    """

    def __init__(self):
        self._records: dict[str, dict] = {}
        self._lock = threading.Lock()

    def create(self, api_key: str, api_secret: str) -> str:
        """Store credentials and return an opaque session id."""
        session_id = secrets.token_urlsafe(32)
        record = {
            'api_key': api_key,
            'api_secret': api_secret,
            'created': time.time(),
        }
        with self._lock:
            self._records[session_id] = record
        return session_id

    def get(self, session_id: str | None) -> dict | None:
        """Return the stored record for ``session_id`` or None.

        Records older than ``SESSION_TTL_SECONDS`` are treated as expired,
        purged from the store, and reported as absent.
        """
        if not session_id:
            return None
        with self._lock:
            record = self._records.get(session_id)
            if record is None:
                return None
            if time.time() - record['created'] > SESSION_TTL_SECONDS:
                del self._records[session_id]
                return None
            return record

    def delete(self, session_id: str | None) -> None:
        """Remove the record for ``session_id`` (no-op if absent)."""
        if not session_id:
            return
        with self._lock:
            self._records.pop(session_id, None)


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
