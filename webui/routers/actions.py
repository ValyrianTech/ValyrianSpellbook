#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Actions router - manage actions
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from auth import is_authenticated, get_api_client

router = APIRouter()

WEBUI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(WEBUI_DIR, "templates"))


@router.get("/")
async def list_actions(request: Request):
    """List all actions"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    actions = client.get_actions() if client else []
    
    # Get detailed info for each action
    action_details = []
    if isinstance(actions, list):
        for action_id in actions:
            config = client.get_action_config(action_id)
            if not isinstance(config, dict) or 'error' not in config:
                action_details.append({
                    'id': action_id,
                    'config': config
                })
    
    return templates.TemplateResponse(
        "actions/list.html",
        {
            "request": request,
            "actions": action_details,
        }
    )


@router.get("/new")
async def new_action(request: Request):
    """New action form"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    return templates.TemplateResponse(
        "actions/form.html",
        {
            "request": request,
            "action": None,
            "action_id": None,
            "is_new": True,
        }
    )


@router.get("/{action_id}")
async def view_action(request: Request, action_id: str):
    """View a specific action"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    action = client.get_action_config(action_id) if client else {}
    
    return templates.TemplateResponse(
        "actions/view.html",
        {
            "request": request,
            "action": action,
            "action_id": action_id,
        }
    )


@router.get("/{action_id}/edit")
async def edit_action(request: Request, action_id: str):
    """Edit action form"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    action = client.get_action_config(action_id) if client else {}
    
    return templates.TemplateResponse(
        "actions/form.html",
        {
            "request": request,
            "action": action,
            "action_id": action_id,
            "is_new": False,
        }
    )


@router.post("/{action_id}/save")
async def save_action(request: Request, action_id: str):
    """Save action configuration"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    form_data = await request.form()
    
    # Build config from form data
    config = {}
    for key, value in form_data.items():
        if value:  # Only include non-empty values
            config[key] = value
    
    result = client.save_action(action_id, config) if client else {'error': 'Not authenticated'}
    
    if 'error' in result:
        return templates.TemplateResponse(
            "actions/form.html",
            {
                "request": request,
                "action": config,
                "action_id": action_id,
                "is_new": False,
                "error": result.get('error'),
            }
        )
    
    return RedirectResponse(url=f"/actions/{action_id}", status_code=303)


@router.post("/{action_id}/delete")
async def delete_action(request: Request, action_id: str):
    """Delete an action"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    client.delete_action(action_id) if client else None
    
    return RedirectResponse(url="/actions", status_code=303)


@router.post("/{action_id}/run")
async def run_action(request: Request, action_id: str):
    """Run an action"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    result = client.run_action(action_id) if client else {'error': 'Not authenticated'}
    
    return RedirectResponse(url=f"/actions/{action_id}", status_code=303)
