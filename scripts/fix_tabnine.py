#!/usr/bin/env python3
import os
import json
import shutil
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def find_tabnine_directories():
    """Find all possible Tabnine configuration directories"""
    possible_dirs = [
        Path.home() / ".tabnine",
        Path.home() / ".config" / "TabNine",
        Path.home() / "Library" / "Preferences" / "TabNine",  # macOS
        Path.home() / "AppData" / "Roaming" / "TabNine",      # Windows
        Path.cwd() / ".tabnine",
        Path("/workspaces/cherry/.tabnine")
    ]

    found_dirs = [d for d in possible_dirs if d.exists()]
    logger.info(f"Found Tabnine directories: {found_dirs}")
    return found_dirs


def backup_config(config_path):
    """Create a backup of the existing config file"""
    if config_path.exists():
        backup_path = config_path.with_suffix('.json.bak')
        shutil.copy(config_path, backup_path)
        logger.info(f"Created backup at {backup_path}")


def write_config(config_path, config):
    """Write configuration to file"""
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Updated configuration at {config_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to write configuration: {e}")
        return False


def fix_tabnine_config():
    """Fix Tabnine configuration in all possible locations"""
    tabnine_dirs = find_tabnine_directories()

    # Create directories if they don't exist
    if not tabnine_dirs:
        new_dir = Path.home() / ".tabnine"
        new_dir.mkdir(exist_ok=True)
        tabnine_dirs = [new_dir]
        logger.info(f"Created new Tabnine directory: {new_dir}")

    # Configuration to disable watermarks and snippets
    config = {
        "disable_watermark": True,
        "disable_branding": True,
        "disable_suggestions_headers": True,
        "suggestion_mode": "full_file",
        "inline_suggestions": False,
        "snippet_mode": "disabled",
        "disable_line_suggestions": True,
        "disable_snippet_suggestions": True,
        "disable_auto_import": True,
        "disable_telemetry": True
    }

    # Update config in all locations
    success = False
    for directory in tabnine_dirs:
        config_path = directory / "config.json"
        backup_config(config_path)
        if write_config(config_path, config):
            success = True

    # Also create in project directory
    project_config_dir = Path("/workspaces/cherry/.tabnine")
    project_config_dir.mkdir(exist_ok=True)
    project_config_path = project_config_dir / "config.json"
    backup_config(project_config_path)
    write_config(project_config_path, config)

    return success


def restart_tabnine():
    """Attempt to restart Tabnine service"""
    try:
        # Try to find Tabnine process
        logger.info("Attempting to restart Tabnine...")

        # On Unix-like systems
        try:
            subprocess.run(["pkill", "-f", "TabNine"], check=False)
            logger.info("Killed Tabnine processes")
        except Exception:
            pass

        # For VS Code, we can't directly restart the extension, so inform the user
        logger.info("Please restart VS Code to apply the changes to Tabnine")

        return True
    except Exception as e:
        logger.error(f"Failed to restart Tabnine: {e}")
        return False


def main():
    logger.info("Starting Tabnine configuration fix...")

    if fix_tabnine_config():
        logger.info("Successfully updated Tabnine configuration")
    else:
        logger.error("Failed to update Tabnine configuration")

    if restart_tabnine():
        logger.info("Tabnine restart initiated")

    logger.info("Please restart your editor for changes to take effect")
    logger.info(
        "If issues persist, consider uninstalling and reinstalling the Tabnine extension")


if __name__ == "__main__":
    main()
