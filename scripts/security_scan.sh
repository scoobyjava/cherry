#!/bin/bash

set -e

# Load configuration from benchmark_config.json
CONFIG_FILE="/workspaces/cherry/benchmarks/benchmark_config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file not found at $CONFIG_FILE"
    exit 1
fi

# Extract Checkov configuration using jq
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed. Please install jq."
    exit 1
fi

CHECKOV_ENABLED=$(jq -r '.security_scanning.checkov.enabled // "false"' "$CONFIG_FILE")
CHECKOV_VERSION=$(jq -r '.security_scanning.checkov.version // "latest"' "$CONFIG_FILE")
SKIP_CHECKS=$(jq -r '.security_scanning.checkov.skip_checks | join(",") // ""' "$CONFIG_FILE")
FRAMEWORKS=$(jq -r '.security_scanning.checkov.frameworks | join(",") // ""' "$CONFIG_FILE")
OUTPUT_FORMATS=$(jq -r '.security_scanning.checkov.output_formats | join(",") // ""' "$CONFIG_FILE")
OUTPUT_DIR=$(jq -r '.security_scanning.checkov.output_directory // "./reports/checkov"' "$CONFIG_FILE")
SOFT_FAIL=$(jq -r '.security_scanning.checkov.soft_fail // "false"' "$CONFIG_FILE")
BASELINE=$(jq -r '.security_scanning.checkov.baseline // ""' "$CONFIG_FILE")

# Check if Checkov is enabled
if [ "$CHECKOV_ENABLED" != "true" ]; then
    echo "Checkov scanning is disabled in configuration."
    exit 0
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Build Checkov command
CHECKOV_CMD="checkov -d /workspaces/cherry/infrastructure"

# Add optional parameters
if [ -n "$SKIP_CHECKS" ]; then
    CHECKOV_CMD="$CHECKOV_CMD --skip-check $SKIP_CHECKS"
fi

if [ -n "$FRAMEWORKS" ]; then
    CHECKOV_CMD="$CHECKOV_CMD --framework $FRAMEWORKS"
fi

if [ -n "$OUTPUT_FORMATS" ]; then
    for format in $(echo "$OUTPUT_FORMATS" | tr ',' ' '); do
        CHECKOV_CMD="$CHECKOV_CMD --output $format"
    done
fi

if [ -n "$OUTPUT_DIR" ]; then
    CHECKOV_CMD="$CHECKOV_CMD --output-path $OUTPUT_DIR"
fi

if [ "$SOFT_FAIL" == "true" ]; then
    CHECKOV_CMD="$CHECKOV_CMD --soft-fail"
fi

if [ -n "$BASELINE" ] && [ -f "$BASELINE" ]; then
    CHECKOV_CMD="$CHECKOV_CMD --baseline $BASELINE"
fi

# Run Checkov
echo "Running Checkov with command: $CHECKOV_CMD"
eval "$CHECKOV_CMD"

EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "Checkov found security issues. Check the report in $OUTPUT_DIR for details."
    if [ "$SOFT_FAIL" != "true" ]; then
        exit $EXIT_CODE
    fi
else
    echo "Checkov security scan completed successfully. No issues found."
fi
