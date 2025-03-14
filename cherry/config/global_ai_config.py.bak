import os
import json
import logging
import yaml
from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class AIConfigPolicy:
    """
    Defines cross-tool AI policies and preferences at a global level.
    """

    # Defines priorities, fallback tools, and which are disabled by default per language
    TOOL_PRIORITY = {
        'python': {
            'primary': 'Tabnine',
            'fallback': 'Codeium',
            'disabled': ['Copilot']
        },
        'typescript': {
            'primary': 'Copilot',
            'fallback': 'Tabnine',
            'disabled': []
        },
        'java': {
            'primary': 'Copilot',
            'fallback': 'Tabnine',
            'disabled': ['Codeium']
        },
        'javascript': {
            'primary': 'Cody',
            'fallback': 'Copilot',
            'disabled': []
        },
        'default': {
            'primary': 'Cody',
            'fallback': 'Tabnine',
            'disabled': []
        }
    }

    # Context rules for different file types
    CONTEXT_RULES = {
        'deep_context': {
            'extensions': ['.py', '.js', '.ts', '.tsx', '.jsx'],
            'window_size': 2048,
            'cross_file_links': True
        },
        'medium_context': {
            'extensions': ['.java', '.c', '.cpp', '.cs'],
            'window_size': 1024,
            'cross_file_links': True
        },
        'shallow_context': {
            'extensions': ['.md', '.txt', '.json', '.yaml', '.yml'],
            'window_size': 512,
            'cross_file_links': False
        }
    }

    # Security parameters that enforce which AI model versions can be used
    SECURITY_PARAMS = {
        'model_whitelist': ['Tabnine-Prod-2025', 'Copilot-Enterprise', 'Codeium-Legacy', 'Cody-Enterprise'],
        'license_checks': {
            'validate_spdx': True,
            'allowed_licenses': ['Apache-2.0', 'MIT', 'BSD-3-Clause']
        }
    }

    @classmethod
    def get_language_policy(cls, file_extension: str) -> Dict[str, Any]:
        """
        Get the AI tool policy for a specific file extension

        Args:
            file_extension: The file extension (e.g., '.py', '.js')

        Returns:
            Dictionary with the tool priority configuration for the language
        """
        # Map file extensions to language keys
        extension_to_language = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.java': 'java',
            # Add more mappings as needed
        }

        language = extension_to_language.get(file_extension, 'default')
        return cls.TOOL_PRIORITY.get(language, cls.TOOL_PRIORITY['default'])

    @classmethod
    def get_context_rules(cls, file_extension: str) -> Dict[str, Any]:
        """
        Get the context rules for a specific file extension

        Args:
            file_extension: The file extension (e.g., '.py', '.js')

        Returns:
            Dictionary with context rules for the file type
        """
        for rule_type, rule in cls.CONTEXT_RULES.items():
            if file_extension in rule['extensions']:
                return rule

        # Default to shallow context if no match
        return cls.CONTEXT_RULES['shallow_context']

    # If we detect a particular environment, we might adapt the config
    @classmethod
    def dynamic_env_overrides(cls, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply environment-specific overrides to the configuration

        Args:
            config_data: The base configuration data

        Returns:
            Updated configuration with environment-specific overrides
        """
        cloud_env = os.getenv("CLOUD_ENV", "").lower()
        if cloud_env == "azure":
            # Possibly switch primary/fallback for certain languages in Azure
            # or enable Azure-specific models
            config_data['azureOptimized'] = True
        elif cloud_env == "gcp":
            config_data['gcpOptimized'] = True

        # Cherry-specific environment variables
        if os.getenv("CHERRY_AI_DISABLE_ALL", "").lower() == "true":
            config_data['disableAllAITools'] = True

        return config_data


def load_context_config(path=".aicfg"):
    """
    Load semantic context configuration from .aicfg file

    Args:
        path: Path to the .aicfg file

    Returns:
        Dictionary with context configuration
    """
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return data.get('context', {})
    except Exception as e:
        logger.warning(f"Failed to load context config from {path}: {e}")
        return {}


def tool_router(file_meta, rules=None):
    """
    AI tool selection based on file characteristics.

    Args:
        file_meta: dict with at least {'path': '...', 'language': 'python' etc.}
        rules: optional override for multi-tool routing

    Returns:
        Dictionary with selected tools and context mode
    """
    default_rules = {
        'test_files': {
            'pattern': '*_test.py',
            'tools': ['pytest-copilot', 'Tabnine-TDD'],
            'context': 'isolated'
        },
        'legacy_code': {
            'path_glob': '/legacy/**',
            'tools': ['Codeium-Legacy'],
            'context': 'strict'
        }
    }
    if rules is None:
        rules = default_rules

    for rule_name, r in rules.items():
        pattern_match = r.get('pattern') and fnmatch(file_meta['path'], r['pattern'])
        path_match = r.get('path_glob') and fnmatch(file_meta['path'], r['path_glob'])
        if pattern_match or path_match:
            return r

    # If no rule matched, fall back to global language-based priority
    lang = file_meta.get('language', 'python')
    pri = AIConfigPolicy.TOOL_PRIORITY.get(lang, {})
    return {
        'tools': [pri.get('primary')],
        'disabled': pri.get('disabled', []),
        'context': 'default'
    }
class AIToolManager:
    """
    Responsible for generating IDE configurations from the global policy.
    """

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the AI Tool Manager

        Args:
            project_root: The root directory of the project
        """
        self.project_root = project_root or os.getcwd()
        self.context_config = self._load_context_config()
        self.routing_rules = self._load_routing_rules()

    def _load_context_config(self) -> Dict[str, Any]:
        """
        Load semantic context configuration from .aicfg file

        Returns:
            Dictionary with context configuration
        """
        config_path = Path(self.project_root) / ".aicfg"
        default_config = {
            "context": {
                "depth": 3,
                "file_weights": {
                    ".py": 0.85,
                    ".ts": 0.75,
                    ".java": 0.8,
                    ".md": 0.25
                },
                "dynamic_adjustment": {
                    "enabled": True,
                    "cpu_threshold": "60%",
                    "memory_threshold": "4GB"
                }
            }
        }

        if not config_path.exists():
            # Create default config file
            with open(config_path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
            return default_config
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load .aicfg: {e}. Using default configuration.")
            return default_config

    def _load_routing_rules(self) -> Dict[str, Any]:
        """
        Load tool routing rules from configuration

        Returns:
            Dictionary with routing rules
        """
        rules_path = Path(self.project_root) / ".ai-routing.yaml"
        default_rules = {
            'test_files': {
                'pattern': '*_test.py',
                'tools': ['pytest-copilot', 'Tabnine-TDD'],
                'context': 'isolated'
            },
            'legacy_code': {
                'path_glob': '/legacy/**',
                'tools': ['Codeium-Legacy'],
                'context': 'strict'
            }
        }

        if not rules_path.exists():
            return default_rules

        try:
            with open(rules_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load .ai-routing.yaml: {e}. Using default rules.")
            return default_rules

    def get_tool_for_file(self, file_path: str, language: str = None) -> Dict[str, Any]:
        """
        Determine which AI tool should be used for a specific file

        Args:
            file_path: Path to the file
            language: Optional language override

        Returns:
            Dictionary with tool selection information
        """
        file_meta = {
            'path': file_path,
            'language': language or self._detect_language(file_path)
        }
        return tool_router(file_meta, self.routing_rules)

    def _detect_language(self, file_path: str) -> str:
        """
        Detect the programming language from a file path

        Args:
            file_path: Path to the file

        Returns:
            Detected language name
        """
        ext = os.path.splitext(file_path)[1].lower()
        extension_to_language = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cs': 'csharp',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.sh': 'shell',
            '.md': 'markdown',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
        }
        return extension_to_language.get(ext, 'unknown')

    def apply_config(self) -> bool:
        """
        Apply the AI configuration to all supported tools in the project

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate and apply configs for each supported IDE/tool
            self._apply_vscode_config()
            self._apply_tabnine_config()
            self._apply_codeium_config()
            self._apply_copilot_config()
            self._apply_cody_config()

            logger.info("Successfully applied AI tool configurations")
        Build a dictionary representing the recommended settings and extensions
        for VS Code based on the AI policy.

        Returns:
            Dictionary with VS Code settings and extension recommendations
        """
        settings = {}
        recommendations = []

        for lang, tools in AIConfigPolicy.TOOL_PRIORITY.items():
            primary_tool = tools['primary']
            # You might also process fallback_tool = tools.get('fallback')
            # or handle disabled tools.

            # Example: enforce Tabnine settings
            if primary_tool == 'Tabnine':
                settings.update({
                    "tabnine.experimentalAutoImports": True,
                    "tabnine.disable_line_of_code_comments": True,
                    # Disabling branding or watermarks:
                    "tabnine.hideBranding": True
                })
                recommendations.append("TabNine.tabnine-vscode")
