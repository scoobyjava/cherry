import os
import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigProvider:
    """Base class for configuration providers"""
    
    def get_config(self) -> Dict[str, Any]:
        """Get configuration from this provider"""
        raise NotImplementedError()


class EnvConfigProvider(ConfigProvider):
    """Provider that loads config from environment variables"""
    
    def __init__(self, prefix: str = "CHERRY_"):
        self.prefix = prefix
    
    def get_config(self) -> Dict[str, Any]:
        config = {}
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                # Convert CHERRY_LLM_MODEL to llm.model
                path = key[len(self.prefix):].lower().split('_')
                
                # Handle nested config with dictionaries
                current = config
                for part in path[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Set the actual value
                # Try to convert to appropriate type
                value = self._convert_value(value)
                current[path[-1]] = value
        
        return config
    
    def _convert_value(self, value: str) -> Any:
        """Convert string values to appropriate types"""
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        return value


class FileConfigProvider(ConfigProvider):
    """Provider that loads config from a file"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def get_config(self) -> Dict[str, Any]:
        path = Path(self.file_path)
        if not path.exists():
            return {}
        
        with open(path, 'r') as f:
            if path.suffix.lower() == '.json':
                return json.load(f)
            elif path.suffix.lower() in ('.yml', '.yaml'):
                return yaml.safe_load(f)
            else:
                # Assume it's a JSON file if we can't determine the type
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    try:
                        return yaml.safe_load(f)
                    except yaml.YAMLError:
                        return {}
