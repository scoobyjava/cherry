import json
import os
import re

def resolve_env_vars(value):
    """Resolve environment variables or secrets in config values"""
    if not isinstance(value, str):
        return value
        
    # Handle ${SECRET:NAME:env_var} or ${SECRET:NAME} pattern
    secret_pattern = r'\${SECRET:([^:}]+)(?::([^}]+))?}'
    matches = re.findall(secret_pattern, value)
    
    if matches:
        for match in matches:
            secret_name, secret_type = match
            # In a real-world scenario, we'd handle secrets differently
            # For benchmarks, just use environment variables
            env_value = os.environ.get(secret_name, '')
            if not env_value and secret_name:
                print(f"Warning: Environment variable {secret_name} not found")
            value = value.replace(f"${{SECRET:{secret_name}{':' + secret_type if secret_type else ''}}}", env_value)
    
    return value

def process_config_values(config):
    """Process all values in the config recursively"""
    if isinstance(config, dict):
        return {k: process_config_values(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [process_config_values(v) for v in config]
    else:
        return resolve_env_vars(config)

def load_config():
    """Load benchmark configuration from file"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'benchmark_config.json')
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")
        
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Process environment variables and secrets
    processed_config = process_config_values(config)
    
    return processed_config
