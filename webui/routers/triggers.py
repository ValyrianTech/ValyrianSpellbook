#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Triggers router - manage triggers
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
async def list_triggers(request: Request):
    """List all triggers"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    triggers = client.get_triggers() if client else []
    
    # Get detailed info for each trigger
    trigger_details = []
    if isinstance(triggers, list):
        for trigger_id in triggers:
            config = client.get_trigger_config(trigger_id)
            if not isinstance(config, dict) or 'error' not in config:
                trigger_details.append({
                    'id': trigger_id,
                    'config': config
                })
    
    return templates.TemplateResponse(
        "triggers/list.html",
        {
            "request": request,
            "triggers": trigger_details,
        }
    )


@router.get("/new")
async def new_trigger(request: Request):
    """New trigger form"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    return templates.TemplateResponse(
        "triggers/form.html",
        {
            "request": request,
            "trigger": None,
            "trigger_id": None,
            "is_new": True,
        }
    )


@router.get("/{trigger_id}")
async def view_trigger(request: Request, trigger_id: str):
    """View a specific trigger"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    trigger = client.get_trigger_config(trigger_id) if client else {}
    
    return templates.TemplateResponse(
        "triggers/view.html",
        {
            "request": request,
            "trigger": trigger,
            "trigger_id": trigger_id,
        }
    )


@router.get("/{trigger_id}/edit")
async def edit_trigger(request: Request, trigger_id: str):
    """Edit trigger form"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    trigger = client.get_trigger_config(trigger_id) if client else {}
    
    return templates.TemplateResponse(
        "triggers/form.html",
        {
            "request": request,
            "trigger": trigger,
            "trigger_id": trigger_id,
            "is_new": False,
        }
    )


@router.post("/{trigger_id}/save")
async def save_trigger(request: Request, trigger_id: str):
    """Save trigger configuration"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    form_data = await request.form()
    
    # Build config from form data
    config = {}
    for key, value in form_data.items():
        if value:  # Only include non-empty values
            config[key] = value
    
    result = client.save_trigger(trigger_id, config) if client else {'error': 'Not authenticated'}
    
    if 'error' in result:
        return templates.TemplateResponse(
            "triggers/form.html",
            {
                "request": request,
                "trigger": config,
                "trigger_id": trigger_id,
                "is_new": False,
                "error": result.get('error'),
            }
        )
    
    return RedirectResponse(url=f"/triggers/{trigger_id}", status_code=303)


@router.post("/{trigger_id}/delete")
async def delete_trigger(request: Request, trigger_id: str):
    """Delete a trigger"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    client.delete_trigger(trigger_id) if client else None
    
    return RedirectResponse(url="/triggers", status_code=303)


@router.post("/{trigger_id}/activate")
async def activate_trigger(request: Request, trigger_id: str):
    """Manually activate a trigger"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    result = client.activate_trigger(trigger_id) if client else {'error': 'Not authenticated'}
    
    return RedirectResponse(url=f"/triggers/{trigger_id}", status_code=303)


@router.post("/{trigger_id}/check")
async def check_trigger(request: Request, trigger_id: str):
    """Check a trigger"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    result = client.check_trigger(trigger_id) if client else {'error': 'Not authenticated'}
    
    return RedirectResponse(url=f"/triggers/{trigger_id}", status_code=303)
