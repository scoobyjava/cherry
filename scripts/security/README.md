# Security Scanning Tools

This directory contains security scanning tools for the project.

## Dependency Scanner

The dependency scanner checks project dependencies for known security vulnerabilities.

### Usage

Run the following command to scan all project dependencies:

```bash
node scripts/security/run_dependency_scan.js
```

### Configuration

The scanner is configured in `benchmarks/benchmark_config.json` under the `security_scanning.dependency_scan` section:

```json
"dependency_scan": {
  "enabled": true,
  "outputDir": "./reports/dependency-scan",
  "outputFormat": "json",
  "severityThreshold": "moderate",
  "ignoreDevDependencies": false,
  "failOnVulnerabilities": true,
  "exclusions": [
    "CWE-1234",
    "GHSA-abcd-efgh-ijkl"
  ]
}
```

### Options

- `enabled`: Enable/disable dependency scanning
- `outputDir`: Directory for scan reports
- `outputFormat`: Format for scan reports (json, cli)
- `severityThreshold`: Minimum severity to report (info, low, moderate, high, critical)
- `ignoreDevDependencies`: Whether to ignore dev dependencies
- `failOnVulnerabilities`: Exit with non-zero code if vulnerabilities are found
- `exclusions`: List of vulnerability IDs to ignore

### Requirements

For Node.js dependencies:
- Node.js must be installed
- npm must be available in PATH

For Python dependencies:
- Python must be installed
- safety package must be installed (`pip install safety`)

## Running Scheduled Scans

You can set up a scheduled scan by adding a cron job or setting up a CI/CD pipeline.
