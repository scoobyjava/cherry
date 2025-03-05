# Security Scanning with Checkov

This directory contains tools and configurations for security scanning using Checkov.

## Overview

Checkov is a static code analysis tool for infrastructure-as-code. It scans cloud infrastructure provisioned using Terraform, Cloudformation, Kubernetes, Dockerfile, Helm, or ARM Templates and detects security and compliance misconfigurations.

## Usage

### One-time Run

To install Checkov and run a scan:

```bash
python3 security/run_checkov.py
```

### Configuration

The script uses the configuration from `benchmarks/benchmark_config.json` under the `security_scanning.checkov` section. You can modify these settings:

- `enabled`: Enable/disable Checkov scanning
- `version`: Checkov version to install (use "latest" for the most recent version)
- `skip_checks`: Array of check IDs to skip during scanning
- `frameworks`: Frameworks to scan (terraform, cloudformation, kubernetes, etc.)
- `output_formats`: Output formats to generate (cli, json, junitxml)
- `output_directory`: Directory to store reports
- `soft_fail`: If true, script won't exit with error code on violations
- `baseline`: Path to baseline file for compare mode

### Baseline

To create a baseline file:

```bash
checkov -d . -o json --output-file security/checkov_baseline.json
```

This baseline can be referenced in the configuration to track only new issues.

## Integration

This script can be integrated into CI/CD pipelines by adding it as a step in your workflow.

