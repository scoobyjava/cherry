"""
Configuration loader utility for benchmark configurations.
Implements Python best practices for handling JSON configuration files.
"""

import os
import json
import re
from typing import Dict, Any, Optional, Union, List
from pathlib import Path


class ConfigurationError(Exception):
    """Exception raised for configuration errors."""
    pass


class BenchmarkConfigLoader:
    """Loads and processes benchmark configuration files following Python best practices."""
    
    ENV_VAR_PATTERN = re.compile(r'\${([A-Za-z0-9_]+)}')
    
    def __init__(self, config_path: Union[str, Path]):
        """Initialize with path to config file."""
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        
    def load(self) -> Dict[str, Any]:
        """Load the configuration file with environment variable substitution."""
        if not self.config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {self.config_path}")
            
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration: {e}")
            
        # Process environment variables
        self._process_env_vars(self.config)
        return self.config
    
    def _process_env_vars(self, config_obj: Any) -> None:
        """Recursively process environment variables in the configuration."""
        if isinstance(config_obj, dict):
            for key, value in config_obj.items():
                if isinstance(value, (dict, list)):
                    self._process_env_vars(value)
                elif isinstance(value, str):
                    config_obj[key] = self._replace_env_vars(value)
        elif isinstance(config_obj, list):
            for i, item in enumerate(config_obj):
                if isinstance(item, (dict, list)):
                    self._process_env_vars(item)
                elif isinstance(item, str):
                    config_obj[i] = self._replace_env_vars(item)
    
    def _replace_env_vars(self, value: str) -> str:
        """Replace environment variables in a string."""
        if not isinstance(value, str):
            return value
            
        def replace_var(match):
            var_name = match.group(1)
            env_value = os.environ.get(var_name)
            if env_value is None:
                raise ConfigurationError(f"Environment variable not set: {var_name}")
            return env_value
            
        return self.ENV_VAR_PATTERN.sub(replace_var, value)
    
    def get_pinecone_config(self) -> Dict[str, Any]:
        """Get the Pinecone service configuration."""
        try:
            return self.config["app"]["services"]["pinecone"]
        except KeyError:
            raise ConfigurationError("Pinecone configuration not found")
    
    def get_postgres_config(self) -> Dict[str, Any]:
        """Get the PostgreSQL service configuration."""
        try:
            return self.config["app"]["services"]["postgres"]
        except KeyError:
            raise ConfigurationError("PostgreSQL configuration not found")
    
    def get_namespaces(self) -> Dict[str, Any]:
        """Get all Pinecone namespaces."""
        try:
            return self.config["app"]["services"]["pinecone"]["namespaces"]
        except KeyError:
            raise ConfigurationError("Pinecone namespaces not found")


# Example usage:
if __name__ == "__main__":
    loader = BenchmarkConfigLoader("benchmarks/benchmark_config.json")
    config = loader.load()
    print(f"Loaded configuration with {len(config.get('app', {}).get('services', {}))} services")
