#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication helpers for the Valyrian Spellbook Web UI
"""

import os
import sys
from functools import wraps
from typing import Optional

from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.configurationhelpers import get_key, get_secret
from api_client import SpellbookAPIClient


def get_api_client(request: Request) -> SpellbookAPIClient:
    """Get an API client from the session (with credentials if available)"""
    api_key = request.session.get('api_key')
    api_secret = request.session.get('api_secret')
    
    # Always return a client - credentials are optional for many endpoints
    return SpellbookAPIClient(api_key=api_key, api_secret=api_secret)


def is_authenticated(request: Request) -> bool:
    """Check if the user is authenticated"""
    return request.session.get('authenticated', False)


def require_auth(func):
    """Decorator to require authentication for a route"""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
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
    
    return api_key == configured_key and api_secret == configured_secret


def login_user(request: Request, api_key: str, api_secret: str) -> bool:
    """
    Attempt to log in a user with the given credentials.
    Returns True if successful.
    """
    if validate_credentials(api_key, api_secret):
        request.session['authenticated'] = True
        request.session['api_key'] = api_key
        request.session['api_secret'] = api_secret
        return True
    return False


def logout_user(request: Request):
    """Log out the current user"""
    request.session.clear()
