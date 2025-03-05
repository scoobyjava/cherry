#!/bin/bash

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo "Checking security scanning tool versions..."

# Check if Checkov is installed
if command -v checkov &> /dev/null; then
    INSTALLED_VERSION=$(checkov --version | cut -d ' ' -f 2)
    echo -e "${GREEN}✓ Checkov is installed: version ${INSTALLED_VERSION}${NC}"
    
    # Extract expected version from benchmark config
    CONFIG_FILE="/workspaces/cherry/benchmarks/benchmark_config.json"
    if [ -f "$CONFIG_FILE" ]; then
        EXPECTED_VERSION=$(grep -o '"version": "[^"]*"' "$CONFIG_FILE" | cut -d '"' -f 4)
        if [ "$EXPECTED_VERSION" = "latest" ]; then
            echo -e "${YELLOW}ℹ Config specifies 'latest' version - no version check needed${NC}"
        elif [ "$INSTALLED_VERSION" = "$EXPECTED_VERSION" ]; then
            echo -e "${GREEN}✓ Installed version matches config (${EXPECTED_VERSION})${NC}"
        else
            echo -e "${YELLOW}⚠ Warning: Installed version (${INSTALLED_VERSION}) differs from config (${EXPECTED_VERSION})${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Could not find config file at ${CONFIG_FILE}${NC}"
    fi
else
    echo -e "${RED}✗ Checkov is not installed${NC}"
    echo "To install Checkov, run: pip install checkov"
    exit 1
fi

echo "Security tool version check complete."
