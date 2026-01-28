#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard router - main pages and authentication
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from auth import is_authenticated, login_user, logout_user, get_api_client

router = APIRouter()

WEBUI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(WEBUI_DIR, "templates"))


@router.get("/")
async def index(request: Request):
    """Main dashboard page"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    
    # Get counts for dashboard
    triggers = client.get_triggers()
    actions = client.get_actions()
    llms = client.get_llms()
    explorers = client.get_explorers()
    
    # Check API health
    ping_result = client.ping()
    api_online = ping_result.get('success', False)
    
    # Get latest block info
    latest_block = client.get_latest_block()
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "trigger_count": len(triggers) if isinstance(triggers, list) else 0,
            "action_count": len(actions) if isinstance(actions, list) else 0,
            "llm_count": len(llms) if isinstance(llms, list) else 0,
            "explorer_count": len(explorers) if isinstance(explorers, list) else 0,
            "api_online": api_online,
            "latest_block": latest_block,
        }
    )


@router.get("/login")
async def login_page(request: Request):
    """Login page"""
    if is_authenticated(request):
        return RedirectResponse(url="/", status_code=303)
    
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None}
    )


@router.post("/login")
async def login(request: Request, api_key: str = Form(...), api_secret: str = Form(...)):
    """Handle login form submission"""
    if login_user(request, api_key, api_secret):
        return RedirectResponse(url="/", status_code=303)
    
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid API key or secret"}
    )


@router.get("/logout")
async def logout(request: Request):
    """Log out the user"""
    logout_user(request)
    return RedirectResponse(url="/login", status_code=303)
