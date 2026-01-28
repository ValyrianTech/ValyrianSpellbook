#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration for the Valyrian Spellbook Web UI
"""

import os
import secrets
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.configurationhelpers import get_host, get_port


class Settings:
    """Application settings"""
    
    # Web UI server settings
    WEBUI_HOST: str = "0.0.0.0"
    WEBUI_PORT: int = 5001
    DEBUG: bool = True
    
    # Session settings
    SESSION_SECRET_KEY: str = secrets.token_hex(32)
    
    # Spellbook REST API settings (the existing Bottle server)
    @property
    def SPELLBOOK_API_HOST(self) -> str:
        return get_host()
    
    @property
    def SPELLBOOK_API_PORT(self) -> int:
        return get_port()
    
    @property
    def SPELLBOOK_API_URL(self) -> str:
        return f"http://{self.SPELLBOOK_API_HOST}:{self.SPELLBOOK_API_PORT}"


settings = Settings()
