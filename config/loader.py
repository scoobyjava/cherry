import os
from typing import Dict, Any, List, Optional
from pathlib import Path

from .models import AppConfig
from .providers import ConfigProvider, EnvConfigProvider, FileConfigProvider


class ConfigLoader:
    """Loads and merges configuration from various sources"""
    
    def __init__(self):
        self.providers: List[ConfigProvider] = []
        
        # Default providers
        self._setup_default_providers()
    
    def _setup_default_providers(self):
        """Set up the default configuration providers"""
        # Look for config files in common locations
        config_paths = [
            os.path.join(os.getcwd(), "config.yaml"),
            os.path.join(os.getcwd(), "config.yml"),
            os.path.join(os.getcwd(), "config.json"),
            os.path.expanduser("~/.cherry/config.yaml"),
        ]
        
        # Add file providers for all potential config files
        for path in config_paths:
            if os.path.exists(path):
                self.providers.append(FileConfigProvider(path))
        
        # Always add environment variables provider last (highest priority)
        self.providers.append(EnvConfigProvider())
    
    def add_provider(self, provider: ConfigProvider) -> None:
        """Add a configuration provider"""
        self.providers.append(provider)
    
    def load_config(self) -> AppConfig:
        """Load and merge configuration from all providers"""
        # Start with an empty config dictionary
        config_dict: Dict[str, Any] = {}
        
        # Merge in configurations from all providers
        for provider in self.providers:
            provider_config = provider.get_config()
            config_dict = self._deep_merge(config_dict, provider_config)
        
        # Create a Pydantic model instance with the merged configuration
        # This also applies the defaults for any values not provided
        return AppConfig(**config_dict)
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two dictionaries, with override taking precedence"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # If both values are dictionaries, recursively merge them
                result[key] = self._deep_merge(result[key], value)
            else:
                # Otherwise, override takes precedence
                result[key] = value
                
        return result
