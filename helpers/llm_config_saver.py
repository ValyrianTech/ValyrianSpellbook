#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lightweight LLM configuration saver module.

This module provides a minimal interface for saving LLM configurations
without importing heavy dependencies that create background threads.
"""

import os
import json
from typing import Dict, Any


def load_from_json_file(filename: str) -> Dict[str, Any]:
    """Load data from a JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_to_json_file(data: Dict[str, Any], filename: str) -> None:
    """Save data to a JSON file."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_llms_file_path() -> str:
    """Get the path to the LLMs.json configuration file."""
    return os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        '..', 
        'configuration', 
        'LLMs.json'
    )


def load_llms() -> Dict[str, Any]:
    """Load LLM configurations from the JSON file."""
    llms_file = get_llms_file_path()
    return load_from_json_file(llms_file) if os.path.exists(llms_file) else {}


def save_llm_config_lightweight(llm_name: str, llm_config: Dict[str, Any]) -> None:
    """
    Save LLM configuration to the JSON file.
    
    This is a lightweight version that only handles JSON operations
    without importing heavy LLM client libraries or websocket helpers.
    """
    llms_data = load_llms()
    
    # Prevent masked api_key to override existing api_key
    if llm_config.get('api_key', None) == '********':
        existing_api_key = llms_data.get(llm_name, {}).get('api_key', None)
        llm_config['api_key'] = existing_api_key
    
    # if host ends with a trailing /, remove it
    if llm_config.get('host') is not None and llm_config['host'].endswith('/'):
        llm_config['host'] = llm_config['host'][:-1]
    
    llms_data[llm_name] = llm_config
    
    save_to_json_file(data=llms_data, filename=get_llms_file_path())


def get_llm_config_lightweight(llm_name: str) -> Dict[str, Any]:
    """Get LLM configuration from the JSON file."""
    llms_data = load_llms()
    return llms_data.get(llm_name, {})


def delete_llm_lightweight(llm_name: str) -> bool:
    """Delete LLM configuration from the JSON file."""
    llms_data = load_llms()
    if llm_name in llms_data:
        del llms_data[llm_name]
        save_to_json_file(data=llms_data, filename=get_llms_file_path())
        return True
    return False
