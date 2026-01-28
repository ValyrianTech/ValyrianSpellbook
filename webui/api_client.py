#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Client for communicating with the Valyrian Spellbook REST API (Bottle server)
"""

import time
import requests
from typing import Optional, Dict, Any, List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from authentication import signature
from config import settings


class SpellbookAPIClient:
    """Client for the Spellbook REST API"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.base_url = settings.SPELLBOOK_API_URL
        self.api_key = api_key
        self.api_secret = api_secret
    
    def _get_auth_headers(self, data: Optional[Dict] = None) -> Dict[str, str]:
        """Generate authentication headers"""
        if not self.api_key or not self.api_secret:
            return {}
        
        nonce = int(round(time.time() * 1000))
        return {
            'Content-Type': 'application/json',
            'API_Key': self.api_key,
            'API_Sign': signature(data, nonce, self.api_secret),
            'API_Nonce': str(nonce)
        }
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                 authenticate: bool = False) -> Dict[str, Any]:
        """Make a request to the API"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_auth_headers(data) if authenticate else {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, json=data, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    # ==================== Health ====================
    
    def ping(self) -> Dict:
        """Check if the API is online"""
        return self._request('GET', '/spellbook/ping')
    
    # ==================== LLMs ====================
    
    def get_llms(self) -> List[str]:
        """Get list of configured LLMs"""
        return self._request('GET', '/spellbook/llms')
    
    def get_llm_config(self, llm_id: str) -> Dict:
        """Get configuration for a specific LLM"""
        return self._request('GET', f'/spellbook/llms/{llm_id}')
    
    def save_llm_config(self, llm_id: str, config: Dict) -> Dict:
        """Save or update an LLM configuration"""
        return self._request('POST', f'/spellbook/llms/{llm_id}', data=config, authenticate=True)
    
    def delete_llm(self, llm_id: str) -> Dict:
        """Delete an LLM configuration"""
        return self._request('DELETE', f'/spellbook/llms/{llm_id}', authenticate=True)
    
    # ==================== Explorers ====================
    
    def get_explorers(self) -> List[str]:
        """Get list of configured explorers"""
        return self._request('GET', '/spellbook/explorers')
    
    def get_explorer_config(self, explorer_id: str) -> Dict:
        """Get configuration for a specific explorer"""
        return self._request('GET', f'/spellbook/explorers/{explorer_id}', authenticate=True)
    
    def save_explorer(self, explorer_id: str, config: Dict) -> Dict:
        """Save or update an explorer configuration"""
        return self._request('POST', f'/spellbook/explorers/{explorer_id}', data=config, authenticate=True)
    
    def delete_explorer(self, explorer_id: str) -> Dict:
        """Delete an explorer configuration"""
        return self._request('DELETE', f'/spellbook/explorers/{explorer_id}', authenticate=True)
    
    # ==================== Triggers ====================
    
    def get_triggers(self) -> List[str]:
        """Get list of configured triggers"""
        return self._request('GET', '/spellbook/triggers')
    
    def get_trigger_config(self, trigger_id: str) -> Dict:
        """Get configuration for a specific trigger"""
        return self._request('GET', f'/spellbook/triggers/{trigger_id}', authenticate=True)
    
    def save_trigger(self, trigger_id: str, config: Dict) -> Dict:
        """Save or update a trigger configuration"""
        return self._request('POST', f'/spellbook/triggers/{trigger_id}', data=config, authenticate=True)
    
    def delete_trigger(self, trigger_id: str) -> Dict:
        """Delete a trigger configuration"""
        return self._request('DELETE', f'/spellbook/triggers/{trigger_id}', authenticate=True)
    
    def activate_trigger(self, trigger_id: str) -> Dict:
        """Manually activate a trigger"""
        return self._request('GET', f'/spellbook/triggers/{trigger_id}/activate', authenticate=True)
    
    def check_trigger(self, trigger_id: str) -> Dict:
        """Check a specific trigger"""
        return self._request('GET', f'/spellbook/triggers/{trigger_id}/check', authenticate=True)
    
    def check_all_triggers(self) -> Dict:
        """Check all triggers"""
        return self._request('GET', '/spellbook/check_triggers', authenticate=True)
    
    # ==================== Actions ====================
    
    def get_actions(self) -> List[str]:
        """Get list of configured actions"""
        return self._request('GET', '/spellbook/actions')
    
    def get_action_config(self, action_id: str) -> Dict:
        """Get configuration for a specific action"""
        return self._request('GET', f'/spellbook/actions/{action_id}', authenticate=True)
    
    def save_action(self, action_id: str, config: Dict) -> Dict:
        """Save or update an action configuration"""
        return self._request('POST', f'/spellbook/actions/{action_id}', data=config, authenticate=True)
    
    def delete_action(self, action_id: str) -> Dict:
        """Delete an action configuration"""
        return self._request('DELETE', f'/spellbook/actions/{action_id}', authenticate=True)
    
    def run_action(self, action_id: str) -> Dict:
        """Run a specific action"""
        return self._request('GET', f'/spellbook/actions/{action_id}/run', authenticate=True)
    
    def get_reveal(self, action_id: str) -> Dict:
        """Get revealed secret from a RevealSecret action"""
        return self._request('GET', f'/spellbook/actions/{action_id}/reveal')
    
    # ==================== Blockchain ====================
    
    def get_latest_block(self) -> Dict:
        """Get the latest block"""
        return self._request('GET', '/spellbook/blocks/latest')
    
    def get_block_by_height(self, height: int) -> Dict:
        """Get a block by height"""
        return self._request('GET', f'/spellbook/blocks/{height}')
    
    def get_block_by_hash(self, block_hash: str) -> Dict:
        """Get a block by hash"""
        return self._request('GET', f'/spellbook/blocks/{block_hash}')
    
    def get_transaction(self, txid: str) -> Dict:
        """Get a transaction by txid"""
        return self._request('GET', f'/spellbook/transactions/{txid}')
    
    def get_prime_input_address(self, txid: str) -> Dict:
        """Get the prime input address of a transaction"""
        return self._request('GET', f'/spellbook/transactions/{txid}/prime_input')
    
    def get_balance(self, address: str) -> Dict:
        """Get the balance of an address"""
        return self._request('GET', f'/spellbook/addresses/{address}/balance')
    
    def get_transactions(self, address: str) -> Dict:
        """Get transactions for an address"""
        return self._request('GET', f'/spellbook/addresses/{address}/transactions')
    
    def get_utxos(self, address: str, confirmations: int = 1) -> Dict:
        """Get UTXOs for an address"""
        return self._request('GET', f'/spellbook/addresses/{address}/utxos?confirmations={confirmations}')
    
    # ==================== Logs ====================
    
    def get_logs(self, filter_string: str = "") -> Dict:
        """Get log messages"""
        return self._request('GET', f'/spellbook/logs/{filter_string}', authenticate=True)
