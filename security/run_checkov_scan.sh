#!/bin/bash

# Set variables
REPORT_DIR="/workspaces/cherry/security/reports"
REPORT_FILE="${REPORT_DIR}/checkov-report-$(date +%Y-%m-%d-%H%M%S).json"
LOG_FILE="${REPORT_DIR}/checkov-scan.log"

# Create reports directory if it doesn't exist
mkdir -p ${REPORT_DIR}

echo "Starting Checkov scan at $(date)" | tee -a ${LOG_FILE}

# Run Checkov scan
checkov \
  --directory /workspaces/cherry \
  --output cli json \
  --soft-fail \
  --output-file-path ${REPORT_FILE} \
  --framework all \
  2>&1 | tee -a ${LOG_FILE}

# Return code indicates if there were any failures
EXIT_CODE=$?

echo "Scan completed at $(date) with exit code ${EXIT_CODE}" | tee -a ${LOG_FILE}
echo "Report saved to ${REPORT_FILE}" | tee -a ${LOG_FILE}

# Find critical issues
CRITICAL_ISSUES=$(cat ${REPORT_FILE} | grep -c '"severity": "CRITICAL"')
echo "Found ${CRITICAL_ISSUES} critical issues" | tee -a ${LOG_FILE}

exit ${EXIT_CODE}
