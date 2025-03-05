#!/usr/bin/env python3

import json
import os
import subprocess
import sys

def load_config():
    """Load the benchmark configuration from the JSON file."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "benchmarks", "benchmark_config.json")
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get('security_scanning', {}).get('checkov', {})
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return {}

def install_checkov(version="latest"):
    """Install the specified version of Checkov."""
    try:
        if version == "latest":
            subprocess.check_call([sys.executable, "-m", "pip", "install", "checkov"])
        else:
            subprocess.check_call([sys.executable, "-m", "pip", "install", f"checkov=={version}"])
        print(f"Successfully installed Checkov {version}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Checkov: {e}")
        sys.exit(1)

def run_checkov(config):
    """Run Checkov with the configuration parameters."""
    if not config.get('enabled', False):
        print("Checkov is disabled in configuration. Exiting.")
        return
    
    # Prepare the command
    cmd = ["checkov"]
    
    # Add frameworks
    frameworks = config.get('frameworks', [])
    if frameworks:
        for framework in frameworks:
            cmd.extend(["-f", framework])
    
    # Add skip checks
    skip_checks = config.get('skip_checks', [])
    if skip_checks:
        cmd.extend(["--skip-check", ",".join(skip_checks)])
    
    # Add output formats
    output_formats = config.get('output_formats', [])
    output_dir = config.get('output_directory', './reports/checkov')
    os.makedirs(output_dir, exist_ok=True)
    
    for output_format in output_formats:
        if output_format == 'cli':
            continue  # CLI output is default
        elif output_format == 'json':
            cmd.extend(["--output", "json", "--output-file", f"{output_dir}/results.json"])
        elif output_format == 'junitxml':
            cmd.extend(["--output", "junitxml", "--output-file", f"{output_dir}/results.xml"])
    
    # Add baseline if it exists
    baseline = config.get('baseline')
    if baseline and os.path.exists(baseline):
        cmd.extend(["--baseline", baseline])
    
    # Set soft fail option
    if config.get('soft_fail', False):
        cmd.append("--soft-fail")
    
    # Run in current directory
    cmd.extend(["-d", "."])
    
    print(f"Running Checkov with command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=not config.get('soft_fail', False))
        print("Checkov scan completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Checkov scan failed with exit code {e.returncode}")
        if not config.get('soft_fail', False):
            sys.exit(e.returncode)

if __name__ == "__main__":
    config = load_config()
    if not config:
        print("No Checkov configuration found. Using defaults.")
        config = {"enabled": True, "version": "latest"}
    
    install_checkov(config.get('version', 'latest'))
    run_checkov(config)
