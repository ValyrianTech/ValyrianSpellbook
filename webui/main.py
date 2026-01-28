#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Valyrian Spellbook Web UI - FastAPI Application

A web-based admin dashboard for managing the Valyrian Spellbook.
Runs alongside the existing Bottle REST API server.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from config import settings
from routers import dashboard, triggers, actions, llms, explorers, blockchain

# Create FastAPI app
app = FastAPI(
    title="Valyrian Spellbook Admin",
    description="Web UI for managing the Valyrian Spellbook",
    version="1.0.0"
)

# Add session middleware for authentication
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    session_cookie="spellbook_session",
    max_age=86400  # 24 hours
)

# Mount static files
WEBUI_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(WEBUI_DIR, "static")), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory=os.path.join(WEBUI_DIR, "templates"))

# Include routers
app.include_router(dashboard.router)
app.include_router(triggers.router, prefix="/triggers", tags=["triggers"])
app.include_router(actions.router, prefix="/actions", tags=["actions"])
app.include_router(llms.router, prefix="/llms", tags=["llms"])
app.include_router(explorers.router, prefix="/explorers", tags=["explorers"])
app.include_router(blockchain.router, prefix="/blockchain", tags=["blockchain"])


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(
        "errors/404.html",
        {"request": request},
        status_code=404
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return templates.TemplateResponse(
        "errors/500.html",
        {"request": request, "error": str(exc)},
        status_code=500
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.WEBUI_HOST,
        port=settings.WEBUI_PORT,
        reload=settings.DEBUG
    )
