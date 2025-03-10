#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os


def main():
    parser = argparse.ArgumentParser(
        description="Repository maintenance tools")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Schema validation command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate GitHub configuration files")

    # Health check command
    health_parser = subparsers.add_parser(
        "health", help="Check repository health")

    # Workflows command
    workflow_parser = subparsers.add_parser(
        "workflows", help="Analyze GitHub workflows")

    # NPM setup command
    npm_parser = subparsers.add_parser("npm", help="Set up NPM configuration")

    args = parser.parse_args()

    if args.command == "validate":
        run_script("github_schema_validator.py")
    elif args.command == "health":
        run_script("repo_health_checker.py")
    elif args.command == "workflows":
        run_script("workflow_analyzer.py")
    elif args.command == "npm":
        run_script("npm_config_helper.py")
    else:
        parser.print_help()
        sys.exit(1)


def run_script(script_name):
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    if os.path.exists(script_path):
        subprocess.run([sys.executable, script_path])
    else:
        print(f"Error: Script {script_name} not found")
        sys.exit(1)


if __name__ == "__main__":
    main()
