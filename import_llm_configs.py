#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import LLM configurations from preconfigured_llm_models.csv into the Valyrian Spellbook.

This script reads the CSV file containing pre-configured LLM models and makes API calls
to the SaveLLMConfig endpoint to bulk import them into the system.
"""

import os
import sys
import csv
import json
import argparse
import requests
from typing import Dict, Any, Optional

# Add the current directory to the path to import Spellbook modules
sys.path.append(os.path.dirname(__file__))
from helpers.configurationhelpers import get_host, get_port
from helpers.messagehelpers import sign_data


def parse_price(price_str: str) -> float:
    """Parse price string like '$2.00' to float 2.0"""
    if not price_str or price_str.strip() == '':
        return 0.0
    
    # Remove dollar sign and convert to float
    try:
        return float(price_str.replace('$', '').replace(',', ''))
    except (ValueError, AttributeError):
        return 0.0


def parse_context_size(context_str: str) -> int:
    """Parse context size string to integer"""
    if not context_str or context_str.strip() == '':
        return 4096  # Default context size
    
    try:
        # Remove any commas and convert to int
        return int(context_str.replace(',', ''))
    except (ValueError, AttributeError):
        return 4096


def parse_vision_capability(vision_str: str) -> bool:
    """Parse vision capability string to boolean"""
    if not vision_str or vision_str.strip() == '':
        return False
    
    return vision_str.lower() in ['true', 'yes', '1', 'enabled']


def create_llm_config(model_data: Dict[str, str], api_key: str = '') -> Dict[str, Any]:
    """Create LLM configuration dictionary from CSV row data"""
    provider = model_data['Provider']
    model_name = model_data['Model_name']
    input_price = parse_price(model_data['Input_Price'])
    output_price = parse_price(model_data['Output_Price'])
    context_size = parse_context_size(model_data['Context Size'])
    vision = parse_vision_capability(model_data['Vision'])
    
    # CSV prices are per million tokens, so use them directly with 1M multiplier
    prompt_tokens_cost = input_price
    completion_tokens_cost = output_price
    
    config = {
        'llm_name': f'{provider}:{model_name}',
        'llm_host': '',
        'llm_port': None,  # Not needed for cloud providers
        'llm_server_type': provider,  # Use provider from CSV (e.g., 'OpenAI')
        'llm_model_name': model_name,
        'llm_description': f'{provider} {model_name} model',
        'prompt_tokens_cost': prompt_tokens_cost,
        'prompt_tokens_multiplier': 1000000,  # Prices are per 1M tokens
        'completion_tokens_cost': completion_tokens_cost,
        'completion_tokens_multiplier': 1000000,  # Prices are per 1M tokens
        'allow_auto_routing': True,
        'api_key': api_key,
        'vision': vision,
        'audio': 'audio' in model_name.lower(),  # Detect audio models
        'video': False,  # No video models in current CSV
        'context_length': context_size,
        'prompt_template': '',
        'chat': True  # All modern LLM models support chat format
    }
    
    return config


def save_llm_config_via_api(config: Dict[str, Any], host: str, port: int, verbose: bool = False) -> bool:
    """Save LLM configuration via API call to SaveLLMConfig endpoint"""
    url = f'http://{host}:{port}/api/SaveLLMConfig/message'
    
    # Sign the data for authentication
    signed_data = sign_data(message_data=config, account=0, index=0)
    
    if verbose:
        print(f"Saving LLM config: {config['llm_name']}")
        print(f"URL: {url}")
        print(f"Input cost: ${config['prompt_tokens_cost']:.2f}/1M tokens")
        print(f"Output cost: ${config['completion_tokens_cost']:.2f}/1M tokens")
    
    try:
        response = requests.post(url, json=signed_data, timeout=30)
        
        if verbose:
            print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success', False):
                print(f"✓ Successfully saved: {config['llm_name']}")
                return True
            else:
                print(f"✗ API returned success=False for: {config['llm_name']}")
                if verbose:
                    print(f"Response: {json.dumps(result, indent=2)}")
                return False
        else:
            print(f"✗ HTTP {response.status_code} error for: {config['llm_name']}")
            if verbose:
                print(f"Response text: {response.text}")
            return False
            
    except Exception as ex:
        print(f"✗ Exception saving {config['llm_name']}: {ex}")
        return False


def read_csv_models(csv_file_path: str) -> list:
    """Read and parse the CSV file containing LLM model data"""
    models = []
    
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                models.append(row)
        
        print(f"Read {len(models)} models from {csv_file_path}")
        return models
        
    except FileNotFoundError:
        print(f"Error: CSV file not found: {csv_file_path}")
        return []
    except Exception as ex:
        print(f"Error reading CSV file: {ex}")
        return []


def main():
    parser = argparse.ArgumentParser(description='Import LLM configurations from CSV file')
    parser.add_argument('--csv-file', 
                       default='preconfigured_llm_models.csv',
                       help='Path to CSV file (default: preconfigured_llm_models.csv)')
    parser.add_argument('--api-key', 
                       default='',
                       help='OpenAI API key to use for all models')
    parser.add_argument('--host', 
                       default=None,
                       help='Spellbook server host (default: from config)')
    parser.add_argument('--port', 
                       default=None,
                       type=int,
                       help='Spellbook server port (default: from config)')
    parser.add_argument('--dry-run', 
                       action='store_true',
                       help='Show what would be imported without actually doing it')
    parser.add_argument('--verbose', '-v', 
                       action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--filter', 
                       default='',
                       help='Only import models containing this string in the name')
    
    args = parser.parse_args()
    
    # Get host and port from configuration if not provided
    host = args.host if args.host else get_host()
    port = args.port if args.port else get_port()
    
    print(f"Valyrian Spellbook LLM Config Import Tool")
    print(f"Target server: {host}:{port}")
    print(f"CSV file: {args.csv_file}")
    if args.dry_run:
        print("DRY RUN MODE - No actual changes will be made")
    print("-" * 50)
    
    # Resolve CSV file path relative to script directory if not absolute
    if not os.path.isabs(args.csv_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_dir, args.csv_file)
    else:
        csv_file_path = args.csv_file
    
    # Read CSV data
    models = read_csv_models(csv_file_path)
    if not models:
        print("No models to import. Exiting.")
        return 1
    
    # Filter models if requested
    if args.filter:
        original_count = len(models)
        models = [m for m in models if args.filter.lower() in m['Model_name'].lower()]
        print(f"Filtered to {len(models)} models (from {original_count}) containing '{args.filter}'")
    
    # Process each model
    success_count = 0
    total_count = len(models)
    
    for i, model_data in enumerate(models, 1):
        print(f"\n[{i}/{total_count}] Processing: {model_data['Model_name']}")
        
        # Create configuration
        try:
            config = create_llm_config(model_data, args.api_key)
        except Exception as ex:
            print(f"✗ Error creating config for {model_data['Model_name']}: {ex}")
            continue
        
        if args.verbose:
            print(f"Config: {json.dumps(config, indent=2)}")
        
        if args.dry_run:
            print(f"Would save: {config['llm_name']}")
            print(f"  Input: ${config['prompt_tokens_cost']:.2f}/1M tokens")
            print(f"  Output: ${config['completion_tokens_cost']:.2f}/1M tokens")
            print(f"  Context: {config['context_length']} tokens")
            print(f"  Vision: {config['vision']}")
            success_count += 1
        else:
            # Save via API
            if save_llm_config_via_api(config, host, port, args.verbose):
                success_count += 1
    
    # Summary
    print(f"\n" + "=" * 50)
    if args.dry_run:
        print(f"DRY RUN COMPLETE: Would have imported {success_count}/{total_count} models")
    else:
        print(f"IMPORT COMPLETE: Successfully imported {success_count}/{total_count} models")
        if success_count < total_count:
            print(f"Failed to import {total_count - success_count} models")
    
    return 0 if success_count == total_count else 1


if __name__ == '__main__':
    sys.exit(main())
