#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blockchain router - view blockchain data
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
async def blockchain_index(request: Request):
    """Blockchain data overview"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    latest_block = client.get_latest_block() if client else {}
    
    return templates.TemplateResponse(
        "blockchain/index.html",
        {
            "request": request,
            "latest_block": latest_block,
        }
    )


@router.get("/block/{block_id}")
async def view_block(request: Request, block_id: str):
    """View a specific block"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    
    # Try to parse as height first
    try:
        height = int(block_id)
        block = client.get_block_by_height(height) if client else {}
    except ValueError:
        # It's a hash
        block = client.get_block_by_hash(block_id) if client else {}
    
    return templates.TemplateResponse(
        "blockchain/block.html",
        {
            "request": request,
            "block": block,
            "block_id": block_id,
        }
    )


@router.get("/tx/{txid}")
async def view_transaction(request: Request, txid: str):
    """View a specific transaction"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    transaction = client.get_transaction(txid) if client else {}
    prime_input = client.get_prime_input_address(txid) if client else {}
    
    return templates.TemplateResponse(
        "blockchain/transaction.html",
        {
            "request": request,
            "transaction": transaction,
            "prime_input": prime_input,
            "txid": txid,
        }
    )


@router.get("/address/{address}")
async def view_address(request: Request, address: str):
    """View address details"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    client = get_api_client(request)
    balance = client.get_balance(address) if client else {}
    transactions = client.get_transactions(address) if client else {}
    utxos = client.get_utxos(address) if client else {}
    
    return templates.TemplateResponse(
        "blockchain/address.html",
        {
            "request": request,
            "address": address,
            "balance": balance,
            "transactions": transactions,
            "utxos": utxos,
        }
    )


@router.post("/search")
async def search(request: Request, query: str = Form(...)):
    """Search for block, transaction, or address"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    
    query = query.strip()
    
    # Determine what type of query this is
    if len(query) == 64:
        # Could be a txid or block hash - try transaction first
        return RedirectResponse(url=f"/blockchain/tx/{query}", status_code=303)
    elif query.isdigit():
        # Block height
        return RedirectResponse(url=f"/blockchain/block/{query}", status_code=303)
    else:
        # Assume it's an address
        return RedirectResponse(url=f"/blockchain/address/{query}", status_code=303)
