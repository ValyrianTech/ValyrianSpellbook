#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLMs router - manage LLM configurations
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
async def list_llms(request: Request):
    """List all LLMs"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    llms = client.get_llms() if client else []
    
    # Get detailed info for each LLM
    llm_details = []
    if isinstance(llms, list):
        for llm_id in llms:
            config = client.get_llm_config(llm_id)
            if not isinstance(config, dict) or 'error' not in config:
                llm_details.append({
                    'id': llm_id,
                    'config': config
                })
    
    return templates.TemplateResponse(
        "llms/list.html",
        {
            "request": request,
            "llms": llm_details,
        }
    )


@router.get("/new")
async def new_llm(request: Request):
    """New LLM form"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    return templates.TemplateResponse(
        "llms/form.html",
        {
            "request": request,
            "llm": None,
            "llm_id": None,
            "is_new": True,
        }
    )


@router.get("/{llm_id:path}")
async def view_llm(request: Request, llm_id: str):
    """View a specific LLM"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    # Handle edit route
    if llm_id.endswith("/edit"):
        llm_id = llm_id[:-5]
        client = get_api_client(request)
        llm = client.get_llm_config(llm_id) if client else {}
        
        return templates.TemplateResponse(
            "llms/form.html",
            {
                "request": request,
                "llm": llm,
                "llm_id": llm_id,
                "is_new": False,
            }
        )
    
    client = get_api_client(request)
    llm = client.get_llm_config(llm_id) if client else {}
    
    return templates.TemplateResponse(
        "llms/view.html",
        {
            "request": request,
            "llm": llm,
            "llm_id": llm_id,
        }
    )


@router.post("/{llm_id:path}/save")
async def save_llm(request: Request, llm_id: str):
    """Save LLM configuration"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    form_data = await request.form()
    
    # Build config from form data
    config = {}
    for key, value in form_data.items():
        if value:  # Only include non-empty values
            config[key] = value
    
    result = client.save_llm_config(llm_id, config) if client else {'error': 'Not authenticated'}
    
    if isinstance(result, dict) and 'error' in result:
        return templates.TemplateResponse(
            "llms/form.html",
            {
                "request": request,
                "llm": config,
                "llm_id": llm_id,
                "is_new": False,
                "error": result.get('error'),
            }
        )
    
    return RedirectResponse(url=f"/llms/{llm_id}", status_code=303)


@router.post("/{llm_id:path}/delete")
async def delete_llm(request: Request, llm_id: str):
    """Delete an LLM"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    client.delete_llm(llm_id) if client else None
    
    return RedirectResponse(url="/llms", status_code=303)
