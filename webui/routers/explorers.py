#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Explorers router - manage block explorer configurations
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
async def list_explorers(request: Request):
    """List all explorers"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    explorers = client.get_explorers() if client else []
    
    # Get detailed info for each explorer
    explorer_details = []
    if isinstance(explorers, list):
        for explorer_id in explorers:
            config = client.get_explorer_config(explorer_id)
            if not isinstance(config, dict) or 'error' not in config:
                explorer_details.append({
                    'id': explorer_id,
                    'config': config
                })
    
    return templates.TemplateResponse(
        "explorers/list.html",
        {
            "request": request,
            "explorers": explorer_details,
        }
    )


@router.get("/new")
async def new_explorer(request: Request):
    """New explorer form"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    return templates.TemplateResponse(
        "explorers/form.html",
        {
            "request": request,
            "explorer": None,
            "explorer_id": None,
            "is_new": True,
        }
    )


@router.get("/{explorer_id}")
async def view_explorer(request: Request, explorer_id: str):
    """View a specific explorer"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    explorer = client.get_explorer_config(explorer_id) if client else {}
    
    return templates.TemplateResponse(
        "explorers/view.html",
        {
            "request": request,
            "explorer": explorer,
            "explorer_id": explorer_id,
        }
    )


@router.get("/{explorer_id}/edit")
async def edit_explorer(request: Request, explorer_id: str):
    """Edit explorer form"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    explorer = client.get_explorer_config(explorer_id) if client else {}
    
    return templates.TemplateResponse(
        "explorers/form.html",
        {
            "request": request,
            "explorer": explorer,
            "explorer_id": explorer_id,
            "is_new": False,
        }
    )


@router.post("/{explorer_id}/save")
async def save_explorer(request: Request, explorer_id: str):
    """Save explorer configuration"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    form_data = await request.form()
    
    # Build config from form data
    config = {}
    for key, value in form_data.items():
        if value:  # Only include non-empty values
            config[key] = value
    
    result = client.save_explorer(explorer_id, config) if client else {'error': 'Not authenticated'}
    
    if 'error' in result:
        return templates.TemplateResponse(
            "explorers/form.html",
            {
                "request": request,
                "explorer": config,
                "explorer_id": explorer_id,
                "is_new": False,
                "error": result.get('error'),
            }
        )
    
    return RedirectResponse(url=f"/explorers/{explorer_id}", status_code=303)


@router.post("/{explorer_id}/delete")
async def delete_explorer(request: Request, explorer_id: str):
    """Delete an explorer"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    client.delete_explorer(explorer_id) if client else None
    
    return RedirectResponse(url="/explorers", status_code=303)
